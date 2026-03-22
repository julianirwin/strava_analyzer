from __future__ import annotations

import argparse
from pathlib import Path

from strava_analyzer.catalog import build_catalog
from strava_analyzer.constants import DEFAULT_DB_FILE, DEFAULT_PARQUET_FILE
from strava_analyzer.context_export import export_context
from strava_analyzer.ingest import ingest_export


def _cmd_ingest(args: argparse.Namespace) -> None:
    export_dir = Path(args.export_dir) if args.export_dir else None
    df = ingest_export(export_dir=export_dir)
    print(f"Ingested {len(df)} activities")


def _cmd_build_catalog(_: argparse.Namespace) -> None:
    build_catalog(DEFAULT_PARQUET_FILE, DEFAULT_DB_FILE)
    print(f"Catalog built at {DEFAULT_DB_FILE}")


def _cmd_export_context(_: argparse.Namespace) -> None:
    summary_md, extract_csv = export_context()
    print(f"Wrote {summary_md}")
    print(f"Wrote {extract_csv}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="strava-analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Ingest latest or specified Strava export")
    ingest.add_argument("--export-dir", type=str, default=None, help="Path to export_* folder")
    ingest.set_defaults(func=_cmd_ingest)

    build = sub.add_parser("build-catalog", help="Build catalog DB from parquet")
    build.set_defaults(func=_cmd_build_catalog)

    context = sub.add_parser("export-context", help="Export privacy-safe LLM context artifacts")
    context.set_defaults(func=_cmd_export_context)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
