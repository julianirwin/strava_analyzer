from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from strava_analyzer.constants import DEFAULT_DB_FILE, DEFAULT_LLM_CONTEXT_DIR


def _round_coord_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "route_start_lat",
        "route_start_lon",
        "route_end_lat",
        "route_end_lon",
        "route_bbox_min_lat",
        "route_bbox_max_lat",
        "route_bbox_min_lon",
        "route_bbox_max_lon",
    ]
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").round(2)
    return out


def export_context(
    db_file: Path = DEFAULT_DB_FILE,
    llm_context_dir: Path = DEFAULT_LLM_CONTEXT_DIR,
) -> tuple[Path, Path]:
    artifacts_dir = llm_context_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_file))
    try:
        df = con.execute("SELECT * FROM activities").fetch_df()
    finally:
        con.close()

    total = len(df)
    by_type = (
        df.groupby("activity_type", dropna=False).size().sort_values(ascending=False)
        if total
        else pd.Series(dtype="int64")
    )
    by_equipment = (
        df.groupby("equipment_name", dropna=False).size().sort_values(ascending=False).head(10)
        if total
        else pd.Series(dtype="int64")
    )

    summary_lines = [
        "# Latest Activity Catalog Summary",
        "",
        f"- total activities: {total}",
    ]
    if total:
        min_dt = df["activity_datetime"].min()
        max_dt = df["activity_datetime"].max()
        summary_lines.append(f"- date range: {min_dt} to {max_dt}")

    summary_lines.extend(["", "## Activity Counts by Type"])
    for activity_type, count in by_type.items():
        summary_lines.append(f"- {activity_type}: {int(count)}")

    summary_lines.extend(["", "## Top Equipment"])
    for equipment_name, count in by_equipment.items():
        label = equipment_name if pd.notna(equipment_name) and equipment_name else "(none)"
        summary_lines.append(f"- {label}: {int(count)}")

    summary_md = artifacts_dir / "latest_summary.md"
    summary_md.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    extract_cols = [
        "activity_id",
        "activity_datetime",
        "activity_name",
        "activity_type",
        "distance_m",
        "elapsed_time_s",
        "average_speed_mps",
        "elevation_gain_m",
        "equipment_name",
        "equipment_type",
        "name_category",
        "time_of_day_label",
        "name_tag",
        "is_structured_commute",
        "commute_week_label",
        "commute_week_number",
        "commute_number",
        "commute_period",
        "commute_direction",
        "commute_label_raw",
        "commute_label_key",
        "commute_parse_notes",
        "route_point_count",
        "route_start_lat",
        "route_start_lon",
        "route_end_lat",
        "route_end_lon",
        "route_bbox_min_lat",
        "route_bbox_max_lat",
        "route_bbox_min_lon",
        "route_bbox_max_lon",
    ]
    existing_cols = [c for c in extract_cols if c in df.columns]
    extract = _round_coord_columns(df[existing_cols])

    extract_csv = artifacts_dir / "activity_extract.csv"
    extract.to_csv(extract_csv, index=False)
    return summary_md, extract_csv
