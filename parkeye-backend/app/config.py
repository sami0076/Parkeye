"""Settings loaded from environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from .env."""

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str = ""
    DATABASE_URL: str
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    ENV: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
