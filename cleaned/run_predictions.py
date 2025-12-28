import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
# ensure repo root is on sys.path so `services` package can be imported
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
from services.financial_predictor.market_predictor import MarketPredictor

IN_PATH = BASE / 'results' / 'cleaned' / 'cleaned.jsonl'
OUT_PATH = BASE / 'results' / 'cleaned' / 'predictions.jsonl'

pred = MarketPredictor()

def make_series_from_text(text: str):
    # simple numeric series: sliding word counts for windows of 1..n
    words = (text or '').split()
    # produce a short sequence based on sentence lengths or word count buckets
    return [float(min(len(words), i)) for i in range(1,6)]

def run():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with IN_PATH.open('r', encoding='utf-8') as inf, OUT_PATH.open('w', encoding='utf-8') as outf:
        for line in inf:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            series = {'_default': make_series_from_text(rec.get('text',''))}
            insights = {'series': series}
            forecast = pred.predict(insights, horizon=24)
            out = {'url': rec.get('url'), 'fetched_at': rec.get('fetched_at'), 'forecast': forecast}
            outf.write(json.dumps(out, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    run()
