from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Ipona"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://ipona:ipona_dev@localhost:5432/ipona"
    secret_key: str = "dev-only-secret-not-for-production-use-00000000"
    access_token_expire_minutes: int = 60 * 24
    auth_rate_limit: str = "5/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()
