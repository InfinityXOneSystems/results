import shutil
import os
from pathlib import Path

PIPELINE_RESULTS = Path(r"c:\AI\repos\crawler_pipeline\results")
DEST = Path(r"c:\AI\repos\results\uncleaned")


def ingest_all():
    DEST.mkdir(parents=True, exist_ok=True)
    if not PIPELINE_RESULTS.exists():
        print(f"Pipeline results folder not found: {PIPELINE_RESULTS}")
        return
    for item in PIPELINE_RESULTS.glob('*.json'):
        dest = DEST / item.name
        print(f"Copying {item} -> {dest}")
        shutil.copy2(item, dest)


if __name__ == '__main__':
    ingest_all()
