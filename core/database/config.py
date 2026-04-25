from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Origin API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./origin.db"

    # ID Generator lock timeout (seconds)
    ID_GEN_LOCK_TIMEOUT: float = 10.0

    # Audit log agent name
    DEFAULT_AGENT: str = "fuxi"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
