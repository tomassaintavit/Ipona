from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Ipona"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://ipona:ipona_dev@localhost:5432/ipona"


@lru_cache
def get_settings() -> Settings:
    return Settings()
