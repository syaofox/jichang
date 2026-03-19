"""API routes for HTMX updates."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from webui.services.yaml_service import YamlService
from webui.services.rule_service import RuleService

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/configs")
async def api_list_configs():
    """List all configuration files."""
    configs = YamlService.list_configs()
    active = YamlService.get_active_config()
    return JSONResponse(
        content={
            "configs": configs,
            "active": active,
        }
    )


@router.post("/configs")
async def api_create_config(request: Request):
    """Create a new configuration file."""
    data = await request.json()
    name = data.get("name", "")

    if not name:
        return JSONResponse(
            content={"success": False, "error": "名称不能为空"}, status_code=400
        )

    if not name.endswith(".yaml"):
        name = f"{name}.yaml"

    success = YamlService.create_config(name)
    if not success:
        return JSONResponse(
            content={"success": False, "error": "配置文件已存在"}, status_code=400
        )

    return JSONResponse(content={"success": True, "name": name})


@router.delete("/configs/{name}")
async def api_delete_config(name: str):
    """Delete a configuration file."""
    success = YamlService.delete_config(name)
    if not success:
        return JSONResponse(
            content={"success": False, "error": "无法删除配置文件"}, status_code=400
        )

    return JSONResponse(content={"success": True})


@router.post("/configs/{name}/activate")
async def api_activate_config(name: str):
    """Set a configuration as active."""
    success = YamlService.activate_config(name)
    if not success:
        return JSONResponse(
            content={"success": False, "error": "配置文件不存在"}, status_code=400
        )

    return JSONResponse(content={"success": True, "active": name})


@router.get("/config/dns")
async def api_get_dns():
    """Get DNS configuration fragment."""
    yaml_service = YamlService()
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_dns_partial(config))


@router.post("/config/dns")
async def api_update_dns(request: Request):
    """Update DNS configuration."""
    yaml_service = YamlService()
    data = await request.form()

    dns_data = {}
    for key, value in data.items():
        if key.startswith("dns."):
            attr = key[4:]
            if attr in ("ipv6", "enable", "respect_rules"):
                dns_data[attr] = value == "true" or value == "on"
            elif attr in (
                "cache_algorithm",
                "listen",
                "enhanced_mode",
                "fake_ip_range",
                "fake_ip_filter_mode",
            ):
                dns_data[attr] = value
            elif attr.endswith("[]"):
                attr_name = attr[:-2]
                if attr_name not in dns_data:
                    dns_data[attr_name] = []
                dns_data[attr_name].append(value)
            else:
                dns_data[attr] = value

    yaml_service.update_dns(dns_data)
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_dns_partial(config))


@router.get("/config/tun")
async def api_get_tun():
    """Get TUN configuration fragment."""
    yaml_service = YamlService()
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_tun_partial(config))


@router.post("/config/tun")
async def api_update_tun(request: Request):
    """Update TUN configuration."""
    yaml_service = YamlService()
    data = await request.form()

    tun_data = {}
    for key, value in data.items():
        if key.startswith("tun."):
            attr = key[4:]
            if attr in (
                "enable",
                "auto_route",
                "auto_redirect",
                "auto_detect_interface",
            ):
                tun_data[attr] = value == "true" or value == "on"
            else:
                tun_data[attr] = value

    yaml_service.update_tun(tun_data)
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_tun_partial(config))


@router.get("/config/proxy-groups")
async def api_get_proxy_groups():
    """Get proxy groups fragment."""
    yaml_service = YamlService()
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_proxy_groups_partial(config))


@router.post("/config/proxy-groups")
async def api_update_proxy_groups(request: Request):
    """Update proxy groups."""
    yaml_service = YamlService()
    data = await request.json()

    yaml_service.update_proxy_groups(data)
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_proxy_groups_partial(config))


@router.get("/config/providers")
async def api_get_providers():
    """Get providers fragment."""
    yaml_service = YamlService()
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_providers_partial(config))


@router.post("/config/providers")
async def api_update_providers(request: Request):
    """Update providers."""
    yaml_service = YamlService()
    data = await request.json()

    yaml_service.update_providers(data)
    config = yaml_service.get_config()
    return HTMLResponse(content=_render_providers_partial(config))


@router.get("/rules")
async def api_get_rules():
    """Get rule files list."""
    rule_service = RuleService()
    rule_files = rule_service.list_rule_files()
    return JSONResponse(
        content={
            "files": [{"name": rf.name, "count": len(rf.rules)} for rf in rule_files]
        }
    )


@router.get("/rules/{filename}")
async def api_get_rule_file(filename: str):
    """Get rule file content."""
    rule_service = RuleService()
    rule_file = rule_service.read_rule_file(filename)
    return JSONResponse(
        content={
            "name": rule_file.name,
            "rules": [r.model_dump() for r in rule_file.rules],
        }
    )


@router.post("/rules/{filename}")
async def api_update_rule_file(filename: str, request: Request):
    """Update rule file."""
    rule_service = RuleService()
    data = await request.json()

    content = data.get("content", "")
    rule_service.save_rule_file(filename, content)

    return JSONResponse(content={"success": True})


@router.post("/rules/{filename}/add")
async def api_add_rule(filename: str, request: Request):
    """Add rule to file."""
    rule_service = RuleService()
    data = await request.json()

    rule_line = data.get("line", "")
    rule_service.add_rule(filename, rule_line)

    rule_file = rule_service.read_rule_file(filename)
    return HTMLResponse(content=_render_rules_table(rule_file))


@router.delete("/rules/{filename}/{line_num}")
async def api_delete_rule(filename: str, line_num: int):
    """Delete rule from file."""
    rule_service = RuleService()
    rule_service.remove_rule(filename, line_num)

    rule_file = rule_service.read_rule_file(filename)
    return HTMLResponse(content=_render_rules_table(rule_file))


@router.get("/preview")
async def api_preview():
    """Get YAML preview."""
    import yaml

    yaml_service = YamlService()
    raw = yaml_service.get_raw_config()

    content = yaml.dump(
        raw, allow_unicode=True, default_flow_style=False, sort_keys=False
    )
    return HTMLResponse(
        content=f'<pre class="yaml-preview"><code>{content}</code></pre>'
    )


def _render_dns_partial(config) -> str:
    """Render DNS partial HTML."""
    return f"""
    <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium mb-1">监听地址</label>
                <input type="text" name="dns.listen" value="{config.dns.listen}" 
                    hx-post="/api/config/dns" hx-trigger="change" hx-swap="none"
                    class="w-full px-3 py-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium mb-1">增强模式</label>
                <select name="dns.enhanced_mode" hx-post="/api/config/dns" hx-trigger="change" hx-swap="none"
                    class="w-full px-3 py-2 border rounded">
                    <option value="fake-ip" {"selected" if config.dns.enhanced_mode == "fake-ip" else ""}>Fake-IP</option>
                    <option value="redir-host" {"selected" if config.dns.enhanced_mode == "redir-host" else ""}>Redir-Host</option>
                </select>
            </div>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Fake-IP 范围</label>
            <input type="text" name="dns.fake_ip_range" value="{config.dns.fake_ip_range}"
                hx-post="/api/config/dns" hx-trigger="change" hx-swap="none"
                class="w-full px-3 py-2 border rounded">
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Nameserver (每行一个)</label>
            <textarea name="dns.nameserver" rows="3"
                hx-post="/api/config/dns" hx-trigger="change" hx-swap="none"
                class="w-full px-3 py-2 border rounded font-mono text-sm">{"\\n".join(config.dns.nameserver)}</textarea>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Direct Nameserver (每行一个)</label>
            <textarea name="dns.direct_nameserver" rows="2"
                hx-post="/api/config/dns" hx-trigger="change" hx-swap="none"
                class="w-full px-3 py-2 border rounded font-mono text-sm">{"\\n".join(config.dns.direct_nameserver)}</textarea>
        </div>
        <div class="flex gap-4">
            <label class="flex items-center gap-2">
                <input type="checkbox" name="dns.enable" value="true" {"checked" if config.dns.enable else ""}
                    hx-post="/api/config/dns" hx-trigger="change" hx-swap="none">
                启用 DNS
            </label>
            <label class="flex items-center gap-2">
                <input type="checkbox" name="dns.ipv6" value="true" {"checked" if config.dns.ipv6 else ""}
                    hx-post="/api/config/dns" hx-trigger="change" hx-swap="none">
                启用 IPv6
            </label>
        </div>
    </div>
    """


def _render_tun_partial(config) -> str:
    """Render TUN partial HTML."""
    return f"""
    <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium mb-1">Stack 模式</label>
                <select name="tun.stack" hx-post="/api/config/tun" hx-trigger="change" hx-swap="none"
                    class="w-full px-3 py-2 border rounded">
                    <option value="system" {"selected" if config.tun.stack == "system" else ""}>System</option>
                    <option value="gvisor" {"selected" if config.tun.stack == "gvisor" else ""}>Gvisor</option>
                    <option value="mixed" {"selected" if config.tun.stack == "mixed" else ""}>Mixed</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium mb-1">DNS 劫持</label>
                <input type="text" name="tun.dns_hijack" value="{",".join(config.tun.dns_hijack)}"
                    hx-post="/api/config/tun" hx-trigger="change" hx-swap="none"
                    class="w-full px-3 py-2 border rounded">
            </div>
        </div>
        <div class="space-y-2">
            <label class="flex items-center gap-2">
                <input type="checkbox" name="tun.auto_route" value="true" {"checked" if config.tun.auto_route else ""}
                    hx-post="/api/config/tun" hx-trigger="change" hx-swap="none">
                Auto Route (手动接管)
            </label>
            <label class="flex items-center gap-2">
                <input type="checkbox" name="tun.auto_redirect" value="true" {"checked" if config.tun.auto_redirect else ""}
                    hx-post="/api/config/tun" hx-trigger="change" hx-swap="none">
                Auto Redirect
            </label>
            <label class="flex items-center gap-2">
                <input type="checkbox" name="tun.auto_detect_interface" value="true" {"checked" if config.tun.auto_detect_interface else ""}
                    hx-post="/api/config/tun" hx-trigger="change" hx-swap="none">
                Auto Detect Interface
            </label>
        </div>
    </div>
    """


def _render_proxy_groups_partial(config) -> str:
    """Render proxy groups partial HTML."""
    groups_html = ""
    for i, group in enumerate(config.proxy_groups):
        groups_html += f"""
        <div class="proxy-group-card bg-white p-4 rounded-lg shadow" data-index="{i}">
            <div class="flex justify-between items-center mb-3">
                <h3 class="font-medium">{group.name}</h3>
                <span class="text-xs bg-gray-200 px-2 py-1 rounded">{group.type}</span>
            </div>
            <div class="proxy-list min-h-[60px] border rounded p-2" data-group="{i}">
                {"<br>".join(group.proxies) if group.proxies else '<span class="text-gray-400">无</span>'}
            </div>
        </div>
        """

    return f"""
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="proxy-groups-grid">
        {groups_html}
    </div>
    """


def _render_providers_partial(config) -> str:
    """Render providers partial HTML."""
    providers_html = ""
    for name, provider in config.proxy_providers.items():
        providers_html += f"""
        <div class="provider-card bg-white p-4 rounded-lg shadow">
            <h3 class="font-medium mb-2">{name}</h3>
            <div class="text-sm text-gray-600">
                <p>类型: {provider.type}</p>
                <p>更新间隔: {provider.interval}秒</p>
                <p>健康检查代理: {provider.proxy}</p>
            </div>
            <div class="mt-2">
                <input type="text" value="{provider.url}" placeholder="订阅地址"
                    class="w-full px-2 py-1 border rounded text-sm"
                    hx-post="/api/config/providers" hx-trigger="change" hx-swap="none">
            </div>
        </div>
        """

    return f"""
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="providers-grid">
        {providers_html}
    </div>
    """


def _render_rules_table(rule_file) -> str:
    """Render rules table HTML."""
    rows = ""
    for rule in rule_file.rules:
        if rule.type:
            rows += f"""
            <tr class="border-b hover:bg-gray-50">
                <td class="px-2 py-1">{rule.id}</td>
                <td class="px-2 py-1 font-mono text-xs">{rule.type}</td>
                <td class="px-2 py-1 font-mono text-xs">{rule.value}</td>
                <td class="px-2 py-1">{rule.proxy}</td>
                <td class="px-2 py-1">
                    <button class="text-red-500 hover:text-red-700" 
                        hx-delete="/api/rules/{rule_file.name}/{rule.id}"
                        hx-target="closest tr"
                        hx-swap="outerHTML">删除</button>
                </td>
            </tr>
            """

    return f"""
    <table class="w-full text-sm">
        <thead>
            <tr class="bg-gray-100">
                <th class="px-2 py-1 text-left w-12">#</th>
                <th class="px-2 py-1 text-left w-32">类型</th>
                <th class="px-2 py-1 text-left">值</th>
                <th class="px-2 py-1 text-left w-24">代理</th>
                <th class="px-2 py-1 text-left w-16">操作</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
