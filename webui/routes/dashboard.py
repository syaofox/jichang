"""Dashboard routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from webui.templates import templates
from webui.services.yaml_service import YamlService
from webui.services.rule_service import RuleService

router = APIRouter(prefix="", tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page."""
    yaml_service = YamlService()
    rule_service = RuleService()

    config = yaml_service.get_config()
    rule_files = rule_service.list_rule_files()
    configs = yaml_service.list_configs()
    active_config = yaml_service.get_active_config()

    stats = {
        "proxy_groups": len(config.proxy_groups),
        "rule_providers": len(config.rule_providers),
        "rule_files": len(rule_files),
        "total_rules": sum(len(rf.rules) for rf in rule_files),
        "config_files": len(configs),
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "config": config,
            "stats": stats,
            "rule_files": rule_files,
            "configs": configs,
            "active_config": active_config,
        },
    )
