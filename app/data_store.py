import json
from typing import Any

from app.config import get_settings


def load_data() -> dict[str, Any]:
    with get_settings().data_file.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return dict(raw)


def get_value(key: str) -> Any:
    return load_data().get(key)
