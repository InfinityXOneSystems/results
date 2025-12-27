import json
from pathlib import Path

SRC = Path(r"c:\AI\repos\results\uncleaned")
DEST = Path(r"c:\AI\repos\results\cleaned")

def normalize_record(obj):
    return {
        'url': obj.get('url'),
        'title': obj.get('title') or obj.get('meta', {}).get('title'),
        'text': obj.get('text') or obj.get('content', ''),
        'fetched_at': obj.get('fetched_at')
    }

def run():
    DEST.mkdir(parents=True, exist_ok=True)
    for p in SRC.glob('*.json'):
        data = json.loads(p.read_text(encoding='utf-8'))
        cleaned = normalize_record(data)
        out = DEST / p.name
        out.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Wrote cleaned: {out}")

if __name__ == '__main__':
    run()
