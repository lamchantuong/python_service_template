import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    data_file: Path
    reload: bool


@lru_cache
def get_settings() -> Settings:
    data_path = Path(os.getenv("DATA_FILE", "data.json"))
    data_file = data_path if data_path.is_absolute() else BASE_DIR / data_path
    return Settings(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        data_file=data_file,
        reload=_env_bool("RELOAD", True),
    )
