#!/usr/bin/env python3
"""Profile a full extraction run and output HTML stats."""

import pytest

pytestmark = pytest.mark.benchmark

# Imports
import argparse
import cProfile
import pstats
import io
from pathlib import Path
from tempfile import TemporaryDirectory

from template import log_message
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.index.indexer import index_pst

# Logging

# Globals

# Classes/Functions

def _stats_to_html(stats: pstats.Stats) -> str:
    out = io.StringIO()
    stats.stream = out
    stats.sort_stats("cumtime")
    stats.print_stats(50)
    text = out.getvalue()
    html = "<html><body><pre>" + text + "</pre></body></html>"
    return html


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Profile extraction run")
    parser.add_argument("pst", help="Path to PST file")
    parser.add_argument("--output", default="profile.html", help="HTML report path")
    args = parser.parse_args(argv)

    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "idx.db"
        index = SQLiteFTSIndex(str(db))
        profiler = cProfile.Profile()
        profiler.enable()
        index_pst(args.pst, index)
        profiler.disable()
        stats = pstats.Stats(profiler)
        html = _stats_to_html(stats)
        out_path = Path(args.output)
        out_path.write_text(html, encoding="utf-8")
        log_message("info", f"Profile written to {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
