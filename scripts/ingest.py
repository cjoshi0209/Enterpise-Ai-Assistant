#!/usr/bin/env python3
"""CLI helper referenced in the README's Quick Start: bulk-ingest a folder of
text files into the assistant via the /ingest endpoint.

Usage:
    python scripts/ingest.py --source ./docs/ --category public --api-url http://localhost:8000
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Folder of .txt/.md files to ingest")
    parser.add_argument("--category", default="public")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--role", default="admin")
    args = parser.parse_args()

    folder = pathlib.Path(args.source)
    if not folder.is_dir():
        print(f"Not a directory: {folder}", file=sys.stderr)
        return 1

    files = [p for p in folder.rglob("*") if p.suffix in (".txt", ".md")]
    if not files:
        print(f"No .txt/.md files found under {folder}")
        return 0

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        resp = requests.post(
            f"{args.api_url}/ingest",
            json={"text": text, "category": args.category, "source": str(path)},
            headers={"x-role": args.role},
            timeout=30,
        )
        status = "ok" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
        print(f"{path}: {status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
