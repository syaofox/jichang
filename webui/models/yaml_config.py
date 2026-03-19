"""Clash configuration data models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProxyProvider(BaseModel):
    """Proxy provider configuration."""

    url: str = ""
    type: str = "http"
    interval: int = 864000
    health_check: Optional[Dict[str, Any]] = None
    proxy: str = "直连"


class ProxyGroup(BaseModel):
    """Proxy group configuration."""

    name: str
    type: str = "select"
    proxies: Optional[List[str]] = None
    include_all: Optional[bool] = None
    filter: Optional[str] = None
    tolerance: Optional[int] = None
    url: Optional[str] = None
    interval: Optional[int] = None

    def model_post_init(self, __context):
        if self.type == "select" and self.proxies is None:
            self.proxies = []


class RuleProvider(BaseModel):
    """Rule provider configuration."""

    type: str = "http"
    interval: int = 86400
    behavior: str = "domain"
    format: str = "mrs"
    url: str = ""


class DnsConfig(BaseModel):
    """DNS configuration."""

    enable: bool = True
    cache_algorithm: str = "arc"
    listen: str = "0.0.0.0:1053"
    ipv6: bool = False
    respect_rules: bool = True
    enhanced_mode: str = "fake-ip"
    fake_ip_range: str = "28.0.0.1/8"
    fake_ip_filter_mode: str = "blacklist"
    default_nameserver: List[str] = Field(
        default_factory=lambda: ["https://223.5.5.5/dns-query"]
    )
    proxy_server_nameserver: List[str] = Field(
        default_factory=lambda: [
            "https://dns.alidns.com/dns-query",
            "https://doh.pub/dns-query",
        ]
    )
    direct_nameserver: List[str] = Field(
        default_factory=lambda: [
            "https://dns.alidns.com/dns-query",
            "https://doh.pub/dns-query",
        ]
    )
    nameserver: List[str] = Field(
        default_factory=lambda: ["https://8.8.8.8/dns-query#RULES&ecs=223.5.5.0/24"]
    )
    fake_ip_filter: List[str] = Field(default_factory=list)


class TunConfig(BaseModel):
    """TUN configuration."""

    enable: bool = True
    stack: str = "mixed"
    dns_hijack: List[str] = Field(default_factory=lambda: ["any:53", "tcp://any:53"])
    device: Optional[str] = None
    auto_route: bool = False
    auto_redirect: bool = False
    auto_detect_interface: bool = False


class SnifferConfig(BaseModel):
    """Sniffer configuration."""

    enable: bool = True
    sniff: Dict[str, Any] = Field(default_factory=dict)
    skip_domain: List[str] = Field(default_factory=list)


class ClashConfig(BaseModel):
    """Main Clash configuration model."""

    mixed_port: int = 7890
    allow_lan: bool = True
    bind_address: str = "*"
    ipv6: bool = False
    unified_delay: bool = True
    tcp_concurrent: bool = True
    log_level: str = "warning"
    global_client_fingerprint: str = "chrome"
    keep_alive_idle: int = 600
    keep_alive_interval: int = 15

    profile: Dict[str, bool] = Field(
        default_factory=lambda: {"store-selected": True, "store-fake-ip": True}
    )

    proxy_providers: Dict[str, ProxyProvider] = Field(default_factory=dict)
    proxies: List[Dict[str, Any]] = Field(
        default_factory=lambda: [{"name": "直连", "type": "direct"}]
    )

    dns: DnsConfig = Field(default_factory=DnsConfig)
    tun: TunConfig = Field(default_factory=TunConfig)
    sniffer: Optional[SnifferConfig] = None

    proxy_groups: List[ProxyGroup] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    rule_anchor: Optional[Dict[str, Any]] = None
    rule_providers: Dict[str, RuleProvider] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        populate_by_name = True
