#!/usr/bin/env python3
"""从 blackmatrix7/ios_rule_script 同步更新 rule-providers 下的规则文件."""

import sys
import urllib.request
import re
from pathlib import Path

# 上游映射: 本地文件名 -> 上游分类名
UPSTREAM = {
    'youtubeapp': 'YouTube',
    'tiktok': 'TikTok',
    'netflix': 'Netflix',
    'telegram': 'Telegram',
    'twitter': 'Twitter',
    'instagram': 'Instagram',
    'openai': 'OpenAI',
}

BASE_URL = (
    'https://raw.githubusercontent.com'
    '/blackmatrix7/ios_rule_script/master/rule/Clash'
)

RULE_DIR = Path(__file__).parent / 'rule-providers'


def download(url):
    """下载文件内容，返回行列表."""
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            text = resp.read().decode('utf-8')
            return text.splitlines()
    except Exception as e:
        print(f'  下载失败: {e}', file=sys.stderr)
        return None


def should_keep(line):
    """判断规则行是否应该保留（过滤路由器上无效的规则类型）. """
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return True
    return not re.match(
        r'^(IP-CIDR|IP-CIDR6|PROCESS-NAME)\b', stripped, re.IGNORECASE
    )


def update_file(local_name, category):
    """更新单个规则文件."""
    url = f'{BASE_URL}/{category}/{category}.list'
    print(f'  {local_name:12} <- {category}.list ... ', end='')

    lines = download(url)
    if lines is None:
        print('跳过')
        return False

    lines = [l for l in lines if should_keep(l)]

    dst = RULE_DIR / f'{local_name}.list'
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        for line in lines:
            f.write(line.rstrip() + '\n')

    count = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    print(f'{count} 条规则')
    return True


def main():
    args = sys.argv[1:]

    if not RULE_DIR.exists():
        print(f'错误: 目录不存在: {RULE_DIR}', file=sys.stderr)
        sys.exit(1)

    names = args if args else sorted(UPSTREAM.keys())

    ok = 0
    fail = 0
    for name in names:
        if name not in UPSTREAM:
            print(f'  未知规则: {name}（可选: {", ".join(sorted(UPSTREAM.keys()))}）')
            fail += 1
            continue
        category = UPSTREAM[name]
        if update_file(name, category):
            ok += 1
        else:
            fail += 1

    total = ok + fail
    print(f'\n完成: {ok}/{total} 个文件更新成功')
    sys.exit(0 if fail == 0 else 1)


if __name__ == '__main__':
    main()
