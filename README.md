# python_service_template (CLI + Web + API)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Dependencies use compatible releases in `pyproject.toml` (`~=`, e.g. `fastapi~=0.136.0` allows `0.136.x` patches only) — fix releases without picking up new minors, no lockfile. Transitive deps still float; use a lockfile in your app if you need bit-for-bit installs.

Configuration (`.env` or environment variables):

| Variable   | Default       | Description              |
|------------|---------------|--------------------------|
| `HOST`     | `127.0.0.1`   | Server bind host         |
| `PORT`     | `8000`        | Server bind port         |
| `DATA_FILE`| `data.json`   | Path to JSON data file   |
| `RELOAD`   | `true`        | Uvicorn auto-reload      |

## Test & lint

```bash
pytest
ruff check .
ruff format --check .
mypy
pyright
```

## Pre-commit (check before every commit)

Config lives in `.pre-commit-config.yaml` (committed to git). After clone/setup, each developer runs **once**:

```bash
pip install -e ".[dev]"
pre-commit install
```

From then on, `git commit` automatically runs Ruff + Mypy (and basic file checks). To run manually on all files:

```bash
pre-commit run --all-files
```

CI also runs the same hooks so everyone stays aligned even if hooks are skipped locally.

## Run (foreground)

After `pip install -e .`, use the console script or `main.py`:

```bash
python-service serve
# or
python main.py serve
```

- Web UI: `http://127.0.0.1:8000/`
- API: `http://127.0.0.1:8000/api/get/hello`
- Liveness: `http://127.0.0.1:8000/healthz` (readiness `/readyz` is not included — add when you have real dependencies)

## Test CLI

```bash
python main.py get hello
python main.py get app_name
```

## Daemon (Windows)

`daemon start` does not enable uvicorn reload: reload uses a watcher process, so the stored PID would not match the server and `daemon stop` could miss child processes. Use `serve` for development with `RELOAD=true`.

```bash
python main.py daemon start
python main.py daemon status
python main.py daemon stop
```

## Test API quickly

```bash
curl http://127.0.0.1:8000/api/get/hello
```
