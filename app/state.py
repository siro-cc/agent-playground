from typing import Any, Dict, Optional

from pydantic import BaseModel


class AgentState(BaseModel):
    question: str
    intent: Optional[str] = None
    tool_used: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None
    next_action: Optional[str] = None
    error: Optional[str] = None

