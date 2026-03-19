"""Configuration files management routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from webui.templates import templates
from webui.services.yaml_service import YamlService

router = APIRouter(prefix="/configs", tags=["configs"])


@router.get("", response_class=HTMLResponse)
async def configs_page(request: Request):
    """Configuration files management page."""
    yaml_service = YamlService()
    configs = yaml_service.list_configs()
    active_config = yaml_service.get_active_config()

    return templates.TemplateResponse(
        "configs/index.html",
        {
            "request": request,
            "configs": configs,
            "active_config": active_config,
        },
    )
