#!/usr/bin/env python3
"""Command-line interface for signature recovery."""

import argparse

from ..index.indexer import index_pst
from ..index.search_index import SQLiteFTSIndex


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover signatures from a PST")
    parser.add_argument("--input", required=True, help="Path to PST file")
    parser.add_argument("--output", required=True, help="SQLite index path")
    args = parser.parse_args()

    index = SQLiteFTSIndex(args.output)
    index_pst(args.input, index)


if __name__ == "__main__":
    main()
