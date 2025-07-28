#!/usr/bin/env python3
"""Measure SQLite index size growth."""

import pytest

pytestmark = pytest.mark.benchmark

# Imports
import argparse
import csv
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from template import log_message
from signature_recovery.core.models import Signature
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.index.indexer import add_batch

# Logging

# Globals

# Classes/Functions

def _make_signatures(n: int):
    for i in range(n):
        yield Signature(text=f"Sig {i}", source_msg_id=str(i), timestamp=str(i))


def _measure(n: int) -> int:
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "idx.db"
        index = SQLiteFTSIndex(str(db))
        add_batch(index, _make_signatures(n))
        index.conn.close()
        return os.path.getsize(db)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Benchmark index size growth")
    parser.add_argument("--out", default="index_growth.csv", help="CSV output path")
    parser.add_argument("--counts", nargs="*", type=int, default=[1000, 10000, 100000])
    args = parser.parse_args(argv)

    rows = []
    for count in args.counts:
        log_message("info", f"Indexing {count} signatures")
        size = _measure(count)
        rows.append({"signatures": count, "bytes": size})

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["signatures", "bytes"])
        writer.writeheader()
        writer.writerows(rows)
    log_message("info", f"Results written to {args.out}")


if __name__ == "__main__":  # pragma: no cover
    main()
