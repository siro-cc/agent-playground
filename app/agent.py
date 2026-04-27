import json
import re
from typing import Any, Callable

from openai import OpenAI

from app.config import get_settings
from app.logger import get_logger
from app.prompts import SYSTEM_PROMPT
from app.schemas import ChatResponse
from app.state import AgentState
from app.tools import (
    get_cluster_status,
    get_recent_changes,
    query_alerts,
    query_service_status,
    search_runbook,
)


logger = get_logger(__name__)

TOOLS = [
    {
        "type": "function",
        "name": "get_cluster_status",
        "description": "查询指定集群的健康状态、节点数量和告警信息",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "cluster_name": {
                    "type": "string",
                    "description": "集群名称，例如 test-cluster 或 cluster-a",
                }
            },
            "required": ["cluster_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_runbook",
        "description": "根据故障关键词检索排障手册",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "故障关键词，例如 CrashLoopBackOff、服务启动失败、CPU高",
                }
            },
            "required": ["keyword"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "query_alerts",
        "description": "查询指定服务当前的告警信息",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "服务名称，例如 user-service 或 payment-service",
                }
            },
            "required": ["service_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_recent_changes",
        "description": "查询指定服务最近的发布或配置变更记录",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "服务名称，例如 user-service 或 payment-service",
                }
            },
            "required": ["service_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "query_service_status",
        "description": "查询指定服务当前运行状态、副本数和就绪情况",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "服务名称，例如 user-service 或 payment-service",
                }
            },
            "required": ["service_name"],
            "additionalProperties": False,
        },
    },
]

TOOL_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "get_cluster_status": get_cluster_status,
    "search_runbook": search_runbook,
    "query_alerts": query_alerts,
    "get_recent_changes": get_recent_changes,
    "query_service_status": query_service_status,
}


def _get_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def _extract_tool_calls(response: Any) -> list[Any]:
    output = getattr(response, "output", []) or []
    return [item for item in output if getattr(item, "type", None) == "function_call"]


def _execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    tool = TOOL_REGISTRY.get(name)
    if tool is None:
        raise ValueError(f"未知工具:{name}")

    return tool(**args)


def classify_intent(question: str) -> str:
    q = question.lower()

    if (
        "集群" in q
        or "节点" in q
        or "整体状态" in q
        or re.search(r"\bcluster[-a-z0-9]+\b", q)
    ):
        return "cluster_status"

    if "告警" in q:
        return "alerts"

    if (
        "变更" in q
        or "发布" in q
        or "发版" in q
        or "发过版" in q
        or "最近动过" in q
        or "最近改过" in q
    ):
        return "recent_changes"

    if (
        "crashloopbackoff" in q
        or "启动失败" in q
        or "cpu 高" in q
        or "cpu高" in q
        or "重启" in q
        or "排查" in q
        or "定位" in q
        or "分析" in q
    ):
        return "runbook"

    if "状态" in q or "副本" in q or "正常吗" in q or "健康吗" in q:
        return "service_status"

    return "unknown"


def run_agent(question: str) -> ChatResponse:
    question = (question or "").strip()
    if not question:
        return ChatResponse(
            question="",
            error="question不能为空",
        )

    client = _get_client()

    logger.info("收到问题:%s", question)
    input_items = [{"role": "user", "content": question}]
    settings = get_settings()
    logger.info(
        "当前模型=%s, base_url=%s", settings.model_name, settings.openai_base_url
    )
    first_response = client.responses.create(
        model=settings.model_name,
        instructions=SYSTEM_PROMPT,
        input=input_items,
        tools=TOOLS,
        parallel_tool_calls=False,
    )
    tool_calls = _extract_tool_calls(first_response)

    if not tool_calls:
        logger.info("模型未调用工具,直接返回答案")
        final_answer = first_response.output_text or "当前没有生成可用回答"

        if not final_answer.strip():
            final_answer = (
                "目前信息不足，请补充集群名称、服务名称、故障现象或最近变更信息"
            )

        return ChatResponse(
            question=question,
            tool_used=None,
            tool_result=None,
            final_answer=final_answer,
            error=None,
        )
    tool_call = tool_calls[0]
    tool_name = tool_call.name
    tool_args = json.loads(tool_call.arguments)
    if not isinstance(tool_args, dict):
        raise ValueError(f"工具参数解析失败:{tool_args}")
    logger.info("模型输出:%s", first_response.output_text)
    logger.info("模型输出:%s", first_response.output)
    logger.info("模型决定调用工具:%s", tool_name)
    logger.info("工具参数:%s", tool_args)

    try:
        tool_result = _execute_tool(tool_name, tool_args)
    except Exception as exc:
        logger.exception("工具执行失败")
        return ChatResponse(
            question=question,
            tool_used=tool_name,
            tool_result=None,
            final_answer=None,
            error=f"工具执行失败:{str(exc)}",
        )

    logger.info(f"工具返回:{tool_result}")

    input_items.append(
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(tool_result, ensure_ascii=False),
        }
    )

    second_input = list(first_response.output)
    second_input.append(
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(tool_result, ensure_ascii=False),
        }
    )

    try:
        second_response = client.responses.create(
            model=settings.model_name,
            instructions=SYSTEM_PROMPT,
            input=second_input,
            tools=TOOLS,
            parallel_tool_calls=False,
        )
    except Exception as exc:
        logger.exception("第二轮模型调用失败")
        return ChatResponse(
            question=question,
            tool_used=tool_name,
            tool_result=tool_result,
            final_answer=None,
            error=f"第二轮模型调用失败:{str(exc)}",
        )

    final_answer = second_response.output_text or "工具已执行，但模型未生成最终说明"

    logger.info("收到问题: %s", question)
    logger.info(
        "当前模型=%s, base_url=%s", settings.model_name, settings.openai_base_url
    )
    logger.info(
        "第一轮输出类型: %s", [getattr(i, "type", None) for i in first_response.output]
    )
    logger.info("模型决定调用工具: %s", tool_name)
    logger.info("工具参数: %s", tool_args)
    logger.info("工具返回: %s", tool_result)
    logger.info("最终回答: %s", final_answer)

    return ChatResponse(
        question=question,
        tool_used=tool_name,
        tool_result=tool_result,
        final_answer=final_answer,
        error=None,
    )


def choose_tool_by_intent(intent: str) -> str | None:
    mapping = {
        "cluster_status": "get_cluster_status",
        "alerts": "query_alerts",
        "recent_changes": "get_recent_changes",
        "service_status": "query_service_status",
        "runbook": "search_runbook",
    }
    return mapping.get(intent)


def extract_cluster_name(question: str) -> str | None:
    q = question.lower()

    match = re.search(r"\b(cluster[-a-z0-9]+)\b", q)
    if match:
        return match.group(1)

    if "test-cluster" in q:
        return "test-cluster"

    return None


def extract_service_name(question: str) -> str | None:
    q = question.lower()
    match = re.search(r"\b([a-z0-9-]+-service)\b", q)
    if match:
        return match.group(1)

    if "user-service" in q:
        return "user-service"
    if "payment-service" in q:
        return "payment-service"

    return None


def build_tool_args(tool_name: str, question: str) -> dict:
    if tool_name == "get_cluster_status":
        cluster_name = extract_cluster_name(question)
        if cluster_name:
            return {"cluster_name": cluster_name}
        return {"cluster_name": "test-cluster"}

    if tool_name in ["query_alerts", "get_recent_changes", "query_service_status"]:
        service_name = extract_service_name(question)
        if service_name:
            return {"service_name": service_name}
        return {"service_name": "user-service"}

    if tool_name == "search_runbook":
        return {"keyword": question}

    return {}


def run_agent_flow(question: str) -> AgentState:
    question = (question or "").strip()
    state = AgentState(question=question)
    if not question:
        state.error = "question 不能为空"
        return state

    intent = classify_intent(question=question)
    state.intent = intent
    tool_name = choose_tool_by_intent(intent=intent)
    if not tool_name:
        state.final_answer = (
            "目前信息不足，请补充集群名称、服务名称、故障现象或最近变更信息。"
        )
        state.next_action = "补充更具体的问题背景"
        return state

    state.tool_used = tool_name
    state.tool_args = build_tool_args(tool_name, question)

    try:
        state.tool_result = _execute_tool(tool_name, state.tool_args)
    except Exception as exc:
        state.error = f"工具执行失败:{str(exc)}"
        return state

    state.final_answer = build_final_answer(state)
    state.next_action = suggest_next_action(state)

    return state


def build_final_answer(state: AgentState) -> str:
    if state.error:
        return state.error

    if state.tool_used == "get_cluster_status":
        status = state.tool_result.get("status")
        warning = state.tool_result.get("warning") or "无明显告警"
        cluster_name = state.tool_result.get("cluster_name")
        return f"集群 {cluster_name} 当前状态为 {status}。依据：{warning}"

    if state.tool_used == "query_service_status":
        status = state.tool_result.get("status")
        replicas = state.tool_result.get("replicas")
        ready = state.tool_result.get("ready_replicas")
        service_name = state.tool_result.get("service_name")
        message = state.tool_result.get("message") or "无额外说明"
        return f"服务 {service_name} 当前状态为 {status}，就绪副本 {ready}/{replicas}。依据：{message}"

    if state.tool_used == "query_alerts":
        count = state.tool_result.get("count", 0)
        service_name = state.tool_result.get("service_name")
        return f"服务 {service_name} 当前共查询到 {count} 条告警。"

    if state.tool_used == "get_recent_changes":
        count = state.tool_result.get("count", 0)
        service_name = state.tool_result.get("service_name")
        return f"服务 {service_name} 最近共发现 {count} 条变更记录。"

    if state.tool_used == "search_runbook":
        matched = state.tool_result.get("matched")
        if matched:
            return "已找到相关排障手册，可按建议步骤继续排查。"
        return "未找到直接匹配的排障手册，建议补充更具体的故障现象。"

    return "暂时无法生成结论。"


def suggest_next_action(state: AgentState) -> str:
    if state.error:
        return "先修复错误后再继续"

    if state.tool_used == "get_cluster_status":
        if state.tool_result.get("status") == "healthy":
            return "继续观察,无需立即处理"

        return "优先检查异常节点 控制面或集群事件"

    if state.tool_used == "query_service_status":
        if state.tool_result.get("status") == "healthy":
            return "继续观察服务监控和告警"
        return "优先检查未就绪副本、Pod 事件和最近变更"

    if state.tool_used == "query_alerts":
        return "结合告警级别判断是否需要先止损或继续定位"

    if state.tool_used == "get_recent_changes":
        return "优先核对最近发布或配置改动是否与当前异常相关"

    if state.tool_used == "search_runbook":
        return "按手册步骤逐项排查，并补充日志、事件或监控信息"

    return "补充更多上下文"
