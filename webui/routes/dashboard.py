"""Dashboard routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from webui.services.yaml_service import YamlService
from webui.services.rule_service import RuleService

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="", tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page."""
    yaml_service = YamlService()
    rule_service = RuleService()

    config = yaml_service.get_config()
    rule_files = rule_service.list_rule_files()

    stats = {
        "proxy_groups": len(config.proxy_groups),
        "rule_providers": len(config.rule_providers),
        "rule_files": len(rule_files),
        "total_rules": sum(len(rf.rules) for rf in rule_files),
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "config": config,
            "stats": stats,
            "rule_files": rule_files,
        },
    )
