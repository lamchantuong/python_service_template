from app.config import get_settings


def test_get_settings_reads_logging_env(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("ACCESS_LOG", "false")
    monkeypatch.setenv("LOG_FILE", "custom.log")

    settings = get_settings()
    assert settings.log_level == "debug"
    assert settings.access_log is False
    assert settings.log_file == settings.data_file.parent / "custom.log"

    get_settings.cache_clear()


def test_get_settings_logging_defaults(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("ACCESS_LOG", raising=False)
    monkeypatch.delenv("LOG_FILE", raising=False)

    settings = get_settings()
    assert settings.log_level == "info"
    assert settings.access_log is True
    assert settings.log_file is None

    get_settings.cache_clear()
