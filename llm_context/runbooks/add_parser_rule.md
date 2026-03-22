# Runbook: Add Naming Parser Rule

1. Edit `src/strava_analyzer/naming.py`.
2. Add/adjust parser condition.
3. Update parser tests in `tests/test_naming.py`.
4. Update docs in `docs/naming_parser.md`.
5. Run:
```bash
uv run pytest
uv run ruff check .
```
