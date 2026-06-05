import subprocess
import sys

import typer
import uvicorn

from app.config import BASE_DIR, get_settings
from app.data_store import get_value

cli = typer.Typer(help="Simple Python service CLI")
daemon = typer.Typer(help="Background daemon commands")
cli.add_typer(daemon, name="daemon")
PID_FILE = BASE_DIR / ".daemon.pid"


@cli.command("get")
def get_command(key: str):
    value = get_value(key)
    if value is None:
        typer.echo(f"{key} -> not found")
        raise typer.Exit(code=1)
    typer.echo(f"{key} -> {value}")


@cli.command("serve")
def serve_command(
    host: str | None = typer.Option(None, "--host", "-h", help="Bind host (env: HOST)"),
    port: int | None = typer.Option(None, "--port", "-p", help="Bind port (env: PORT)"),
    reload: bool | None = typer.Option(
        None, "--reload/--no-reload", help="Auto-reload on code changes (env: RELOAD)"
    ),
):
    settings = get_settings()
    uvicorn.run(
        "app.api:app",
        host=host if host is not None else settings.host,
        port=port if port is not None else settings.port,
        reload=reload if reload is not None else settings.reload,
    )


def _read_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def _is_running(pid: int) -> bool:
    check = subprocess.run(  # noqa: S603
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode != 0:
        return False
    output = check.stdout.strip()
    return bool(output) and "No tasks are running" not in output


@daemon.command("start")
def daemon_start(
    host: str | None = typer.Option(None, "--host", "-h", help="Bind host (env: HOST)"),
    port: int | None = typer.Option(None, "--port", "-p", help="Bind port (env: PORT)"),
):
    # No --reload here: uvicorn reload spawns a watcher + worker, so the PID we
    # store would not match the process serving traffic and daemon stop could
    # leave orphan workers. Use `serve` (foreground, respects RELOAD) for dev.
    settings = get_settings()
    host = host if host is not None else settings.host
    port = port if port is not None else settings.port
    pid = _read_pid()
    if pid and _is_running(pid):
        typer.echo(f"daemon already running (pid={pid})")
        raise typer.Exit(code=0)

    if PID_FILE.exists():
        PID_FILE.unlink()

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.api:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    # Windows-only constants; getattr keeps mypy happy on Linux CI.
    creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
        subprocess, "CREATE_NEW_PROCESS_GROUP", 0
    )
    proc = subprocess.Popen(  # noqa: S603
        cmd,
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    typer.echo(f"daemon started (pid={proc.pid})")


@daemon.command("stop")
def daemon_stop():
    pid = _read_pid()
    if not pid:
        typer.echo("daemon is not running")
        raise typer.Exit(code=0)

    subprocess.run(  # noqa: S603
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    if PID_FILE.exists():
        PID_FILE.unlink()
    typer.echo(f"daemon stopped (pid={pid})")


@daemon.command("status")
def daemon_status():
    pid = _read_pid()
    if pid and _is_running(pid):
        typer.echo(f"daemon is running (pid={pid})")
        raise typer.Exit(code=0)

    if PID_FILE.exists():
        PID_FILE.unlink()
    typer.echo("daemon is not running")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
