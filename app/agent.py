import json
from typing import Any, Callable, Dict

from openai import OpenAI

from app.config import get_settings
from app.logger import get_logger
from app.prompts import SYSTEM_PROMPT
from app.schemas import ChatResponse
from app.tools import get_cluster_status, search_runbook


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
]

TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
    "get_cluster_status": get_cluster_status,
    "search_runbook": search_runbook,
}


def _get_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


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
    tool_calls = [
        item
        for item in first_response.output
        if getattr(item, "type", None) == "function_call"
    ]

    if not tool_calls:
        logger.info("模型未调用工具,直接返回答案")
        return ChatResponse(
            question=question,
            tool_used=None,
            tool_result=None,
            final_answer=first_response.output_text or "当前没有生成可用回答",
            error=None,
        )
    tool_call = tool_calls[0]
    tool_name = tool_call.name
    tool_args = json.loads(tool_call.arguments)

    logger.info("模型决定调用工具:%s", tool_name)
    logger.info("工具参数:%s", tool_args)

    tool_result = _execute_tool(tool_name, tool_args)
    logger.info(f"工具返回:{tool_result}")

    input_items.append(
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(tool_result, ensure_ascii=False),
        }
    )

    second_response = client.responses.create(
        model=settings.model_name,
        previous_response_id=first_response.id,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(tool_result, ensure_ascii=False),
            }
        ],
        tools=TOOLS,
        parallel_tool_calls=False,
    )

    final_answer = second_response.output_text or "工具已执行，但模型未生成最终说明"

    logger.info("最终回答:%s", final_answer)
    return ChatResponse(
        question=question,
        tool_used=tool_name,
        tool_result=tool_result,
        final_answer=final_answer,
        error=None,
    )
