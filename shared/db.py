import sqlite3
from pathlib import Path

from shared.config import ensure_runtime_dirs, settings


def get_db_connection() -> sqlite3.Connection:
    ensure_runtime_dirs()
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def db_exists() -> bool:
    return Path(settings.sqlite_db_path).exists()
