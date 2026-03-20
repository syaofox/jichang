#!/usr/bin/env python3
"""OpenClash 配置编辑器 API."""

import subprocess
import sys
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ruamel.yaml import YAML

app = FastAPI(title="OpenClash Config Editor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
CONFIGS_DIR = BASE_DIR / "configs"
RULE_PROVIDERS_DIR = BASE_DIR / "rule-providers"
VALIDATE_SCRIPT = BASE_DIR / "validate_config.py"

ruamel_yaml = YAML()
ruamel_yaml.preserve_quotes = True
ruamel_yaml.default_flow_style = False


class ConfigFile(BaseModel):
    content: str


class RuleProvider(BaseModel):
    content: str


class ValidateRequest(BaseModel):
    config_file: str = "dns.yaml"
    config_dir: str = "configs"


class PatchConfigRequest(BaseModel):
    proxy_groups: list | None = None
    rules: list | None = None
    rule_providers: dict | None = None


@app.get("/api/configs")
def list_configs():
    """列出所有配置文件."""
    configs = []
    for f in sorted(CONFIGS_DIR.glob("*.yaml")):
        configs.append({"name": f.name, "size": f.stat().st_size})
    return configs


@app.get("/api/config/{filename}")
def get_config(filename: str):
    """读取配置文件."""
    path = CONFIGS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "配置文件不存在")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        data = None
    return {"filename": filename, "content": content, "data": data}


@app.put("/api/config/{filename}")
def save_config(filename: str, body: ConfigFile):
    """保存配置文件."""
    path = CONFIGS_DIR / filename
    try:
        yaml.safe_load(body.content)
    except yaml.YAMLError as e:
        raise HTTPException(400, f"YAML 语法错误: {e}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body.content)
    return {"status": "ok"}


@app.patch("/api/config/{filename}")
def patch_config(filename: str, body: PatchConfigRequest):
    """部分更新配置文件，保留原有格式."""
    path = CONFIGS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "配置文件不存在")

    with open(path, "r", encoding="utf-8") as f:
        data = ruamel_yaml.load(f)

    if body.proxy_groups is not None:
        data["proxy-groups"] = body.proxy_groups
    if body.rules is not None:
        data["rules"] = body.rules
    if body.rule_providers is not None:
        data["rule-providers"] = body.rule_providers

    with open(path, "w", encoding="utf-8") as f:
        ruamel_yaml.dump(data, f)

    return {"status": "ok"}


@app.get("/api/rule-providers")
def list_rule_providers():
    """列出所有规则文件."""
    files = []
    for f in sorted(RULE_PROVIDERS_DIR.glob("*.list")):
        lines = f.read_text(encoding="utf-8").splitlines()
        rule_count = sum(
            1 for l in lines if l.strip() and not l.strip().startswith("#")
        )
        files.append({"name": f.name, "rules": rule_count})
    return files


@app.get("/api/rule-provider/{filename}")
def get_rule_provider(filename: str):
    """读取规则文件."""
    path = RULE_PROVIDERS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "规则文件不存在")
    content = path.read_text(encoding="utf-8")
    return {"filename": filename, "content": content}


@app.put("/api/rule-provider/{filename}")
def save_rule_provider(filename: str, body: RuleProvider):
    """保存规则文件."""
    path = RULE_PROVIDERS_DIR / filename
    path.write_text(body.content, encoding="utf-8")
    return {"status": "ok"}


@app.delete("/api/rule-provider/{filename}")
def delete_rule_provider(filename: str):
    """删除规则文件."""
    path = RULE_PROVIDERS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "规则文件不存在")
    path.unlink()
    return {"status": "ok"}


@app.post("/api/validate")
def validate_config(body: ValidateRequest):
    """验证配置文件."""
    if not VALIDATE_SCRIPT.exists():
        raise HTTPException(500, "验证脚本不存在")
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATE_SCRIPT),
                body.config_file,
                "-c",
                body.config_dir,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(BASE_DIR),
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "验证超时")


@app.get("/api/config-structure")
def get_config_structure():
    """获取配置文件结构信息."""
    structure = {
        "rule_types": [
            "DOMAIN",
            "DOMAIN-SUFFIX",
            "DOMAIN-KEYWORD",
            "DOMAIN-REGEX",
            "GEOSITE",
            "GEOIP",
            "IP-CIDR",
            "IP-CIDR6",
            "RULE-SET",
            "MATCH",
            "PROCESS-NAME",
            "DST-PORT",
            "SRC-PORT",
            "NETWORK",
        ],
        "proxy_types": ["select", "url-test", "fallback", "load-balance"],
        "rule_provider_behaviors": ["domain", "ipcidr", "classical"],
        "rule_provider_formats": ["yaml", "text", "mrs"],
        "rule_provider_types": ["http", "file", "inline"],
    }
    return structure


app.mount(
    "/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static"
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
