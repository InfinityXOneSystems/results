import time
from pathlib import Path
import subprocess

PIPELINE_RESULTS = Path(r"c:\AI\repos\crawler_pipeline\results")
INGEST_SCRIPT = Path(r"c:\AI\repos\results\ingest\ingest_from_pipeline.py")
CLEAN_SCRIPT = Path(r"c:\AI\repos\results\cleaning\normalize.py")

CHECK_INTERVAL = 5

seen = set()


def list_files():
    if not PIPELINE_RESULTS.exists():
        return []
    return sorted([p for p in PIPELINE_RESULTS.glob('*.json')])


def run_cmd(script_path):
    subprocess.run(["python", str(script_path)], check=False)


if __name__ == '__main__':
    print("Starting watcher, checking:", PIPELINE_RESULTS)
    while True:
        files = list_files()
        new = [p for p in files if p.name not in seen]
        if new:
            print("New files detected:", [p.name for p in new])
            run_cmd(INGEST_SCRIPT)
            run_cmd(CLEAN_SCRIPT)
            for p in new:
                seen.add(p.name)
        time.sleep(CHECK_INTERVAL)
