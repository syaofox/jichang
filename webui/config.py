"""WebUI configuration module."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
YAML_FILE = BASE_DIR / "dns-allv2.yaml"
RULES_DIR = BASE_DIR / "rules"
