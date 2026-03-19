"""YAML service for Clash configuration."""

import yaml
import copy
from pathlib import Path
from typing import Optional, Dict, Any
from webui.config import YAML_FILE, RULES_DIR
from webui.models.yaml_config import (
    ClashConfig,
    DnsConfig,
    TunConfig,
    SnifferConfig,
    ProxyGroup,
    ProxyProvider,
    RuleProvider,
)


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    result = []
    for i, c in enumerate(name):
        if c.isupper() and i > 0:
            result.append("_")
        result.append(c.lower())
    return "".join(result)


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class YamlService:
    """Service for managing Clash YAML configuration."""

    _instance: Optional["YamlService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config: Optional[ClashConfig] = None
            cls._instance._raw_config: Optional[Dict[str, Any]] = None
        return cls._instance

    def reload(self):
        """Reload configuration from file."""
        self._config = None
        self._raw_config = None
        self._load()

    def _load(self) -> tuple[ClashConfig, Dict[str, Any]]:
        """Load and parse YAML file."""
        if self._config is not None:
            return self._config, self._raw_config

        if not YAML_FILE.exists():
            raise FileNotFoundError(f"Config file not found: {YAML_FILE}")

        with open(YAML_FILE, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        self._raw_config = copy.deepcopy(raw) or {}
        self._config = self._parse_raw_config(raw)

        return self._config, self._raw_config

    def _parse_raw_config(self, raw: Dict[str, Any]) -> ClashConfig:
        """Parse raw config dict to ClashConfig model."""
        config = ClashConfig()

        simple_fields = [
            "mixed-port",
            "allow-lan",
            "bind-address",
            "ipv6",
            "unified-delay",
            "tcp-concurrent",
            "log-level",
            "global-client-fingerprint",
            "keep-alive-idle",
            "keep-alive-interval",
        ]

        for field in simple_fields:
            snake_field = field.replace("-", "_")
            if field in raw:
                setattr(config, snake_field, raw[field])

        if "profile" in raw:
            config.profile = raw["profile"]

        if "proxies" in raw:
            config.proxies = raw["proxies"]

        if "proxy-providers" in raw:
            providers = {}
            for name, data in raw["proxy-providers"].items():
                providers[name] = ProxyProvider(**data)
            config.proxy_providers = providers

        if "dns" in raw:
            config.dns = DnsConfig(**raw["dns"])

        if "tun" in raw:
            config.tun = TunConfig(**raw["tun"])

        if "sniffer" in raw:
            config.sniffer = SnifferConfig(**raw["sniffer"])

        if "proxy-groups" in raw:
            groups = []
            for group in raw["proxy-groups"]:
                if isinstance(group, dict):
                    groups.append(ProxyGroup(**group))
                elif isinstance(group, str):
                    import re

                    match = re.match(
                        r"- \{name: (.+), type: (.+), proxies: \[(.+)\]\}", group
                    )
                    if match:
                        groups.append(
                            ProxyGroup(
                                name=match.group(1),
                                type=match.group(2),
                                proxies=[p.strip() for p in match.group(3).split(",")],
                            )
                        )
            config.proxy_groups = groups

        if "rules" in raw:
            config.rules = raw["rules"]

        if "rule-providers" in raw:
            providers = {}
            for name, data in raw["rule-providers"].items():
                providers[name] = RuleProvider(**data)
            config.rule_providers = providers

        if "rule-anchor" in raw:
            config.rule_anchor = raw["rule-anchor"]

        return config

    def get_config(self) -> ClashConfig:
        """Get current configuration."""
        self._load()
        return self._config

    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw configuration dict."""
        self._load()
        return self._raw_config

    def _build_raw_config(self, config: ClashConfig) -> Dict[str, Any]:
        """Build raw config dict from ClashConfig model."""
        raw = {}

        raw["mixed-port"] = config.mixed_port
        raw["allow-lan"] = config.allow_lan
        raw["bind-address"] = config.bind_address
        raw["ipv6"] = config.ipv6
        raw["unified-delay"] = config.unified_delay
        raw["tcp-concurrent"] = config.tcp_concurrent
        raw["log-level"] = config.log_level
        raw["global-client-fingerprint"] = config.global_client_fingerprint
        raw["keep-alive-idle"] = config.keep_alive_idle
        raw["keep-alive-interval"] = config.keep_alive_interval

        raw["profile"] = config.profile
        raw["proxies"] = config.proxies

        if config.proxy_providers:
            raw["proxy-providers"] = {
                name: provider.model_dump(exclude_none=True)
                for name, provider in config.proxy_providers.items()
            }

        raw["dns"] = config.dns.model_dump(exclude_none=True)

        raw["tun"] = {
            "enable": config.tun.enable,
            "stack": config.tun.stack,
            "dns-hijack": config.tun.dns_hijack,
        }
        if config.tun.device:
            raw["tun"]["device"] = config.tun.device
        raw["tun"]["auto-route"] = config.tun.auto_route
        raw["tun"]["auto-redirect"] = config.tun.auto_redirect
        raw["tun"]["auto-detect-interface"] = config.tun.auto_detect_interface

        if config.sniffer:
            raw["sniffer"] = config.sniffer.model_dump(exclude_none=True)

        if config.proxy_groups:
            raw["proxy-groups"] = []
            for group in config.proxy_groups:
                group_dict = {"name": group.name, "type": group.type}
                if group.proxies is not None:
                    group_dict["proxies"] = group.proxies
                if group.include_all is not None:
                    group_dict["include-all"] = group.include_all
                if group.filter:
                    group_dict["filter"] = group.filter
                if group.tolerance is not None:
                    group_dict["tolerance"] = group.tolerance
                if group.url:
                    group_dict["url"] = group.url
                if group.interval is not None:
                    group_dict["interval"] = group.interval
                raw["proxy-groups"].append(group_dict)

        if config.rules:
            raw["rules"] = config.rules

        if config.rule_anchor:
            raw["rule-anchor"] = config.rule_anchor

        if config.rule_providers:
            raw["rule-providers"] = {
                name: provider.model_dump(exclude_none=True)
                for name, provider in config.rule_providers.items()
            }

        return raw

    def save(self) -> bool:
        """Save configuration to file."""
        if self._config is None:
            return False

        raw = self._build_raw_config(self._config)

        with open(YAML_FILE, "w", encoding="utf-8") as f:
            yaml.dump(
                raw, f, allow_unicode=True, default_flow_style=False, sort_keys=False
            )

        return True

    def update_dns(self, dns_data: Dict[str, Any]) -> bool:
        """Update DNS configuration."""
        config = self.get_config()
        for key, value in dns_data.items():
            if hasattr(config.dns, key):
                setattr(config.dns, key, value)
        return self.save()

    def update_tun(self, tun_data: Dict[str, Any]) -> bool:
        """Update TUN configuration."""
        config = self.get_config()
        for key, value in tun_data.items():
            if hasattr(config.tun, key):
                setattr(config.tun, key, value)
        return self.save()

    def update_sniffer(self, sniffer_data: Dict[str, Any]) -> bool:
        """Update sniffer configuration."""
        config = self.get_config()
        if config.sniffer is None:
            config.sniffer = SnifferConfig()
        for key, value in sniffer_data.items():
            if hasattr(config.sniffer, key):
                setattr(config.sniffer, key, value)
        return self.save()

    def update_proxy_groups(self, groups: list[Dict[str, Any]]) -> bool:
        """Update proxy groups."""
        config = self.get_config()
        config.proxy_groups = [ProxyGroup(**g) for g in groups]
        return self.save()

    def update_providers(self, providers: Dict[str, Dict[str, Any]]) -> bool:
        """Update proxy providers."""
        config = self.get_config()
        config.proxy_providers = {
            name: ProxyProvider(**data) for name, data in providers.items()
        }
        return self.save()

    def update_rules(self, rules: list[str]) -> bool:
        """Update rules list."""
        config = self.get_config()
        config.rules = rules
        return self.save()
