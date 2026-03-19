"""Templating configuration."""

from datetime import datetime
from pathlib import Path
from fastapi.templating import Jinja2Templates


def format_datetime(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
    return value


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.filters["date"] = format_datetime
