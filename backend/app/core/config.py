from typing import List, Optional
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_NAME: str = "Kynetic"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    CORS_ORIGINS: Optional[str] = None

    DATABASE_URL: str = "sqlite:///./kynetic_dev.db"

    SECRET_KEY: str = "insecure-development-secret-key-replace-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LLM_PROVIDER: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = "gemini-1.5-flash"

    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_DIR: str = "./uploads"

    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/integrations/github/callback"

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        origins = [self.FRONTEND_ORIGIN.strip()]
        if self.CORS_ORIGINS:
            for o in self.CORS_ORIGINS.split(","):
                o_clean = o.strip()
                if o_clean and o_clean not in origins:
                    origins.append(o_clean)
        # Always allow standard local dev origins in development
        if self.APP_ENV == "development":
            dev_defaults = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
            ]
            for d in dev_defaults:
                if d not in origins:
                    origins.append(d)
        return origins


settings = Settings()

