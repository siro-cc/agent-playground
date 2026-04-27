from typing import Dict, Optional, Union

from fastapi import FastAPI

from app.agent import run_agent, run_agent_flow
from app.config import get_settings
from app.schemas import ChatRequest, ChatResponse


settings = get_settings()


app = FastAPI(title=settings.app_name, debug=settings.app_debug)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": f"Hello from {settings.app_name}",
        "environment": settings.app_env,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "up"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {
        "status": "up",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return run_agent(request.question)
    except Exception as exc:
        return ChatResponse(
            question=request.question,
            tool_used=None,
            tool_result=None,
            final_answer=None,
            error=str(exc),
        )


@app.post("/flow")
def flow(request:ChatRequest)->Dict:
    state= run_agent_flow(request.question)
    return state.model_dump()