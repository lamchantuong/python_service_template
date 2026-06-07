import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.data_store import get_value

logger = logging.getLogger(__name__)

app = FastAPI(title="Python Service")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: process is up. Does not check dependencies."""
    return {"status": "ok"}


@app.get("/api/get/{key}")
def api_get_value(key: str):
    value = get_value(key)
    if value is None:
        logger.debug("API key not found: %s", key)
        return JSONResponse(status_code=404, content={"key": key, "error": "not found"})
    return {"key": key, "value": value}


@app.get("/")
def web_home(request: Request, key: str | None = None):
    value = get_value(key) if key else None
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"key": key, "value": value},
    )
