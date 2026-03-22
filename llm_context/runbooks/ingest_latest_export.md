# Runbook: Ingest Latest Export

```bash
uv run strava-analyzer ingest
uv run strava-analyzer export-context
```

If needed, ingest a specific export folder:
```bash
uv run strava-analyzer ingest --export-dir account_export/export_21467475
```
