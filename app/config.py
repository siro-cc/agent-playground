from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    app_name: str = "agent-playground"
    app_env: str = "development"
    app_debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "agent-playground"),
        app_env=os.getenv("APP_ENV", "development"),
        app_debug=os.getenv("APP_DEBUG", "false"),
    )
