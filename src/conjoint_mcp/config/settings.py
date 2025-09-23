from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        app_name (str): Application name.
        environment (Literal["dev", "prod", "test"]): Environment name.
        log_level (str): Logging level.
    """

    app_name: str = "conjoint-mcp-server"
    environment: Literal["dev", "prod", "test"] = "dev"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = "APP_"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    """

    return Settings()


