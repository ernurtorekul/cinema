from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Mock Mode
    mock_mode: bool = False

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Gemini
    gemini_api_key: str

    # Audio APIs
    elevenlabs_api_key: str = ""
    suno_api_key: str = ""
    udio_api_key: str = ""

    # CORS
    frontend_url: str = "http://localhost:3000"

    class Config:
        # Find .env file in parent directory of app folder
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
