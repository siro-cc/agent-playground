from functools import lru_cache
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    app_name: str = "agent-playground"
    app_env: str = "development"
    app_debug: bool = False
    openai_base_url:Optional[str]=None
    openai_api_key: Optional[str] = None
    model_name: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "agent-playground"),
        app_env=os.getenv("APP_ENV", "development"),
        app_debug=os.getenv("APP_DEBUG", "false"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name=os.getenv("MODEL_NAME", "gpt-4.1-mini"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    )

