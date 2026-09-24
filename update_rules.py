#!/usr/bin/env python3
"""从上游同步更新 rule-providers 下的列表文件."""

import sys
import urllib.request
from pathlib import Path

# 上游映射: 本地文件名 -> 完整 URL
# 目前为 fakeipfilter 纯域名列表（DNS fake-ip-filter 使用），下载后原样保存
UPSTREAM = {
    'fakeipfilter-cn': (
        'https://raw.githubusercontent.com/qichiyuhub/rule'
        '/refs/heads/main/rules/fakeipfilter-cn.list'
    ),
    'fakeipfilter-!cn': (
        'https://raw.githubusercontent.com/qichiyuhub/rule'
        '/refs/heads/main/rules/fakeipfilter-!cn.list'
    ),
}

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


def update_file(local_name, url, label):
    """更新单个列表文件，返回是否成功."""
    print(f'  {local_name:16} <- {label} ... ', end='')

    lines = download(url)
    if lines is None:
        print('跳过')
        return False

    dst = RULE_DIR / f'{local_name}.list'
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        for line in lines:
            f.write(line.rstrip() + '\n')

    count = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    print(f'{count} 条')
    return True


def main():
    args = sys.argv[1:]

    if not RULE_DIR.exists():
        print(f'错误: 目录不存在: {RULE_DIR}', file=sys.stderr)
        sys.exit(1)

    names = args if args else sorted(UPSTREAM)

    ok = 0
    fail = 0
    for name in names:
        if name not in UPSTREAM:
            print(f'  未知规则: {name}（可选: {", ".join(sorted(UPSTREAM))}）')
            fail += 1
            continue

        url = UPSTREAM[name]
        label = '/'.join(url.split('/')[-2:])
        if update_file(name, url, label):
            ok += 1
        else:
            fail += 1

    total = ok + fail
    print(f'\n完成: {ok}/{total} 个文件更新成功')
    sys.exit(0 if fail == 0 else 1)


if __name__ == '__main__':
    main()
