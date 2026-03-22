# Strava Analyzer

Local Python toolkit for analyzing Strava account exports with a DuckDB + Parquet catalog, notebook-friendly query helpers, and privacy-safe LLM context artifacts.

## Quick Start

1. Install dependencies:
```bash
uv sync --dev
```

2. Ingest the latest export under `account_export/`:
```bash
uv run strava-analyzer ingest
```

3. Rebuild catalog from parquet (optional when ingest already ran):
```bash
uv run strava-analyzer build-catalog
```

4. Generate LLM context artifacts:
```bash
uv run strava-analyzer export-context
```

5. Open the starter notebook:
```bash
uv run jupyter notebook notebooks/starter_analysis.ipynb
```

## Data and Privacy

- Raw Strava export files remain in `account_export/` and are git-ignored.
- Derived catalog outputs are written under `data/`.
- `llm_context/artifacts/` stores coarse, privacy-safe summaries and extracts (no point-by-point route traces).

## Project Layout

- `src/strava_analyzer/`: package code
- `tests/`: unit and integration tests
- `docs/`: architecture and schema docs
- `llm_context/`: decisions, journals, runbooks, and generated artifacts
- `notebooks/`: notebook-first analysis entrypoint
