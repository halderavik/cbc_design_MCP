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
        port (int): Port for HTTP server (Heroku).
        host (str): Host for HTTP server.
        mcp_server_mode (str): MCP server mode (stdio/http).
        mcp_log_level (str): MCP server logging level.
        max_respondents (int): Maximum number of respondents allowed.
        max_tasks_per_respondent (int): Maximum tasks per respondent.
        max_options_per_task (int): Maximum options per task.
        health_check_enabled (bool): Whether health checks are enabled.
        health_check_timeout (int): Health check timeout in seconds.
    """

    app_name: str = "conjoint-mcp-server"
    environment: Literal["dev", "prod", "test"] = "dev"
    log_level: str = "INFO"
    
    # Heroku Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    
    # MCP Server Configuration
    mcp_server_mode: str = "stdio"
    mcp_log_level: str = "WARNING"
    
    # Performance Configuration
    max_respondents: int = 2000
    max_tasks_per_respondent: int = 20
    max_options_per_task: int = 5
    
    # Health Check Configuration
    health_check_enabled: bool = True
    health_check_timeout: int = 30

    class Config:
        env_file = ".env"
        env_prefix = "APP_"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    """

    return Settings()


