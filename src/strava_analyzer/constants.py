from pathlib import Path

ROOT_DIR = Path.cwd()
DEFAULT_ACCOUNT_EXPORT_DIR = ROOT_DIR / "account_export"
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_PARQUET_DIR = DEFAULT_DATA_DIR / "parquet"
DEFAULT_PARQUET_FILE = DEFAULT_PARQUET_DIR / "activities.parquet"
DEFAULT_DB_FILE = DEFAULT_DATA_DIR / "catalog.duckdb"
DEFAULT_LLM_CONTEXT_DIR = ROOT_DIR / "llm_context"
