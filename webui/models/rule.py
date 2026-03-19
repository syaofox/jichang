"""Rule data models."""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class RuleType(str, Enum):
    """Rule type enumeration."""

    DOMAIN_SUFFIX = "DOMAIN-SUFFIX"
    DOMAIN_KEYWORD = "DOMAIN-KEYWORD"
    DOMAIN = "DOMAIN"
    IP_CIDR = "IP-CIDR"
    IP_CIDR6 = "IP-CIDR6"
    GEOIP = "GEOIP"
    RULE_SET = "RULE-SET"
    PROCESS_NAME = "PROCESS-NAME"
    DOMAIN_LIST = "DOMAIN-LIST"
    IP_LIST = "IP-LIST"
    RULE_SET_LOCAL = "RULE-SET,LOCAL"
    MATCH = "MATCH"
    NO_RESOLVE = "no-resolve"


class Rule(BaseModel):
    """Single rule model."""

    id: int
    type: str
    value: str
    proxy: str = ""
    options: str = ""
    comment: Optional[str] = None
    enabled: bool = True

    @classmethod
    def from_line(cls, line: str, line_num: int) -> "Rule":
        """Parse a rule line."""
        raw = line.strip()

        if not raw or raw.startswith("#"):
            comment = raw.lstrip("# ").strip() if raw.startswith("#") else None
            return cls(id=line_num, type="", value="", comment=comment, enabled=False)

        parts = raw.split(",")
        rule_type = parts[0] if parts else ""
        value = parts[1] if len(parts) > 1 else ""
        proxy = parts[2] if len(parts) > 2 else ""
        options = parts[3] if len(parts) > 3 else ""

        return cls(
            id=line_num, type=rule_type, value=value, proxy=proxy, options=options
        )

    def to_line(self) -> str:
        """Convert rule to YAML line format."""
        if self.comment and not self.type:
            return f"# {self.comment}"
        if not self.type or not self.value:
            return ""

        parts = [self.type, self.value]
        if self.proxy:
            parts.append(self.proxy)
        if self.options:
            parts.append(self.options)

        return ",".join(parts)


class RuleFile(BaseModel):
    """Rule file model."""

    name: str
    path: str
    rules: list[Rule] = Field(default_factory=list)
    modified: bool = False

    @property
    def content(self) -> str:
        """Generate file content."""
        lines = []
        for rule in self.rules:
            line = rule.to_line()
            if line:
                lines.append(line)
        return "\n".join(lines)
