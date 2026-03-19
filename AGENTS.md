# AGENTS.md

> Clash 代理配置文件仓库，用于 OpenClash/Mihomo。

## 项目概述

- **配置目录**: `configs/` - Clash 配置文件目录
- **模板文件**: `dns-allv2.yaml` - 配置文件模板（只读）
- **规则文件**: `rules/*.list` - 路由规则列表（Clash classical 格式）
- **WebUI**: `webui/` - 可视化管理界面

## 目录结构

```
/mnt/github/jichang/
├── configs/                 # 配置文件目录
│   ├── active.txt          # 当前活跃配置名
│   └── dns-allv2.yaml       # 默认配置文件
├── dns-allv2.yaml          # 模板文件（只读）
├── rules/                   # 规则文件目录
│   └── *.list              # Clash 规则列表
└── webui/                   # WebUI 目录
```

## 多配置文件管理

WebUI 支持管理多个 Clash 配置文件：

- **新建**: 从模板复制创建新配置
- **切换**: 通过顶部导航栏快速切换
- **删除**: 管理页面删除不需要的配置
- **激活**: 设置当前使用的配置

### 工作流

1. 创建多个配置文件（如：dns-allv2.yaml, my-config.yaml）
2. 通过 WebUI 顶部切换当前使用的配置
3. 提交到 GitHub
4. OpenClash 用户通过订阅 URL 获取更新

## 配置文件规范

### dns-allv2.yaml

- **格式**: YAML，缩进 2 空格
- **注释**: 中文，描述性，放在关键模块上方
- **YAML anchors**: 用 `&name` / `<<: *name` 复用 `rule-anchor` 配置
- **proxy-groups**: 使用 emoji 国旗前缀（🇭🇰🇹🇼🇯🇵🇰🇷🇸🇬🇺🇲）
- **rule-anchor 示例**:
  ```yaml
  rule-anchor:
    ip: &ip {type: http, interval: 86400, behavior: ipcidr, format: mrs}
    domain: &domain {type: http, interval: 86400, behavior: domain, format: mrs}
    class: &class {type: http, interval: 86400, behavior: classical, format: text}
  ```
- **rule-providers URL**: 必须指向 `syaofox/jichang@refs/heads/main/rules/`

### rules/*.list

- **格式**: Clash classical rule，每行一条规则
- **规则类型**:
  - `DOMAIN-SUFFIX,example.com` - 域名后缀
  - `DOMAIN-KEYWORD,keyword` - 域名关键字
  - `IP-CIDR,10.0.0.0/8,no-resolve` - IP 段，末尾 `no-resolve` 阻止 DNS 解析
  - `RULE-SET,name,proxy` - 引用远程规则集（仅在 yaml 的 rules 段使用）
- **注释**: 中文，带分类标题注释（如 `# 域名后缀匹配`）
- **顺序**: 按 `DOMAIN-SUFFIX` → `DOMAIN-KEYWORD` → `IP-CIDR` 排列

## 规则集命名规范

| 规则文件 | rule-provider name | proxy-group | 说明 |
|---|---|---|---|
| proxy.list | proxylite | 默认代理 | 代理补充 |
| domestic.list | domestic | 国内补充 | 国内直连 |
| dmm.list | dmm | dmm | 日本 DMM |
| javdb.list | javdb | javdb | JAV 数据库 |
| manhuagui.list | manhuagui | 漫画柜 | 漫画网站 |
| 18comic.list | x18comic | 禁漫天堂 | 18禁漫画 |
| pikpak.list | pikpak | pikpak | PikPak |
| opencode.list | opencode | opencode | opencode.ai |

## proxy-groups 优先级排序

按服务地区需求调整分组内节点顺序：
- `🇯🇵 日本` 优先: YouTube, ChatGPT, TikTok, dmm, PayPal
- `🇸🇬 坡县` 优先: NETFLIX
- `🇭🇰 香港` 优先: 默认代理, GitHub, Telegram, OneDrive, Microsoft

## 新增规则流程

1. 在 `rules/` 下创建或编辑 `.list` 文件
2. 在 `dns-allv2.yaml` 的 `rule-providers` 中添加条目，引用 GitHub raw URL
3. 在 `dns-allv2.yaml` 的 `rules` 中添加 RULE-SET 条目
4. 如需单独分组，在 `proxy-groups` 中添加对应条目
5. 确保 GitHub remote URL 使用 `@refs/heads/main` 固定分支

## WebUI 开发

```bash
# 安装依赖
uv sync

# 启动开发服务器
uv run uvicorn webui.main:app --reload

# 技术栈
# - FastAPI - 后端框架
# - HTMX - 无刷新交互
# - TailwindCSS - 样式
# - Pydantic - 数据验证
```

### WebUI 路由

| 路径 | 功能 |
|------|------|
| `/` | 仪表盘 |
| `/configs` | 配置文件管理 |
| `/config/dns` | DNS 设置 |
| `/config/tun` | TUN 配置 |
| `/config/proxy-groups` | 代理分组 |
| `/config/providers` | 订阅源 |
| `/rules` | 规则文件列表 |
| `/rules/edit/<file>` | 规则编辑器 |

## 注意事项

- 不要在配置中硬编码订阅地址（已在 `proxy-providers` 中占位）
- 注释掉的面板/UI 配置不要删除，保留给使用插件的用户参考
- `tun` 段的 `auto-route/auto-redirect/auto-detect-interface` 为手动接管模式配置
- 规则尽量精简，避免过度复杂影响性能
- `rule-providers` 中的 `url` 必须是完整的 raw.githubusercontent.com URL
