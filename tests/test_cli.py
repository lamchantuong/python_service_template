from typer.testing import CliRunner

from app.cli import cli

runner = CliRunner()


def test_cli_get_existing_key() -> None:
    result = runner.invoke(cli, ["get", "hello"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "hello -> world"


def test_cli_get_missing_key() -> None:
    result = runner.invoke(cli, ["get", "__nonexistent_key__"])
    assert result.exit_code == 1
    assert result.stdout.strip() == "__nonexistent_key__ -> not found"
