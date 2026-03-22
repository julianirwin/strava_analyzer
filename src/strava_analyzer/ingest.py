from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

from strava_analyzer.catalog import build_catalog
from strava_analyzer.constants import (
    DEFAULT_ACCOUNT_EXPORT_DIR,
    DEFAULT_DB_FILE,
    DEFAULT_PARQUET_FILE,
)
from strava_analyzer.naming import parse_activity_name
from strava_analyzer.routes import summarize_route_file

_NUMERIC_SUFFIX_PATTERN = re.compile(r"_(\d+)$")


def normalize_columns(columns: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    normalized: list[str] = []
    for raw in columns:
        key = raw.strip().lower()
        key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
        key = key or "column"
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > 1:
            normalized.append(f"{key}_{counts[key]}")
        else:
            normalized.append(key)
    return normalized


def discover_latest_export_dir(account_export_dir: Path = DEFAULT_ACCOUNT_EXPORT_DIR) -> Path:
    if not account_export_dir.exists():
        raise FileNotFoundError(f"Account export dir not found: {account_export_dir}")

    candidates = [
        p for p in account_export_dir.iterdir() if p.is_dir() and p.name.startswith("export_")
    ]
    if not candidates:
        raise FileNotFoundError(f"No export_* folders found in {account_export_dir}")

    def key_fn(path: Path) -> tuple[int, str]:
        match = _NUMERIC_SUFFIX_PATTERN.search(path.name)
        numeric = int(match.group(1)) if match else -1
        return (numeric, path.name)

    return sorted(candidates, key=key_fn)[-1]


def _read_csv_with_normalized_header(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))
    names = normalize_columns(header)
    return pd.read_csv(path, header=0, names=names, dtype=str)


def _col(df: pd.DataFrame, *candidates: str) -> pd.Series:
    for c in candidates:
        if c in df.columns:
            return df[c]
    return pd.Series([None] * len(df), index=df.index, dtype="object")


def _to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _distance_meters(df: pd.DataFrame) -> pd.Series:
    metric_distance = _to_float(_col(df, "distance_2"))
    if metric_distance.notna().any():
        return metric_distance

    # The first Strava `Distance` column is in kilometers.
    # Convert to meters when the metric-distance column is unavailable.
    distance_km = _to_float(_col(df, "distance"))
    return distance_km * 1000.0


def _load_equipment_types(export_dir: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    bikes_file = export_dir / "bikes.csv"
    shoes_file = export_dir / "shoes.csv"

    if bikes_file.exists():
        bikes = _read_csv_with_normalized_header(bikes_file)
        for name in bikes.get("bike_name", pd.Series(dtype="object")).dropna():
            mapping[str(name)] = "bike"

    if shoes_file.exists():
        shoes = _read_csv_with_normalized_header(shoes_file)
        for name in shoes.get("shoe_name", pd.Series(dtype="object")).dropna():
            mapping[str(name)] = "shoe"

    return mapping


def _build_route_summary(df: pd.DataFrame, export_dir: Path) -> pd.DataFrame:
    summaries: list[dict[str, object]] = []
    for _, row in df.iterrows():
        route_file = row.get("route_file")
        if not route_file or not isinstance(route_file, str):
            summary = summarize_route_file(Path(""))
        else:
            summary = summarize_route_file(export_dir / route_file)
        summary["activity_id"] = row.get("activity_id")
        summaries.append(summary)
    return pd.DataFrame(summaries)


def ingest_export(
    export_dir: Path | None = None,
    account_export_dir: Path = DEFAULT_ACCOUNT_EXPORT_DIR,
    parquet_file: Path = DEFAULT_PARQUET_FILE,
    db_file: Path = DEFAULT_DB_FILE,
) -> pd.DataFrame:
    export_dir = export_dir or discover_latest_export_dir(account_export_dir)

    activities = _read_csv_with_normalized_header(export_dir / "activities.csv")

    activity_name = _col(activities, "activity_name")
    activity_type = _col(activities, "activity_type")
    activity_gear = _col(activities, "activity_gear", "gear")
    route_file = _col(activities, "filename")

    data = pd.DataFrame(
        {
            "activity_id": _col(activities, "activity_id"),
            "activity_datetime": pd.to_datetime(
                _col(activities, "activity_date"), errors="coerce", format="%b %d, %Y, %I:%M:%S %p"
            ),
            "activity_name": activity_name,
            "activity_type": activity_type,
            "distance_m": _distance_meters(activities),
            "elapsed_time_s": _to_float(_col(activities, "elapsed_time")),
            "moving_time_s": _to_float(_col(activities, "moving_time")),
            "average_speed_mps": _to_float(_col(activities, "average_speed", "average_speed_2")),
            "elevation_gain_m": _to_float(_col(activities, "elevation_gain")),
            "equipment_name": activity_gear,
            "route_file": route_file,
        }
    )

    parsed = data.apply(
        lambda row: parse_activity_name(row.get("activity_name"), row.get("activity_type")),
        axis=1,
    ).apply(pd.Series)
    data = pd.concat([data, parsed], axis=1)

    equipment_types = _load_equipment_types(export_dir)
    data["equipment_type"] = data["equipment_name"].map(equipment_types).fillna("unknown")

    route_summary = _build_route_summary(data, export_dir)
    data = data.merge(route_summary, on="activity_id", how="left")

    parquet_file.parent.mkdir(parents=True, exist_ok=True)
    data.to_parquet(parquet_file, index=False)
    build_catalog(parquet_file=parquet_file, db_file=db_file)
    return data
