# jichang

> Clash 代理配置文件仓库，用于 OpenClash/Mihomo。

## 订阅地址

```
https://raw.githubusercontent.com/syaofox/jichang/main/dns-allv2.yaml
```

## 功能特点

- DNS 防泄露配置
- 智能分流规则
- 多地区节点支持（🇭🇰🇹🇼🇯🇵🇰🇷🇸🇬🇺🇲）
- 支持 OpenClash / Mihomo

## WebUI 管理界面

可视化编辑配置文件，管理规则文件。

### 快速启动

```bash
# 安装依赖
uv sync

# 启动 WebUI
uv run uvicorn webui.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

### WebUI 功能

| 功能 | 说明 |
|------|------|
| 仪表盘 | 配置概览、规则统计 |
| DNS 设置 | Nameserver / Fake-IP / 过滤器 |
| TUN 配置 | 入站 / 路由模式 |
| 代理分组 | 节点优先级管理 |
| 规则编辑 | 可视化编辑规则文件 |

## 目录结构

```
jichang/
├── dns-allv2.yaml    # 主配置文件
├── rules/            # 自定义规则文件
│   ├── proxy.list
│   ├── domestic.list
│   ├── dmm.list
│   └── ...
├── webui/            # WebUI 管理界面
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── templates/
└── pyproject.toml    # Python 依赖
```

## 配置规范

### 代理分组

| 分组 | 用途 |
|------|------|
| 默认代理 | 常规代理流量 |
| 国内补充 | 需要直连的国内域名 |
| YouTube | 🇯🇵 日本优先 |
| ChatGPT | 🇯🇵 日本优先 |
| NETFLIX | 🇸🇬 坡县优先 |
| Telegram | 🇭🇰 香港优先 |
| GitHub | 🇭🇰 香港优先 |

### 规则类型

```
DOMAIN-SUFFIX,example.com     # 域名后缀
DOMAIN-KEYWORD,gmail          # 域名关键字
IP-CIDR,10.0.0.0/8,no-resolve  # IP 段
```

## 技术栈

- **WebUI**: FastAPI + HTMX + TailwindCSS
- **配置**: PyYAML + Pydantic
- **依赖管理**: uv
