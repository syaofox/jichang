"""Rule file service."""

from pathlib import Path
from typing import List, Optional
from webui.config import RULES_DIR
from webui.models.rule import Rule, RuleFile


class RuleService:
    """Service for managing rule files."""

    @staticmethod
    def list_rule_files() -> List[RuleFile]:
        """List all rule files."""
        files = []
        if not RULES_DIR.exists():
            return files

        for path in sorted(RULES_DIR.glob("*.list")):
            files.append(RuleService.read_rule_file(path.name))

        return files

    @staticmethod
    def read_rule_file(filename: str) -> RuleFile:
        """Read a rule file."""
        path = RULES_DIR / filename
        rule_file = RuleFile(name=filename, path=str(path))

        if not path.exists():
            return rule_file

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        rules = []
        for i, line in enumerate(lines, 1):
            rule = Rule.from_line(line.strip(), i)
            rules.append(rule)

        rule_file.rules = rules
        return rule_file

    @staticmethod
    def save_rule_file(filename: str, content: str) -> bool:
        """Save rule file content."""
        path = RULES_DIR / filename

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return True

    @staticmethod
    def create_rule_file(filename: str, initial_content: str = "") -> bool:
        """Create a new rule file."""
        path = RULES_DIR / filename

        if path.exists():
            return False

        with open(path, "w", encoding="utf-8") as f:
            f.write(initial_content)

        return True

    @staticmethod
    def delete_rule_file(filename: str) -> bool:
        """Delete a rule file."""
        path = RULES_DIR / filename

        if not path.exists():
            return False

        path.unlink()
        return True

    @staticmethod
    def add_rule(filename: str, rule_line: str) -> bool:
        """Add a rule to file."""
        path = RULES_DIR / filename

        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{rule_line}")

        return True

    @staticmethod
    def remove_rule(filename: str, line_num: int) -> bool:
        """Remove a rule from file by line number."""
        path = RULES_DIR / filename

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if line_num < 1 or line_num > len(lines):
            return False

        del lines[line_num - 1]

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return True

    @staticmethod
    def update_rule(filename: str, line_num: int, new_line: str) -> bool:
        """Update a rule in file."""
        path = RULES_DIR / filename

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if line_num < 1 or line_num > len(lines):
            return False

        lines[line_num - 1] = new_line + "\n"

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return True

    @staticmethod
    def get_rule_types() -> List[dict]:
        """Get available rule types with metadata."""
        return [
            {
                "value": "DOMAIN-SUFFIX",
                "label": "DOMAIN-SUFFIX",
                "desc": "域名后缀匹配",
                "has_proxy": True,
            },
            {
                "value": "DOMAIN-KEYWORD",
                "label": "DOMAIN-KEYWORD",
                "desc": "域名关键字匹配",
                "has_proxy": True,
            },
            {
                "value": "DOMAIN",
                "label": "DOMAIN",
                "desc": "完整域名匹配",
                "has_proxy": True,
            },
            {
                "value": "IP-CIDR",
                "label": "IP-CIDR",
                "desc": "IP段匹配",
                "has_proxy": True,
                "has_options": True,
            },
            {
                "value": "IP-CIDR6",
                "label": "IP-CIDR6",
                "desc": "IPv6段匹配",
                "has_proxy": True,
                "has_options": True,
            },
            {
                "value": "GEOIP",
                "label": "GEOIP",
                "desc": "GeoIP匹配",
                "has_proxy": True,
            },
            {
                "value": "PROCESS-NAME",
                "label": "PROCESS-NAME",
                "desc": "进程名匹配",
                "has_proxy": True,
            },
            {
                "value": "RULE-SET",
                "label": "RULE-SET",
                "desc": "引用远程规则集",
                "has_proxy": True,
                "has_options": True,
            },
            {
                "value": "MATCH",
                "label": "MATCH",
                "desc": "最终匹配",
                "has_proxy": True,
                "is_terminal": True,
            },
        ]
