# LLM Context Pipeline

Command: `strava-analyzer export-context`

Outputs:
- `llm_context/artifacts/latest_summary.md`
- `llm_context/artifacts/activity_extract.csv`

Privacy policy:
- no point-by-point route data in context artifacts
- no full raw GPX/FIT payloads
- coordinates in CSV extracts are rounded to 2 decimals

Recommended workflow:
1. `strava-analyzer ingest`
2. `strava-analyzer export-context`
3. add journal entry in `llm_context/journals/`

Commute analytics workflow:
- Use query helpers to compute yearly commute counts, AM/PM speed comparisons, and route-label mixes.
- Build notebook charts from grouped DataFrames (for example, route-label bar charts by year).
