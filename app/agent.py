import json
from typing import Any, Callable, Dict, List

from openai import OpenAI

from app.config import get_settings
from app.logger import get_logger
from app.prompts import SYSTEM_PROMPT
from app.schemas import ChatResponse
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

TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
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

def _extract_tool_calls(response:Any)->List[Any]:
    output = getattr(response,"output",[]) or []
    return [
        item for item in output
        if getattr(item,"type",None)=="function_call"
    ]

def _execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    tool = TOOL_REGISTRY.get(name)
    if tool is None:
        raise ValueError(f"未知工具:{name}")

    return tool(**args)


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
            final_answer = "目前信息不足，请补充集群名称、服务名称、故障现象或最近变更信息"

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
