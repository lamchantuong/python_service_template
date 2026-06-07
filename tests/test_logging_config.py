from pathlib import Path

from app.logging_config import build_uvicorn_log_config, normalize_log_level


def test_normalize_log_level_defaults_invalid_to_info() -> None:
    assert normalize_log_level("INFO") == "info"
    assert normalize_log_level("unknown") == "info"


def test_build_uvicorn_log_config_registers_app_logger() -> None:
    config = build_uvicorn_log_config("debug")
    loggers = config["loggers"]
    assert isinstance(loggers, dict)
    assert loggers["app"]["level"] == "DEBUG"
    assert loggers["uvicorn"]["level"] == "DEBUG"


def test_build_uvicorn_log_config_adds_file_handler(tmp_path: Path) -> None:
    log_file = tmp_path / "nested" / "app.log"
    config = build_uvicorn_log_config("info", log_file)
    handlers = config["handlers"]
    assert isinstance(handlers, dict)
    assert handlers["file"]["filename"] == str(log_file)
    assert handlers["file"]["formatter"] == "file_default"
    assert handlers["access_file"]["formatter"] == "file_access"
    assert log_file.parent.exists()


def test_build_uvicorn_log_config_file_formatters_have_timestamp(tmp_path: Path) -> None:
    config = build_uvicorn_log_config("info", tmp_path / "app.log")
    formatters = config["formatters"]
    assert isinstance(formatters, dict)
    assert formatters["file_default"]["use_colors"] is False
    assert "%(asctime)s" in formatters["file_default"]["fmt"]
    assert formatters["file_access"]["use_colors"] is False
    assert "%(asctime)s" in formatters["file_access"]["fmt"]
