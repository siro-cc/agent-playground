from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., description="用户输入的问题")


class FlowRequest(BaseModel):
    question: str
    approved: bool = False


class ChatResponse(BaseModel):
    question: str
    tool_used: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None
    error: Optional[str] = None
