// 状态管理
let state = {
    configs: [],
    ruleProviders: [],
    currentConfig: null,
    currentRuleFile: null,
    configData: null,
    structure: null,
};

// API 请求封装
async function api(method, path, body) {
    const opts = { method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`/api${path}`, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "请求失败");
    }
    return res.json();
}

// Tab 切换
document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById(tab.dataset.tab).classList.add("active");
    });
});

// 初始化
async function init() {
    try {
        const [configs, providers, structure] = await Promise.all([
            api("GET", "/configs"),
            api("GET", "/rule-providers"),
            api("GET", "/config-structure"),
        ]);
        state.configs = configs;
        state.ruleProviders = providers;
        state.structure = structure;
        renderRuleFileList();
        populateConfigSelects();
        if (configs.length > 0) {
            const savedConfig = localStorage.getItem("lastConfig");
            const configToLoad = savedConfig && configs.some(c => c.name === savedConfig)
                ? savedConfig
                : configs[0].name;
            loadConfig(configToLoad);
        }
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// 渲染规则文件列表
function renderRuleFileList() {
    const container = document.getElementById("rule-file-list");
    container.innerHTML = state.ruleProviders
        .map(
            (f) => `
        <div class="file-item${state.currentRuleFile === f.name ? " active" : ""}"
             onclick="loadRuleFile('${f.name}')">
            <span>${f.name}</span>
            <span class="count">${f.rules}条</span>
        </div>
    `
        )
        .join("");
}

// 加载规则文件
async function loadRuleFile(name) {
    try {
        const data = await api("GET", `/rule-provider/${name}`);
        state.currentRuleFile = name;
        document.getElementById("current-rule-file").textContent = name;
        const editor = document.getElementById("rule-editor");
        editor.value = data.content;
        editor.disabled = false;
        document.getElementById("btn-save-rule").disabled = false;
        renderRuleFileList();
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// 保存规则文件
async function saveRuleFile() {
    if (!state.currentRuleFile) return;
    try {
        const content = document.getElementById("rule-editor").value;
        await api("PUT", `/rule-provider/${state.currentRuleFile}`, { content });
        setStatus("规则文件已保存");
        const providers = await api("GET", "/rule-providers");
        state.ruleProviders = providers;
        renderRuleFileList();
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// 创建规则文件
function createRuleFile() {
    showModal("新建规则文件", `
        <div style="margin-bottom: 1rem">
            <label>文件名 (*.list)</label>
            <input type="text" id="new-rule-name" placeholder="例如: custom.list" style="width: 100%; margin-top: 0.5rem">
        </div>
    `, async () => {
        const name = document.getElementById("new-rule-name").value.trim();
        if (!name) return;
        const filename = name.endsWith(".list") ? name : name + ".list";
        try {
            await api("PUT", `/rule-provider/${filename}`, { content: "# 新规则文件\n" });
            const providers = await api("GET", "/rule-providers");
            state.ruleProviders = providers;
            renderRuleFileList();
            loadRuleFile(filename);
            closeModal();
        } catch (e) {
            setStatus(e.message, "error");
        }
    });
}

// 填充配置文件下拉框
function populateConfigSelects() {
    const selects = ["config-file-select", "rules-config-select", "rp-config-select", "yaml-config-select"];
    selects.forEach((id) => {
        const select = document.getElementById(id);
        select.innerHTML = state.configs.map((c) => `<option value="${c.name}">${c.name}</option>`).join("");
    });
}

// 加载配置文件
async function loadConfig(filename) {
    try {
        const data = await api("GET", `/config/${filename}`);
        state.currentConfig = filename;
        state.configData = data.data;
        localStorage.setItem("lastConfig", filename);
        renderProxyGroups();
        renderRules();
        renderRuleProviders();
        document.getElementById("yaml-editor-textarea").value = data.content;
        document.querySelectorAll(`select option[value="${filename}"]`).forEach((opt) => {
            opt.parentElement.value = filename;
        });
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// 渲染代理分组
function renderProxyGroups() {
    if (!state.configData) return;
    const groups = state.configData["proxy-groups"] || [];
    const body = document.getElementById("proxy-groups-body");
    body.innerHTML = groups
        .map(
            (g, i) => `
        <tr>
            <td><input type="text" value="${escHtml(g.name || "")}" onchange="updateGroup(${i}, 'name', this.value)"></td>
            <td>
                <select onchange="updateGroup(${i}, 'type', this.value)">
                    ${state.structure.proxy_types.map((t) => `<option${g.type === t ? " selected" : ""}>${t}</option>`).join("")}
                </select>
            </td>
            <td>
                <div class="proxies-list" data-group-index="${i}">
                    ${(g.proxies || []).map((p, j) => `<span class="tag" draggable="true" data-group-index="${i}" data-proxy-index="${j}" ondragstart="onProxyDragStart(event)" ondragover="onProxyDragOver(event)" ondrop="onProxyDrop(event)" ondragend="onProxyDragEnd(event)">${escHtml(p)}<span class="remove" onclick="removeProxy(${i}, ${j})">×</span></span>`).join("")}
                    <button class="btn-sm btn-icon" onclick="addProxy(${i})">+</button>
                </div>
            </td>
            <td>
                <button class="btn-sm btn-icon" onclick="moveGroup(${i}, -1)">↑</button>
                <button class="btn-sm btn-icon" onclick="moveGroup(${i}, 1)">↓</button>
                <button class="btn-sm danger" onclick="deleteGroup(${i})">删除</button>
            </td>
        </tr>
    `
        )
        .join("");
}

// 代理拖动排序
let draggedProxy = null;

function onProxyDragStart(e) {
    draggedProxy = {
        groupIndex: parseInt(e.target.dataset.groupIndex),
        proxyIndex: parseInt(e.target.dataset.proxyIndex),
    };
    e.target.classList.add("dragging");
    e.dataTransfer.effectAllowed = "move";
}

function onProxyDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
}

function onProxyDrop(e) {
    e.preventDefault();
    if (!draggedProxy) return;

    const targetGroupIndex = parseInt(e.target.dataset.groupIndex);
    const targetProxyIndex = parseInt(e.target.dataset.proxyIndex);

    if (draggedProxy.groupIndex !== targetGroupIndex) return;

    const proxies = state.configData["proxy-groups"][targetGroupIndex].proxies;
    const [moved] = proxies.splice(draggedProxy.proxyIndex, 1);
    proxies.splice(targetProxyIndex, 0, moved);

    renderProxyGroups();
}

function onProxyDragEnd(e) {
    e.target.classList.remove("dragging");
    draggedProxy = null;
}

// 更新分组
function updateGroup(index, field, value) {
    const groups = state.configData["proxy-groups"];
    groups[index][field] = value;
}

// 添加分组
function addProxyGroup() {
    const groups = state.configData["proxy-groups"];
    groups.push({ name: "新分组", type: "select", proxies: ["直连"] });
    renderProxyGroups();
}

// 删除分组
function deleteGroup(index) {
    state.configData["proxy-groups"].splice(index, 1);
    renderProxyGroups();
}

// 移动分组
function moveGroup(index, dir) {
    const groups = state.configData["proxy-groups"];
    const newIndex = index + dir;
    if (newIndex < 0 || newIndex >= groups.length) return;
    [groups[index], groups[newIndex]] = [groups[newIndex], groups[index]];
    renderProxyGroups();
}

// 添加代理到分组
function addProxy(groupIndex) {
    const allProxies = getAvailableProxies();
    const currentProxies = state.configData["proxy-groups"][groupIndex].proxies || [];
    const availableProxies = allProxies.filter(p => !currentProxies.includes(p));

    showModal("添加代理", `
        <div style="margin-bottom: 1rem">
            <input type="text" id="proxy-search" placeholder="搜索代理..." style="width: 100%; margin-bottom: 0.5rem" oninput="filterProxyList()">
            <div id="proxy-list" style="max-height: 300px; overflow-y: auto; border: 1px solid var(--border); border-radius: 4px; padding: 0.5rem">
                ${availableProxies.map(p => `<div class="proxy-option" onclick="selectProxy('${escHtml(p)}')" style="padding: 0.5rem; cursor: pointer; border-radius: 4px" onmouseover="this.style.background='var(--border)'" onmouseout="this.style.background='transparent'">${escHtml(p)}</div>`).join("")}
            </div>
        </div>
        <div style="display: flex; gap: 0.5rem">
            <input type="text" id="proxy-name" placeholder="或输入自定义代理名称" style="flex: 1">
        </div>
    `, () => {
        const name = document.getElementById("proxy-name").value.trim();
        if (!name) return;
        state.configData["proxy-groups"][groupIndex].proxies.push(name);
        renderProxyGroups();
        closeModal();
    });

    window._selectProxy = (name) => {
        document.getElementById("proxy-name").value = name;
    };

    window._filterProxyList = () => {
        const search = document.getElementById("proxy-search").value.toLowerCase();
        document.querySelectorAll(".proxy-option").forEach(el => {
            el.style.display = el.textContent.toLowerCase().includes(search) ? "block" : "none";
        });
    };
}

function selectProxy(name) {
    document.getElementById("proxy-name").value = name;
}

function filterProxyList() {
    const search = document.getElementById("proxy-search").value.toLowerCase();
    document.querySelectorAll(".proxy-option").forEach(el => {
        el.style.display = el.textContent.toLowerCase().includes(search) ? "block" : "none";
    });
}

// 获取所有可用代理
function getAvailableProxies() {
    const proxies = [];
    const groups = state.configData["proxy-groups"] || [];
    const proxyList = state.configData["proxies"] || [];

    // 添加内置代理
    proxies.push("直连", "DIRECT", "REJECT");

    // 添加 proxies 列表中的代理
    proxyList.forEach(p => {
        if (p.name) proxies.push(p.name);
    });

    // 添加 proxy-groups 中的分组名称
    groups.forEach(g => {
        if (g.name) proxies.push(g.name);
    });

    return [...new Set(proxies)];
}

// 移除代理
function removeProxy(groupIndex, proxyIndex) {
    state.configData["proxy-groups"][groupIndex].proxies.splice(proxyIndex, 1);
    renderProxyGroups();
}

// 渲染规则
function renderRules() {
    if (!state.configData) return;
    const rules = state.configData.rules || [];
    const body = document.getElementById("rules-body");
    body.innerHTML = rules
        .map((r, i) => {
            const parts = r.split(",").map((p) => p.trim());
            return `
        <tr>
            <td>${i + 1}</td>
            <td>
                <select onchange="updateRuleType(${i}, this.value)">
                    ${state.structure.rule_types.map((t) => `<option${parts[0] === t ? " selected" : ""}>${t}</option>`).join("")}
                </select>
            </td>
            <td><input type="text" value="${escHtml(parts[1] || "")}" onchange="updateRulePart(${i}, 1, this.value)" style="width: 100%"></td>
            <td><input type="text" value="${escHtml(parts[2] || "")}" onchange="updateRulePart(${i}, 2, this.value)" style="width: 120px"></td>
            <td><input type="text" value="${escHtml(parts[3] || "")}" onchange="updateRulePart(${i}, 3, this.value)" style="width: 100px"></td>
            <td>
                <button class="btn-sm btn-icon" onclick="moveRule(${i}, -1)">↑</button>
                <button class="btn-sm btn-icon" onclick="moveRule(${i}, 1)">↓</button>
                <button class="btn-sm danger" onclick="deleteRule(${i})">删除</button>
            </td>
        </tr>
    `;
        })
        .join("");
}

// 更新规则
function updateRuleType(index, value) {
    const rules = state.configData.rules;
    const parts = rules[index].split(",").map((p) => p.trim());
    parts[0] = value;
    rules[index] = parts.join(",");
}

function updateRulePart(index, partIndex, value) {
    const rules = state.configData.rules;
    let parts = rules[index].split(",").map((p) => p.trim());
    while (parts.length <= partIndex) parts.push("");
    parts[partIndex] = value;
    rules[index] = parts.filter((p, i) => p || i < 2).join(",");
}

// 添加规则
function addRule() {
    state.configData.rules.push("DOMAIN-SUFFIX,example.com,直连");
    renderRules();
}

// 删除规则
function deleteRule(index) {
    state.configData.rules.splice(index, 1);
    renderRules();
}

// 移动规则
function moveRule(index, dir) {
    const rules = state.configData.rules;
    const newIndex = index + dir;
    if (newIndex < 0 || newIndex >= rules.length) return;
    [rules[index], rules[newIndex]] = [rules[newIndex], rules[index]];
    renderRules();
}

// 渲染规则提供者
function renderRuleProviders() {
    if (!state.configData) return;
    const providers = state.configData["rule-providers"] || {};
    const body = document.getElementById("rule-providers-body");
    body.innerHTML = Object.entries(providers)
        .map(
            ([name, cfg]) => `
        <tr>
            <td>${escHtml(name)}</td>
            <td>${escHtml(cfg.type || "")}</td>
            <td>${escHtml(cfg.behavior || "")}</td>
            <td>${escHtml(cfg.format || "")}</td>
            <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escHtml(cfg.url || "")}">${escHtml(cfg.url || "")}</td>
            <td>
                <button class="btn-sm" onclick="editRuleProvider('${name}')">编辑</button>
            </td>
        </tr>
    `
        )
        .join("");
}

// 编辑规则提供者
function editRuleProvider(name) {
    const cfg = state.configData["rule-providers"][name];
    showModal("编辑规则提供者: " + name, `
        <div style="margin-bottom: 1rem">
            <label>URL</label>
            <input type="text" id="rp-url" value="${escHtml(cfg.url || "")}" style="width: 100%; margin-top: 0.5rem">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem">
            <div>
                <label>类型</label>
                <select id="rp-type" style="width: 100%; margin-top: 0.5rem">
                    ${state.structure.rule_provider_types.map((t) => `<option${cfg.type === t ? " selected" : ""}>${t}</option>`).join("")}
                </select>
            </div>
            <div>
                <label>行为</label>
                <select id="rp-behavior" style="width: 100%; margin-top: 0.5rem">
                    ${state.structure.rule_provider_behaviors.map((b) => `<option${cfg.behavior === b ? " selected" : ""}>${b}</option>`).join("")}
                </select>
            </div>
            <div>
                <label>格式</label>
                <select id="rp-format" style="width: 100%; margin-top: 0.5rem">
                    ${state.structure.rule_provider_formats.map((f) => `<option${cfg.format === f ? " selected" : ""}>${f}</option>`).join("")}
                </select>
            </div>
        </div>
    `, () => {
        cfg.url = document.getElementById("rp-url").value;
        cfg.type = document.getElementById("rp-type").value;
        cfg.behavior = document.getElementById("rp-behavior").value;
        cfg.format = document.getElementById("rp-format").value;
        renderRuleProviders();
        closeModal();
    });
}

// YAML 编辑器加载
async function loadYaml(filename) {
    try {
        const data = await api("GET", `/config/${filename}`);
        document.getElementById("yaml-editor-textarea").value = data.content;
        state.currentConfig = filename;
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// 保存当前内容
async function saveCurrent() {
    const activeTab = document.querySelector(".tab.active").dataset.tab;
    try {
        if (activeTab === "rule-files") {
            await saveRuleFile();
        } else if (activeTab === "yaml-editor") {
            const content = document.getElementById("yaml-editor-textarea").value;
            const filename = document.getElementById("yaml-config-select").value;
            await api("PUT", `/config/${filename}`, { content });
            setStatus("配置已保存");
        } else {
            // proxy-groups, rules, rule-providers 使用同一个配置
            const content = yamlDump(state.configData);
            await api("PUT", `/config/${state.currentConfig}`, { content });
            document.getElementById("yaml-editor-textarea").value = content;
            setStatus("配置已保存");
        }
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// 验证配置
async function validateConfig() {
    const filename = state.currentConfig || "dns.yaml";
    try {
        setStatus("验证中...", "");
        const result = await api("POST", "/validate", { config_file: filename });
        if (result.success) {
            setStatus("验证通过 ✓", "success");
        } else {
            setStatus("验证失败: " + (result.stderr || result.stdout), "error");
        }
    } catch (e) {
        setStatus(e.message, "error");
    }
}

// Modal 控制
function showModal(title, body, onConfirm) {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-body").innerHTML = body;
    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("modal-confirm").onclick = onConfirm;
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
}

function confirmModal() {
    // handled by onclick
}

// 状态显示
function setStatus(msg, type) {
    const el = document.getElementById("status");
    el.textContent = msg;
    el.className = type || "";
}

// HTML 转义
function escHtml(str) {
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// 简单的 YAML dump (仅用于当前数据结构)
function yamlDump(obj, indent = 0) {
    const pad = "  ".repeat(indent);
    let result = "";
    if (Array.isArray(obj)) {
        for (const item of obj) {
            if (typeof item === "object" && item !== null) {
                result += `${pad}- ${yamlDump(item, indent + 1).trimStart()}\n`;
            } else {
                result += `${pad}- ${yamlValue(item)}\n`;
            }
        }
    } else if (typeof obj === "object" && obj !== null) {
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === "object" && value !== null) {
                if (Array.isArray(value)) {
                    result += `${pad}${key}:\n${yamlDump(value, indent + 1)}`;
                } else {
                    result += `${pad}${key}:\n${yamlDump(value, indent + 1)}`;
                }
            } else {
                result += `${pad}${key}: ${yamlValue(value)}\n`;
            }
        }
    } else {
        result = `${pad}${yamlValue(obj)}\n`;
    }
    return result;
}

function yamlValue(val) {
    if (val === null || val === undefined) return "null";
    if (typeof val === "boolean") return val ? "true" : "false";
    if (typeof val === "number") return String(val);
    const str = String(val);
    if (str.includes(":") || str.includes("#") || str.includes("'") || str.includes('"') || str.startsWith(" ") || str.endsWith(" ")) {
        return `"${str.replace(/"/g, '\\"')}"`;
    }
    return str;
}

// 键盘快捷键
document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        saveCurrent();
    }
});

// 初始化
init();
