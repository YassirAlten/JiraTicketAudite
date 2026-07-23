#!/usr/bin/env python3
import json
from pathlib import Path
import shutil

base = Path('JiraTicketAudit') / 'ml_engine'
if not base.exists():
    print('ml_engine folder not found at', base.resolve())
    exit(0)

files = list(base.glob('*.json'))
print('Found:', [str(f) for f in files])

def transform_score(current, is_good):
    try:
        curr = float(current)
    except Exception:
        return current
    if is_good == 1:
        return curr * 0.5 + 2.5
    return curr * 2.5

total = 0
for f in files:
    bak = f.with_suffix(f.suffix + '.bak')
    try:
        shutil.copy2(f, bak)
    except Exception:
        pass
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
    except Exception as e:
        print('Skipping', f.name, 'parse error', e)
        continue
    changed = 0
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and 'is_description_content_good' in item and 'description_quality_score' in item:
                is_good = item.get('is_description_content_good')
                cur = item.get('description_quality_score')
                new = transform_score(cur, is_good)
                if new != cur:
                    item['description_quality_score'] = new
                    changed += 1
    if changed:
        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f.name + ':', changed, 'updated')
    total += changed
print('Total updated:', total)
