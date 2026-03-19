"""Routes package."""

from webui.routes.dashboard import router as dashboard_router
from webui.routes.config import router as config_router
from webui.routes.rules import router as rules_router
from webui.routes.api import router as api_router
from webui.routes.configs import router as configs_router

__all__ = [
    "dashboard_router",
    "config_router",
    "rules_router",
    "api_router",
    "configs_router",
]
