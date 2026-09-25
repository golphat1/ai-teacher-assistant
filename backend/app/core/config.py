from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

ai_provider: str = "anthropic"
anthropic_api_key: str | None = None
anthropic_model: str = "claude-sonnet-4-6"
openai_api_key: str | None = None
openai_model: str = "gpt-4o"
ai_max_retries: int = 2
use_mock_ai: bool = True  # flip to false once real keys are set

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.teacher",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    app_name: str = "AI Teacher Assistant"
    environment: str = "development"
    debug: bool = False

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()