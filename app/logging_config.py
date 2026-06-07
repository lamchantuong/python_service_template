import copy
from pathlib import Path

from uvicorn.config import LOGGING_CONFIG

_VALID_LEVELS = frozenset({"critical", "error", "warning", "info", "debug", "trace"})


def normalize_log_level(level: str) -> str:
    normalized = level.strip().lower()
    if normalized not in _VALID_LEVELS:
        return "info"
    return normalized


def _logging_level(level: str) -> str:
    normalized = normalize_log_level(level)
    return "DEBUG" if normalized == "trace" else normalized.upper()


def build_uvicorn_log_config(
    log_level: str,
    log_file: Path | None = None,
) -> dict[str, object]:
    config: dict[str, object] = copy.deepcopy(LOGGING_CONFIG)
    level = _logging_level(log_level)

    loggers = config["loggers"]
    assert isinstance(loggers, dict)
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        if logger_name in loggers:
            entry = loggers[logger_name]
            assert isinstance(entry, dict)
            entry["level"] = level

    handlers = config["handlers"]
    assert isinstance(handlers, dict)
    formatters = config["formatters"]
    assert isinstance(formatters, dict)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        path = str(log_file)
        formatters["file_default"] = {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s %(levelprefix)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": False,
        }
        formatters["file_access"] = {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": (
                '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": False,
        }
        handlers["file"] = {
            "formatter": "file_default",
            "class": "logging.FileHandler",
            "filename": path,
            "encoding": "utf-8",
        }
        handlers["access_file"] = {
            "formatter": "file_access",
            "class": "logging.FileHandler",
            "filename": path,
            "encoding": "utf-8",
        }
        for logger_name, handler_key in (
            ("uvicorn", "file"),
            ("uvicorn.access", "access_file"),
        ):
            entry = loggers[logger_name]
            assert isinstance(entry, dict)
            existing = entry.get("handlers", [])
            assert isinstance(existing, list)
            entry["handlers"] = [*existing, handler_key]

    loggers["app"] = {
        "handlers": ["default", *([] if log_file is None else ["file"])],
        "level": level,
        "propagate": False,
    }

    return config
