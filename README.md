# InfinityXOneSystems — Results (Canonical)

This repository stores crawler output and the lightweight pipeline for ingesting, cleaning, and syncing results.

Structure:
- `uncleaned/` — raw JSON outputs from crawlers (ingest here)
- `cleaned/` — normalized and cleaned JSON ready for downstream use
- `ingest/` — helper scripts to pull pipeline outputs into `uncleaned/`
- `cleaning/` — simple normalizer/cleaner scripts
- `ops/` — operational instructions

Use the scripts in `ingest/` and `cleaning/` to move data from `crawler_pipeline/results` into this repo and normalize it.
