#!/usr/bin/env python3
"""Enhanced collector using gh CLI (authenticated) to bypass rate limits."""
import json, time, subprocess, os
from pathlib import Path

queries = [
    'gpt-image-2',
    'gpt-image2',
    '"gpt image 2"',
    'gpt_image_2',
    'chatgpt images 2.0',
    'chatgpt-image-2',
    'awesome gpt-image-2',
    'gpt-image-2 skill',
    'gpt-image-2 mcp',
    'gpt-image-2 api',
    'gpt-image-2 comfyui',
    'gpt-image-2 prompts',
    'gpt-image-2 playground',
    'gptimage2 prompts',
    'openai gpt-image-2',
]

keys = [
    'gpt-image-2','gpt image 2','gpt_image_2','gptimage2',
    'chatgpt images 2.0','chatgpt-image-2','chatgpt image 2',
]

repos = {}
env = {**os.environ, 'https_proxy': 'http://127.0.0.1:7890', 'http_proxy': 'http://127.0.0.1:7890'}

for q in queries:
    for page in range(1, 5):
        params = f"q={q}&sort=stars&order=desc&per_page=100&page={page}"
        url = f"search/repositories?{params}"
        try:
            result = subprocess.run(
                ['gh', 'api', url],
                capture_output=True, text=True, env=env, timeout=45
            )
        except subprocess.TimeoutExpired:
            print(f"  Timeout for q={q!r} p={page}, skipping")
            break
        if result.returncode != 0:
            print(f"  Error for q={q!r} p={page}: {result.stderr[:100]}")
            break
        try:
            data = json.loads(result.stdout)
        except Exception as e:
            print(f"  JSON error: {e}")
            break
        items = data.get('items') or []
        if not items:
            break
        added = 0
        for it in items:
            full = (it.get('full_name') or '').strip()
            if not full:
                continue
            text = ' '.join([
                full,
                it.get('description') or '',
                ' '.join(it.get('topics') or []),
                it.get('homepage') or ''
            ]).lower()
            if not any(k in text for k in keys):
                continue
            repos[full] = {
                'full_name': full,
                'html_url': it.get('html_url') or f'https://github.com/{full}',
                'description': (it.get('description') or '').replace('\n', ' ').strip() or '—',
                'language': it.get('language') or '—',
                'license': ((it.get('license') or {}).get('spdx_id') or '—'),
                'stargazers_count': it.get('stargazers_count') or 0,
                'updated_at': it.get('updated_at') or '',
            }
            added += 1
        print(f"  q={q!r} page={page}: +{added} (total so far: {len(repos)})")
        if len(items) < 30:
            break
        time.sleep(0.3)

# Sort by stars desc, then updated_at desc
out = sorted(repos.values(), key=lambda x: (-x['stargazers_count'], x['updated_at']), reverse=False)
# Actually sort: stars desc first
out = sorted(repos.values(), key=lambda x: x['stargazers_count'], reverse=True)

Path('data').mkdir(exist_ok=True)
Path('data/repos.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

# Also produce CSV
import csv
with open('data/repos.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['full_name','html_url','description','language','license','stargazers_count','updated_at'])
    w.writeheader()
    w.writerows(out)

print(f'\nTotal: {len(out)} repos collected')
