from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    question: str
    current_stage: str = "start"

    intent: Optional[str] = None
    tool_used: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    tool_result: Optional[dict[str, Any]] = None

    final_answer: Optional[str] = None
    next_action: Optional[str] = None
    error: Optional[str] = None

    history: list[str] = Field(default_factory=list)
