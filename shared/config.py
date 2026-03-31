from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    sqlite_db_path: Path = Field(default=Path("data/orders.db"), alias="SQLITE_DB_PATH")
    audit_log_dir: Path = Field(default=Path("logs/audit"), alias="AUDIT_LOG_DIR")
    protocol_log_dir: Path = Field(default=Path("logs/protocol"), alias="PROTOCOL_LOG_DIR")
    internal_email_domain: str = Field(default="company.local", alias="INTERNAL_EMAIL_DOMAIN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()


def ensure_runtime_dirs() -> None:
    settings.audit_log_dir.mkdir(parents=True, exist_ok=True)
    settings.protocol_log_dir.mkdir(parents=True, exist_ok=True)
    settings.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)
