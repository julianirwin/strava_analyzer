from pathlib import Path

from strava_analyzer.context_export import export_context
from strava_analyzer.ingest import ingest_export
from strava_analyzer.query import connect, filter_activities, group_activity_counts


def test_full_ingest_and_context_export(tmp_path: Path) -> None:
    fixture_export = Path(__file__).parent / "fixtures" / "sample_export" / "export_0001"
    account_root = tmp_path / "account_export"
    account_root.mkdir()
    export_dir = account_root / fixture_export.name
    export_dir.mkdir()

    for src in fixture_export.rglob("*"):
        rel = src.relative_to(fixture_export)
        dst = export_dir / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())

    parquet_file = tmp_path / "data" / "parquet" / "activities.parquet"
    db_file = tmp_path / "data" / "catalog.duckdb"
    llm_context_dir = tmp_path / "llm_context"

    df = ingest_export(
        export_dir=export_dir,
        account_export_dir=account_root,
        parquet_file=parquet_file,
        db_file=db_file,
    )
    assert len(df) == 3
    assert parquet_file.exists()
    assert db_file.exists()

    con = connect(db_file)
    try:
        rides = filter_activities(con, activity_types=["Ride"])
        assert len(rides) == 2
        grouped = group_activity_counts(con)
        assert "activity_count" in grouped.columns
    finally:
        con.close()

    summary_md, extract_csv = export_context(db_file=db_file, llm_context_dir=llm_context_dir)
    assert summary_md.exists()
    assert extract_csv.exists()
