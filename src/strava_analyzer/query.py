from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from strava_analyzer.constants import DEFAULT_DB_FILE


def connect(db_file: Path = DEFAULT_DB_FILE) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(db_file))


def filter_activities(
    con: duckdb.DuckDBPyConnection,
    activity_types: list[str] | None = None,
    equipment_names: list[str] | None = None,
    min_distance_m: float | None = None,
    max_distance_m: float | None = None,
    name_category: str | None = None,
) -> pd.DataFrame:
    clauses = ["1=1"]
    params: list[object] = []

    if activity_types:
        placeholders = ",".join("?" for _ in activity_types)
        clauses.append(f"activity_type IN ({placeholders})")
        params.extend(activity_types)

    if equipment_names:
        placeholders = ",".join("?" for _ in equipment_names)
        clauses.append(f"equipment_name IN ({placeholders})")
        params.extend(equipment_names)

    if min_distance_m is not None:
        clauses.append("distance_m >= ?")
        params.append(min_distance_m)

    if max_distance_m is not None:
        clauses.append("distance_m <= ?")
        params.append(max_distance_m)

    if name_category:
        clauses.append("name_category = ?")
        params.append(name_category)

    sql = f"SELECT * FROM activities WHERE {' AND '.join(clauses)} ORDER BY activity_datetime DESC"
    return con.execute(sql, params).fetch_df()


def group_activity_counts(
    con: duckdb.DuckDBPyConnection, by: str = "activity_type"
) -> pd.DataFrame:
    sql = (
        f"SELECT {by}, COUNT(*) AS activity_count "
        f"FROM activities GROUP BY {by} ORDER BY activity_count DESC"
    )
    return con.execute(sql).fetch_df()


def filter_structured_commutes(
    con: duckdb.DuckDBPyConnection,
    year: int | None = None,
    period: str | None = None,
    route_label_key: str | None = None,
) -> pd.DataFrame:
    clauses = ["is_structured_commute = TRUE"]
    params: list[object] = []

    if year is not None:
        clauses.append("EXTRACT(year FROM activity_datetime) = ?")
        params.append(year)

    if period:
        clauses.append("commute_period = ?")
        params.append(period.lower())

    if route_label_key:
        clauses.append("commute_label_key = ?")
        params.append(route_label_key.lower())

    sql = f"SELECT * FROM activities WHERE {' AND '.join(clauses)} ORDER BY activity_datetime"
    return con.execute(sql, params).fetch_df()


def commute_counts_by_year(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    sql = """
    SELECT
      EXTRACT(year FROM activity_datetime)::INTEGER AS year,
      COUNT(*)::INTEGER AS commute_count
    FROM activities
    WHERE is_structured_commute = TRUE
    GROUP BY 1
    ORDER BY 1
    """
    return con.execute(sql).fetch_df()


def commute_speed_by_period(
    con: duckdb.DuckDBPyConnection,
    year: int | None = None,
) -> pd.DataFrame:
    clauses = ["is_structured_commute = TRUE"]
    params: list[object] = []

    if year is not None:
        clauses.append("EXTRACT(year FROM activity_datetime) = ?")
        params.append(year)

    where_sql = " AND ".join(clauses)
    sql = f"""
    SELECT
      commute_period,
      AVG(
        COALESCE(
          average_speed_mps,
          CASE
            WHEN moving_time_s > 0 THEN distance_m / moving_time_s
            ELSE NULL
          END
        )
      ) AS avg_speed_mps,
      COUNT(*)::INTEGER AS commute_count
    FROM activities
    WHERE {where_sql}
    GROUP BY commute_period
    ORDER BY commute_period
    """
    df = con.execute(sql, params).fetch_df()
    if "avg_speed_mps" in df.columns:
        df["avg_speed_kmh"] = df["avg_speed_mps"] * 3.6
    return df


def commute_route_selection(
    con: duckdb.DuckDBPyConnection,
    year: int | None = None,
) -> pd.DataFrame:
    clauses = ["is_structured_commute = TRUE"]
    params: list[object] = []

    if year is not None:
        clauses.append("EXTRACT(year FROM activity_datetime) = ?")
        params.append(year)

    sql = f"""
    SELECT
      COALESCE(commute_label_key, 'unlabeled') AS route_label,
      COUNT(*)::INTEGER AS commute_count
    FROM activities
    WHERE {' AND '.join(clauses)}
    GROUP BY 1
    ORDER BY commute_count DESC, route_label
    """
    return con.execute(sql, params).fetch_df()


def export_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".md":
        path.write_text(df.to_markdown(index=False), encoding="utf-8")
    else:
        df.to_csv(path, index=False)
