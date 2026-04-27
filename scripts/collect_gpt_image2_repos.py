#!/usr/bin/env python3
import json, time, urllib.parse, urllib.request
from pathlib import Path

queries = [
    'gpt-image-2','gpt-image2','"gpt image 2"','chatgpt images 2.0',
    'gpt_image_2','awesome gpt-image-2','gpt-image-2 skill','gpt-image-2 mcp','gpt-image-2 api'
]
keys = ['gpt-image-2','gpt image 2','gpt_image_2','gptimage2','chatgpt images 2.0','chatgpt-image-2']
headers = {'Accept':'application/vnd.github+json','User-Agent':'awesome-gpt-image2-collector'}
repos = {}
for q in queries:
    for page in range(1,4):
        p = urllib.parse.urlencode({'q':q,'sort':'stars','order':'desc','per_page':50,'page':page})
        req = urllib.request.Request(f'https://api.github.com/search/repositories?{p}', headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=35) as r:
                data = json.loads(r.read().decode('utf-8', errors='ignore'))
        except Exception:
            continue
        items = data.get('items') or []
        if not items:
            break
        for it in items:
            full = (it.get('full_name') or '').strip()
            if not full:
                continue
            text = ' '.join([full, it.get('description') or '', ' '.join(it.get('topics') or []), it.get('homepage') or '']).lower()
            if not any(k in text for k in keys):
                continue
            repos[full] = {
                'full_name': full,
                'html_url': it.get('html_url') or f'https://github.com/{full}',
                'description': (it.get('description') or '').replace('\n', ' ').strip() or '—',
                'language': it.get('language') or '—',
                'license': ((it.get('license') or {}).get('spdx_id') or '—'),
                                'updated_at': it.get('updated_at') or ''
            }
        time.sleep(0.45)
out = sorted(repos.values(), key=lambda x: (x['updated_at'], x['full_name']), reverse=True)
Path('data').mkdir(exist_ok=True)
Path('data/repos.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Collected {len(out)} repos')
