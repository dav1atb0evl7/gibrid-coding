from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    admin_telegram_ids: str = ""
    admin_api_token: str
    bot_mode: str = "polling"
    webhook_base_url: str = ""
    webhook_secret: str = ""
    app_env: str = "production"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def admin_ids(self) -> set[int]:
        return {int(value.strip()) for value in self.admin_telegram_ids.split(",") if value.strip()}

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @field_validator("bot_mode")
    @classmethod
    def validate_bot_mode(cls, value: str) -> str:
        if value not in {"polling", "webhook"}:
            raise ValueError("BOT_MODE must be polling or webhook")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
