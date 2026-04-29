from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


class Settings(BaseSettings):
    app_name: str = "LosTeaApi"
    api_prefix: str = "/api"

    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-v4-pro", alias="DEEPSEEK_MODEL")

    temperature: float = Field(default=0.5, alias="LLM_TEMPERATURE")
    reasoning_effort: str = Field(default="", alias="LLM_REASONING_EFFORT")
    thinking_enabled: bool = Field(default=False, alias="LLM_THINKING_ENABLED")

    max_history: int = Field(default=10, alias="CHAT_MAX_HISTORY")
    max_history_chars: int = Field(default=2000, alias="CHAT_MAX_HISTORY_CHARS")
    max_message_chars: int = Field(default=4000, alias="CHAT_MAX_MESSAGE_CHARS")

    sqlite_database_url : str = Field(default="sqlite:///./app.db", alias="SQLITE_DATABASE_URL")

    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:5174,https://2932238802.github.io",
        alias="ALLOWED_ORIGINS",
    )

    prompt_path: Path = Field(
        default=PROJECT_ROOT / "prompt" / "system_prompt.md",
        alias="SYSTEM_PROMPT_PATH",
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
