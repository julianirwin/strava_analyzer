from pathlib import Path

from strava_analyzer.routes import summarize_route_file

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_export" / "export_0001" / "activities"


def test_summarize_gpx_route() -> None:
    summary = summarize_route_file(FIXTURE_DIR / "1.gpx")
    assert summary["route_point_count"] == 3
    assert summary["route_start_lat"] is not None
    assert summary["route_polyline_hint"] is not None


def test_summarize_fit_route_handles_invalid() -> None:
    summary = summarize_route_file(FIXTURE_DIR / "2.fit")
    assert summary["route_point_count"] == 0
