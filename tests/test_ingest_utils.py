from pathlib import Path

from strava_analyzer.ingest import discover_latest_export_dir, normalize_columns


def test_normalize_columns_handles_duplicates() -> None:
    cols = ["Elapsed Time", "Elapsed Time", "Distance (m)"]
    assert normalize_columns(cols) == ["elapsed_time", "elapsed_time_2", "distance_m"]


def test_discover_latest_export_dir(tmp_path: Path) -> None:
    root = tmp_path / "account_export"
    root.mkdir()
    (root / "export_100").mkdir()
    (root / "export_200").mkdir()
    latest = discover_latest_export_dir(root)
    assert latest.name == "export_200"
