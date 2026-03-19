"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from webui.routes import (
    dashboard_router,
    config_router,
    rules_router,
    api_router,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Clash Config Manager",
    description="WebUI for managing Clash DNS configuration",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(dashboard_router)
app.include_router(config_router)
app.include_router(rules_router)
app.include_router(api_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("webui.main:app", host="0.0.0.0", port=8000, reload=True)
