import json
import shutil
from pathlib import Path


def transform_score(current, is_good):
    try:
        curr = float(current)
    except Exception:
        return current
    if is_good == 1:
        return curr * 0.5 + 2.5
    return curr * 0.5


def process_file(path: Path):
    bak = path.with_suffix(path.suffix + '.bak')
    try:
        shutil.copy2(path, bak)
    except Exception:
        pass
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Skipping {path.name}: JSON parse error: {e}")
            return 0

    if isinstance(data, list):
        changed = 0
        for item in data:
            if not isinstance(item, dict):
                continue
            if 'is_description_content_good' in item and 'description_quality_score' in item:
                is_good = item.get('is_description_content_good')
                cur = item.get('description_quality_score')
                item['description_quality_score'] = transform_score(cur, is_good)
                changed += 1
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return changed
    else:
        return 0



if __name__ == '__main__':
    filepath=Path(r'C:\Users\yjamal\Desktop\JiraTicketAudit\JiraTicketAudite\JiraTicketAudit\ml_engine\M2_data.json')
    process_file(filepath)
