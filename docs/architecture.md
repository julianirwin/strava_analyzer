# Architecture

## Pipeline

1. Detect latest `account_export/export_*` folder.
2. Read `activities.csv` with normalized unique column names.
3. Parse and normalize activity fields.
4. Enrich activities with equipment type and route summaries.
5. Persist to `data/parquet/activities.parquet`.
6. Build/update DuckDB catalog at `data/catalog.duckdb`.
7. Export privacy-safe LLM context files to `llm_context/artifacts/`.

## Core Modules

- `ingest.py`: export discovery + normalization + parquet output.
- `routes.py`: GPX/FIT route summary extraction.
- `catalog.py`: DuckDB catalog creation.
- `query.py`: notebook-facing filtering and grouping helpers.
- `context_export.py`: markdown + CSV artifact generation.
