# Architecture

## Pipeline

1. Detect latest `account_export/export_*` folder.
2. Read `activities.csv` with normalized unique column names.
3. Parse and normalize activity fields.
4. Parse structured bike commute names into commute-specific fields.
5. Enrich activities with equipment type and route summaries.
6. Persist to `data/parquet/activities.parquet`.
7. Build/update DuckDB catalog at `data/catalog.duckdb`.
8. Export privacy-safe LLM context files to `llm_context/artifacts/`.

## Core Modules

- `ingest.py`: export discovery + normalization + parquet output.
- `naming.py`: commute-only structured name parser.
- `routes.py`: GPX/FIT route summary extraction.
- `catalog.py`: DuckDB catalog creation.
- `query.py`: notebook-facing filtering and commute analytics helpers.
- `context_export.py`: markdown + CSV artifact generation.
