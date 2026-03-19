"""WebUI configuration module."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_FILE = BASE_DIR / "dns-allv2.yaml"
CONFIGS_DIR = BASE_DIR / "configs"
ACTIVE_FILE = CONFIGS_DIR / "active.txt"
RULES_DIR = BASE_DIR / "rules"


def get_active_config_name() -> str:
    """Get the name of the currently active config file."""
    if ACTIVE_FILE.exists():
        name = ACTIVE_FILE.read_text().strip()
        if name:
            return name
    return "dns-allv2.yaml"


def set_active_config(name: str) -> None:
    """Set the active config file."""
    ACTIVE_FILE.write_text(name)
