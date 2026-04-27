from app.state import AgentState
from app.tools import (
    get_cluster_status,
    get_recent_changes,
    query_alerts,
    query_service_status,
    search_runbook,
)
import re


TOOL_REGISTRY = {
    "get_cluster_status": get_cluster_status,
    "search_runbook": search_runbook,
    "query_alerts": query_alerts,
    "get_recent_changes": get_recent_changes,
    "query_service_status": query_service_status,
}


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


def classify_intent_node(state: AgentState) -> AgentState:
    state.current_stage = "classify_intent"
    state.history.append(state.current_stage)
    state.intent = classify_intent(state.question)

    return state


def choose_tool_node(state: AgentState) -> AgentState:
    state.current_stage = "choose_tool"
    state.history.append(state.current_stage)
    state.tool_used = choose_tool_by_intent(state.intent)
    return state


def build_tool_args_node(state: AgentState) -> AgentState:
    state.current_stage = "build_tool_args"
    state.history.append(state.current_stage)

    if not state.tool_used:
        return state

    state.tool_args = build_tool_args(state.tool_used, state.question)
    return state


def execute_tool_node(state: AgentState) -> AgentState:
    state.current_stage = "execute_tool"
    state.history.append(state.current_stage)

    if not state.tool_used:
        return state

    try:
        tool = TOOL_REGISTRY[state.tool_used]
        state.tool_result = tool(**state.tool_args)
    except Exception as exc:
        state.error = f"工具执行失败:{str(exc)}"

    return state


def build_response_node(state: AgentState) -> AgentState:
    state.current_stage = "build_response"
    state.history.append(state.current_stage)

    if not state.tool_used:
        state.final_answer = (
            "目前信息不足,请补充集群名称 服务名称 故障现象或最近变更信息"
        )
        state.next_action = "补充更具体的问题背景"
        return state

    state.final_answer = build_final_answer(state)
    state.next_action = suggest_next_action(state)
    return state
