from app.flow_nodes import (
    build_response_node,
    build_tool_args_node,
    choose_tool_node,
    classify_intent_node,
    execute_tool_node,
)
from app.state import AgentState


FLOW_NODES = [
    classify_intent_node,
    choose_tool_node,
    build_tool_args_node,
    execute_tool_node,
    build_response_node,
]


def run_flow_pipeline(question: str) -> AgentState:
    state = AgentState(question=(question or "").strip())

    if not state.question:
        state.error = "question不能为空"
        state.final_answer = None
        state.next_action = None
        return state

    for node in FLOW_NODES:
        state = node(state)
        if state.error:
            break

    return state
