#!/usr/bin/env python3
"""Clash 配置文件验证工具."""

import argparse
import re
import sys
from pathlib import Path

RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "DOMAIN-REGEX",
    "GEOSITE",
    "GEOIP",
    "SRC-GEOIP",
    "IP-CIDR",
    "IP-CIDR6",
    "SRC-IP-CIDR",
    "IP-SUFFIX",
    "IP-ASN",
    "SRC-IP-ASN",
    "DST-PORT",
    "SRC-PORT",
    "PROCESS-NAME",
    "PROCESS-NAME-REGEX",
    "PROCESS-PATH",
    "PROCESS-PATH-REGEX",
    "UID",
    "NETWORK",
    "DSCP",
    "IN-PORT",
    "IN-TYPE",
    "IN-USER",
    "IN-NAME",
    "IPSET",
    "RULE-SET",
    "SCRIPT",
    "AND",
    "OR",
    "NOT",
    "SUB-RULE",
    "MATCH",
}

NO_RESOLVE_RULE_TYPES = {
    "GEOIP",
    "SRC-GEOIP",
    "IP-CIDR",
    "IP-CIDR6",
    "SRC-IP-CIDR",
    "IP-SUFFIX",
    "IP-ASN",
    "SRC-IP-ASN",
    "IPSET",
    "RULE-SET",
    "SCRIPT",
}

TWO_PART_RULE_TYPES = {"MATCH"}

LOGIC_RULE_TYPES = {"AND", "OR", "NOT", "SUB-RULE"}


RULE_LIST_RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "DOMAIN-REGEX",
    "GEOSITE",
    "GEOIP",
    "SRC-GEOIP",
    "IP-CIDR",
    "IP-CIDR6",
    "SRC-IP-CIDR",
    "IP-SUFFIX",
    "IP-ASN",
    "SRC-IP-ASN",
    "DST-PORT",
    "SRC-PORT",
    "PROCESS-NAME",
    "PROCESS-NAME-REGEX",
    "PROCESS-PATH",
    "PROCESS-PATH-REGEX",
    "UID",
    "NETWORK",
    "DSCP",
    "IN-PORT",
    "IN-TYPE",
    "IN-USER",
    "IN-NAME",
    "IPSET",
    "RULE-SET",
    "SCRIPT",
}

RULE_LIST_NO_RESOLVE_TYPES = {
    "GEOIP",
    "SRC-GEOIP",
    "IP-CIDR",
    "IP-CIDR6",
    "SRC-IP-CIDR",
    "IP-SUFFIX",
    "IP-ASN",
    "SRC-IP-ASN",
    "IPSET",
}


def validate_rule_provider_files(rule_providers_dir, errors, warnings):
    rp_file_count = 0
    rp_line_count = 0
    for rp_file in sorted(rule_providers_dir.glob("*.list")):
        rp_file_count += 1
        try:
            with open(rp_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            errors.append(f"{rp_file}: 无法读取文件: {e}")
            continue

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            rp_line_count += 1
            if stripped.startswith("-"):
                stripped = stripped.lstrip("- ").strip()

            parts = [p.strip() for p in stripped.split(",")]
            rule_type = parts[0].upper()
            parts_count = len(parts)

            if rule_type not in RULE_LIST_RULE_TYPES:
                errors.append(f"{rp_file}:{i} 未知规则类型「{rule_type}」: {stripped}")
                continue

            if rule_type in RULE_LIST_NO_RESOLVE_TYPES:
                if parts_count < 2:
                    warnings.append(f"{rp_file}:{i} 格式异常: {stripped}")
                elif parts_count > 2 and parts[2].lower() != "no-resolve":
                    warnings.append(f"{rp_file}:{i} 未知参数「{parts[2]}」: {stripped}")
            else:
                if parts_count < 2:
                    warnings.append(f"{rp_file}:{i} 格式异常: {stripped}")
    return rp_file_count, rp_line_count


def build_line_index(raw_lines):
    group_index = {}
    rule_index = []
    in_rules = False
    for i, line in enumerate(raw_lines, 1):
        stripped = line.strip()
        if stripped.startswith("rules:"):
            in_rules = True
            continue
        if in_rules and stripped.startswith("- "):
            rule_index.append(i)
            continue
        if stripped.startswith("- {"):
            m = re.search(r"name\s*:\s*([^,}]+)", stripped)
            if m:
                key = m.group(1).strip()
                group_index[key] = i
        elif stripped.startswith("-") and ":" in stripped:
            key = stripped.lstrip("- ").split(":")[0].strip()
            if key:
                group_index[key] = i
    return group_index, rule_index


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
    except ImportError:
        print("错误: 需要安装 pyyaml 库", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
        config = yaml.safe_load("".join(raw_lines))

        if not config:
            print("错误: 配置文件为空", file=sys.stderr)
            sys.exit(1)

    except yaml.YAMLError as e:
        print(f"错误: YAML 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    group_index, rule_index = build_line_index(raw_lines)
    errors = []
    warnings = []

    proxy_groups = config.get("proxy-groups", [])
    proxies = config.get("proxies", [])
    proxy_providers = config.get("proxy-providers", {})
    rules = config.get("rules", [])

    group_names = {g.get("name"): g for g in proxy_groups if isinstance(g, dict)}
    proxy_names = {p.get("name"): p for p in proxies if isinstance(p, dict)}
    provider_names = set(proxy_providers.keys())
    all_proxy_refs = set(group_names) | set(proxy_names) | provider_names
    all_proxy_refs.update(["DIRECT", "REJECT"])

    for group in proxy_groups:
        if not isinstance(group, dict):
            warnings.append(f"分组格式异常: {group}")
            continue

        name = group.get("name", "未命名")
        group_proxies = group.get("proxies", [])
        line = group_index.get(name, "?")

        if not group_proxies:
            warnings.append(f"{config_path}:{line} 分组「{name}」没有配置代理节点")
        elif not args.no_check_proxies:
            for proxy in group_proxies:
                if proxy not in all_proxy_refs:
                    errors.append(
                        f"{config_path}:{line} 分组「{name}」引用的代理「{proxy}」不存在"
                    )

    if not args.no_check_rules:
        rule_providers = config.get("rule-providers", {})
        provider_names = set(rule_providers.keys())
        rule_line_map = {r: rule_index[j] for j, r in enumerate(rules)}

        for rule in rules:
            if not rule.strip() or rule.startswith("#"):
                continue

            parts = [p.strip() for p in rule.split(",")]
            rule_type = parts[0].upper()
            parts_count = len(parts)
            rule_proxy = None
            line = rule_line_map[rule]

            if rule_type not in RULE_TYPES:
                errors.append(
                    f"{config_path}:{line} 未知规则类型「{rule_type}」: {rule}"
                )
                continue

            if rule_type in TWO_PART_RULE_TYPES:
                if parts_count < 2:
                    warnings.append(f"{config_path}:{line} 格式异常: {rule}")
                else:
                    rule_proxy = parts[1]
                    if parts_count > 2:
                        warnings.append(
                            f"{config_path}:{line} 多余部分将被忽略: {rule}"
                        )
            elif rule_type in LOGIC_RULE_TYPES:
                if parts_count < 3:
                    warnings.append(f"{config_path}:{line} 格式异常: {rule}")
                else:
                    rule_proxy = parts[2]
                    if parts_count > 3:
                        warnings.append(
                            f"{config_path}:{line} 多余部分将被忽略: {rule}"
                        )
                    if rule_type != "NOT" and not re.match(r"^\(.*\)$", parts[1]):
                        warnings.append(
                            f"{config_path}:{line} {rule_type} 规则条件应使用括号: {rule}"
                        )
            elif rule_type in NO_RESOLVE_RULE_TYPES:
                if parts_count < 3:
                    warnings.append(f"{config_path}:{line} 格式异常: {rule}")
                else:
                    rule_proxy = (
                        parts[2] if parts[2].lower() != "no-resolve" else parts[1]
                    )
                    if parts_count == 4 and parts[3].lower() != "no-resolve":
                        warnings.append(
                            f"{config_path}:{line} 未知参数「{parts[3]}」: {rule}"
                        )
            else:
                if parts_count < 3:
                    warnings.append(f"{config_path}:{line} 格式异常: {rule}")
                else:
                    rule_proxy = parts[2]
                    if parts_count > 3:
                        warnings.append(
                            f"{config_path}:{line} 多余部分将被忽略: {rule}"
                        )

            if rule_type == "RULE-SET" and len(parts) >= 2:
                provider = parts[1]
                if provider not in provider_names:
                    errors.append(
                        f"{config_path}:{line} 引用的规则集「{provider}」未定义"
                    )

            if rule_proxy and rule_proxy not in all_proxy_refs:
                errors.append(f"{config_path}:{line} 引用的代理「{rule_proxy}」不存在")

    rp_file_count = 0
    rp_line_count = 0
    if not args.no_check_rules:
        rule_providers_dir = Path(args.config_dir).parent / "rule-providers"
        if rule_providers_dir.exists():
            rp_file_count, rp_line_count = validate_rule_provider_files(
                rule_providers_dir, errors, warnings
            )

    print(f"文件: {config_path}")
    print(f"分组数: {len(proxy_groups)}")
    print(f"代理数: {len(proxies)}")
    print(f"规则数: {len([r for r in rules if r.strip() and not r.startswith('#')])}")
    if rp_file_count > 0:
        print(f"规则文件: {rp_file_count} 个, {rp_line_count} 条规则")
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
