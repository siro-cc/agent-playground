from typing import Optional, Union

from fastapi import FastAPI

from app.config import get_settings


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


@app.post("/chat")
def chat() -> dict[str, str]:
    return {"message": "agent playground is running"}

