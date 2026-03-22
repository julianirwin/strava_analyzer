from __future__ import annotations

from pathlib import Path

import duckdb


def build_catalog(parquet_file: Path, db_file: Path) -> None:
    db_file.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_file))
    try:
        con.execute("DROP TABLE IF EXISTS activities")
        con.execute(
            "CREATE TABLE activities AS SELECT * FROM read_parquet(?)",
            [str(parquet_file)],
        )
    finally:
        con.close()
