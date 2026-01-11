import sqlite3
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / 'dashboard.db'
CLEANED = BASE / 'cleaned' / 'cleaned.jsonl'
PRED = BASE / 'cleaned' / 'predictions.jsonl'


def init_db(conn):
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS scrapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        text TEXT,
        fetched_at TEXT
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        fetched_at TEXT,
        forecast_json TEXT
    )''')
    conn.commit()


def load_jsonl(path, callback):
    if not path.exists():
        return 0
    count = 0
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            callback(j)
            count += 1
    return count


def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cur = conn.cursor()

    def insert_scrape(rec):
        cur.execute(
            'INSERT INTO scrapes (url,title,text,fetched_at) VALUES (?,?,?,?)',
            (rec.get('url'),
             rec.get('title'),
             rec.get('text'),
             rec.get('fetched_at')))

    def insert_pred(rec):
        cur.execute(
            'INSERT INTO predictions (url,fetched_at,forecast_json) VALUES (?,?,?)',
            (rec.get('url'),
             rec.get('fetched_at'),
             json.dumps(
                rec.get(
                    'forecast',
                    {}))))

    n1 = load_jsonl(CLEANED, insert_scrape)
    n2 = load_jsonl(PRED, insert_pred)
    conn.commit()
    print(f'Inserted {n1} scrapes and {n2} predictions into {DB_PATH}')
    conn.close()


if __name__ == '__main__':
    main()
