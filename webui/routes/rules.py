"""Rules management routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from webui.templates import templates
from webui.services.rule_service import RuleService

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("", response_class=HTMLResponse)
async def rules_index(request: Request):
    """Rules index page."""
    rule_service = RuleService()
    rule_files = rule_service.list_rule_files()

    return templates.TemplateResponse(
        "rules/index.html",
        {
            "request": request,
            "rule_files": rule_files,
        },
    )


@router.get("/edit/{filename}", response_class=HTMLResponse)
async def rules_edit(request: Request, filename: str):
    """Rule file editor page."""
    rule_service = RuleService()
    rule_file = rule_service.read_rule_file(filename)
    rule_types = rule_service.get_rule_types()

    return templates.TemplateResponse(
        "rules/editor.html",
        {
            "request": request,
            "rule_file": rule_file,
            "rule_types": rule_types,
        },
    )
