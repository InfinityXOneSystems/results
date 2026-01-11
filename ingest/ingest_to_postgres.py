import os
import json
from pathlib import Path
import psycopg2

BASE = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL not set')


def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS scrapes (
        id SERIAL PRIMARY KEY,
        url TEXT,
        title TEXT,
        text TEXT,
        fetched_at TIMESTAMP
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        url TEXT,
        fetched_at TIMESTAMP,
        forecast_json JSONB
    )
    ''')
    conn.commit()


def load_jsonl(path, insert_fn):
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
            insert_fn(j)
            count += 1
    return count


def main():
    conn = psycopg2.connect(DATABASE_URL)
    ensure_schema(conn)
    cur = conn.cursor()

    def insert_scrape(rec):
        cur.execute(
            'INSERT INTO scrapes (url,title,text,fetched_at) VALUES (%s,%s,%s,%s)',
            (rec.get('url'),
             rec.get('title'),
             rec.get('text'),
             rec.get('fetched_at')))

    def insert_pred(rec):
        cur.execute(
            'INSERT INTO predictions (url,fetched_at,forecast_json) VALUES (%s,%s,%s)',
            (rec.get('url'),
             rec.get('fetched_at'),
             json.dumps(
                rec.get(
                    'forecast',
                    {}))))

    n1 = load_jsonl(BASE / 'cleaned' / 'cleaned.jsonl', insert_scrape)
    n2 = load_jsonl(BASE / 'cleaned' / 'predictions.jsonl', insert_pred)
    conn.commit()
    print(f'Inserted {n1} scrapes and {n2} predictions')
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
