from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Deploy Network"
    APP_ENV: str = "production"
    APP_PORT: int = 8050
    BASE_PATH: str = "/aideploy"
    SECRET_KEY: str = "production-secret-ai-deploy-network-token-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./ai_deploy_network.db"
    MAX_FOUNDING_BUILDERS: int = 500
    ADMIN_EMAIL: str = "admin@aideploynetwork.com"
    ADMIN_PASSWORD: str = "AdminSecure2026!"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
