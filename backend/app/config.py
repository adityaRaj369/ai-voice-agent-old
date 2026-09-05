import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    # Vercel serverless filesystem is read-only except /tmp
    if os.getenv("VERCEL"):
        return "sqlite:////tmp/frontline.db"
    return "sqlite:///./frontline.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    hunar_api_key: str = ""
    hunar_api_base: str = "https://api.voice.hunar.ai"
    public_base_url: str = "http://localhost:8000"
    pdl_api_key: str = ""
    apollo_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    frontend_origin: str = "http://localhost:3000"
    database_url: str = _default_database_url()


settings = Settings()
