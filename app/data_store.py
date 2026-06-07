import json
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


def load_data() -> dict[str, Any]:
    data_file = get_settings().data_file
    logger.debug("Loading data from %s", data_file)
    try:
        with data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        logger.error("Data file not found: %s", data_file)
        raise
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in data file %s: %s", data_file, exc)
        raise
    return dict(raw)


def get_value(key: str) -> Any:
    return load_data().get(key)
