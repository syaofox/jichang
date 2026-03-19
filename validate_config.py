#!/usr/bin/env python3
"""Clash 配置文件验证工具."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="验证 Clash 配置文件")
    parser.add_argument(
        "config_file",
        nargs="?",
        default="dns.yaml",
        help="配置文件名 (默认: dns.yaml)",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_dir",
        default="configs",
        help="配置文件目录 (默认: configs)",
    )
    parser.add_argument(
        "--no-check-proxies",
        action="store_true",
        help="跳过代理节点存在性检查",
    )
    parser.add_argument(
        "--no-check-rules",
        action="store_true",
        help="跳过规则代理引用检查",
    )
    args = parser.parse_args()

    config_path = Path(args.config_file)
    if not config_path.is_absolute():
        config_path = Path(args.config_dir) / config_path

    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        import yaml

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not config:
            print("错误: 配置文件为空", file=sys.stderr)
            sys.exit(1)

    except yaml.YAMLError as e:
        print(f"错误: YAML 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    errors = []
    warnings = []

    proxy_groups = config.get("proxy-groups", [])
    proxies = config.get("proxies", [])
    proxy_providers = config.get("proxy-providers", {})
    rules = config.get("rules", [])

    group_names = {g.get("name") for g in proxy_groups if isinstance(g, dict)}
    proxy_names = {p.get("name") for p in proxies if isinstance(p, dict)}
    provider_names = set(proxy_providers.keys())
    all_proxy_refs = group_names | proxy_names | provider_names
    all_proxy_refs.update(["DIRECT", "REJECT"])

    for group in proxy_groups:
        if not isinstance(group, dict):
            warnings.append(f"分组格式异常: {group}")
            continue

        name = group.get("name", "未命名")
        group_proxies = group.get("proxies", [])

        if not group_proxies:
            warnings.append(f"分组「{name}」没有配置代理节点")
        elif not args.no_check_proxies:
            for proxy in group_proxies:
                if proxy not in all_proxy_refs:
                    errors.append(f"分组「{name}」引用的代理「{proxy}」不存在")

    if not args.no_check_rules:
        for i, rule in enumerate(rules):
            if not rule.strip() or rule.startswith("#"):
                continue

            parts = rule.split(",")
            rule_type = parts[0].strip().upper()
            min_parts = 3 if rule_type not in ("MATCH", "NO-IP") else 2
            if len(parts) < min_parts:
                warnings.append(f"规则 #{i + 1} 格式异常: {rule}")
                continue

            rule_proxy = parts[-1].strip()
            if rule_proxy.lower() == "no-resolve":
                rule_proxy = parts[-2].strip() if len(parts) >= 2 else ""

            if rule_proxy and rule_proxy not in all_proxy_refs:
                errors.append(f"规则 #{i + 1} 引用的代理「{rule_proxy}」不存在")

    print(f"文件: {config_path}")
    print(f"分组数: {len(proxy_groups)}")
    print(f"代理数: {len(proxies)}")
    print(f"规则数: {len([r for r in rules if r.strip() and not r.startswith('#')])}")
    print()

    if warnings:
        print("警告:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("错误:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("验证通过 ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
