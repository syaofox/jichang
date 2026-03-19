"""Configuration routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from webui.templates import templates
from webui.services.yaml_service import YamlService

router = APIRouter(prefix="/config", tags=["config"])


@router.get("", response_class=HTMLResponse)
async def config_index(request: Request):
    """Configuration index page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    return templates.TemplateResponse(
        "config/index.html",
        {
            "request": request,
            "config": config,
        },
    )


@router.get("/dns", response_class=HTMLResponse)
async def config_dns(request: Request):
    """DNS configuration page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    return templates.TemplateResponse(
        "config/dns.html",
        {
            "request": request,
            "config": config,
        },
    )


@router.get("/tun", response_class=HTMLResponse)
async def config_tun(request: Request):
    """TUN configuration page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    return templates.TemplateResponse(
        "config/tun.html",
        {
            "request": request,
            "config": config,
        },
    )


@router.get("/proxy-groups", response_class=HTMLResponse)
async def config_proxy_groups(request: Request):
    """Proxy groups configuration page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    proxy_groups_json = [g.model_dump() for g in config.proxy_groups]

    return templates.TemplateResponse(
        "config/proxy_groups.html",
        {
            "request": request,
            "config": config,
            "proxy_groups_json": proxy_groups_json,
        },
    )


@router.get("/providers", response_class=HTMLResponse)
async def config_providers(request: Request):
    """Proxy providers configuration page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    return templates.TemplateResponse(
        "config/providers.html",
        {
            "request": request,
            "config": config,
        },
    )


@router.get("/rules", response_class=HTMLResponse)
async def config_rules(request: Request):
    """Rules configuration page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    return templates.TemplateResponse(
        "config/rules.html",
        {
            "request": request,
            "config": config,
        },
    )


@router.get("/sniffer", response_class=HTMLResponse)
async def config_sniffer(request: Request):
    """Sniffer configuration page."""
    yaml_service = YamlService()
    config = yaml_service.get_config()

    return templates.TemplateResponse(
        "config/sniffer.html",
        {
            "request": request,
            "config": config,
        },
    )
