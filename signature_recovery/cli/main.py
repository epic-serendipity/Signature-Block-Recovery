#!/usr/bin/env python3
"""Command-line interface for signature recovery."""

# Imports
import argparse
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List

from template import log_message
from .. import __version__

from ..core.extractor import SignatureExtractor
from ..core.deduplicator import dedupe_signatures
from ..core.metrics import MetricsCollector, MessageMetric
from ..core.models import Message, Signature
from ..core.pst_parser import PSTParser
from ..exporter import export_to_csv, export_to_json, export_to_excel
from ..index.indexer import add_batch
from ..index.search_index import SQLiteFTSIndex

# Logging

# Globals

# Classes/Functions

def _build_parser() -> argparse.ArgumentParser:
    """Return the top-level argument parser."""
    parser = argparse.ArgumentParser(description="Recover signatures from data")
    parser.add_argument("--threads", "-t", type=int, default=1, help="Worker threads for extraction")
    parser.add_argument("--batch-size", type=int, default=1000, help="Messages per commit")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum confidence to keep a signature")
    parser.add_argument("--metrics", action="store_true", help="Print timing statistics")
    parser.add_argument("--dump-metrics", help="Write aggregated metrics to JSON file")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase logging verbosity")
    parser.add_argument(
        "--version",
        action="version",
        version=f"recover-signatures {__version__}",
        help="Show program version and exit",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ex = sub.add_parser("extract", help="Index signatures from a PST file")
    ex.add_argument("--input", required=True, help="Path to PST file")
    ex.add_argument("--index", required=True, help="Path to SQLite FTS index")
    ex.set_defaults(func=handle_extract)

    q = sub.add_parser("query", help="Search an existing index")
    q.add_argument("--index", required=True, help="Path to SQLite FTS index")
    q.add_argument("--q", required=True, help="Search query")
    q.add_argument("--page", type=int, default=1, help="Page number")
    q.add_argument("--size", type=int, default=10, help="Results per page")
    q.add_argument("--verbose", action="store_true", help="Show metadata columns")
    q.set_defaults(func=handle_query)

    exp = sub.add_parser("export", help="Export signatures from an index")
    exp.add_argument("--index", required=True, help="Path to SQLite FTS index")
    exp.add_argument("--format", choices=["csv", "json", "excel"], required=True, help="Output format")
    exp.add_argument("--out", required=True, help="Output file path")
    exp.add_argument("--q", help="Optional search query filter")
    exp.add_argument("--date-from", type=float, help="Start timestamp filter")
    exp.add_argument("--date-to", type=float, help="End timestamp filter")
    exp.set_defaults(func=handle_export)

    return parser


def _configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def handle_extract(args: argparse.Namespace) -> int:
    """Extract signatures from ``args.input`` and index them.

    Returns
    -------
    int
        ``0`` on success, ``1`` on user error.
    """
    try:
        parser = PSTParser(args.input)
    except Exception as exc:  # File not found or pypff issues
        log_message(logging.ERROR, str(exc))
        return 1

    extractor = SignatureExtractor()
    indexer = SQLiteFTSIndex(args.index)
    metrics = MetricsCollector()
    start = time.time()
    batch: List[Signature] = []

    def worker(msg: Message) -> Signature | None:
        start_ts = time.time()
        try:
            sig = extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
        except Exception as e:  # pragma: no cover - unexpected parse errors
            log_message(logging.ERROR, f"Failed to process message {msg.msg_id}")
            logging.exception("worker error")
            metrics.record(
                MessageMetric(msg_id=msg.msg_id, extracted=False, confidence=0.0, time_ms=0.0)
            )
            return None
        duration_ms = (time.time() - start_ts) * 1000
        metrics.record(
            MessageMetric(
                msg_id=msg.msg_id,
                extracted=sig is not None,
                confidence=sig.confidence if sig else 0.0,
                time_ms=duration_ms,
            )
        )
        return sig

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        for sig in pool.map(worker, parser.iter_messages()):
            if sig and sig.confidence >= args.min_confidence:
                batch.append(sig)
            if len(batch) >= args.batch_size:
                uniques = dedupe_signatures(batch)
                add_batch(indexer, uniques)
                log_message(logging.INFO, f"Committed {len(uniques)} signatures")
                batch.clear()

    if batch:
        uniques = dedupe_signatures(batch)
        add_batch(indexer, uniques)
        log_message(logging.INFO, f"Committed {len(uniques)} signatures")

    elapsed = time.time() - start
    summary = metrics.summarize()
    if args.metrics:
        msg_rate = summary["total_messages"] / elapsed if elapsed else 0
        sig_rate = summary["signatures_extracted"] / elapsed if elapsed else 0
        print(
            f"Processed {summary['total_messages']} messages in {elapsed:.2f} seconds ({msg_rate:.0f} msg/sec)"
        )
        print(
            f"Extracted {summary['signatures_extracted']} signatures ({sig_rate:.0f} sig/sec), avg conf {summary['average_confidence']:.2f}"
        )
    if args.dump_metrics:
        metrics.dump(args.dump_metrics)
    return 0


def handle_query(args: argparse.Namespace) -> int:
    """Query the index and print matching signatures.

    Returns
    -------
    int
        ``0`` on success, ``1`` if the index is missing.
    """
    if not os.path.exists(args.index):
        log_message(logging.ERROR, f"Index not found: {args.index}")
        return 1
    indexer = SQLiteFTSIndex(args.index)
    q_raw = args.q.strip()
    q = None if (q_raw == "*" or q_raw == "") else q_raw
    results = indexer.query(q, min_confidence=args.min_confidence)
    start = (args.page - 1) * args.size
    for sig in results[start : start + args.size]:
        if args.verbose:
            print(
                f"{sig.source_msg_id}\t{sig.timestamp}\t{sig.confidence:.2f}\t{sig.text}",
                flush=True,
            )
        else:
            print(sig.text, flush=True)
    return 0


def handle_export(args: argparse.Namespace) -> int:
    """Export signatures from ``args.index`` to ``args.out``.

    Returns
    -------
    int
        ``0`` on success, ``1`` if the index is missing.
    """
    if not os.path.exists(args.index):
        log_message(logging.ERROR, f"Index not found: {args.index}")
        return 1
    indexer = SQLiteFTSIndex(args.index)
    q_raw = (args.q or "").strip()
    q = None if (q_raw == "*" or q_raw == "") else q_raw
    results = indexer.query(q, min_confidence=args.min_confidence)
    if args.date_from:
        results = [s for s in results if float(s.timestamp or 0) >= args.date_from]
    if args.date_to:
        results = [s for s in results if float(s.timestamp or 0) <= args.date_to]
    fmt = args.format
    if fmt == "csv":
        export_to_csv(results, args.out)
    elif fmt == "json":
        export_to_json(results, args.out)
    else:
        export_to_excel(results, args.out)
    return 0


# main

def main(argv: Iterable[str] | None = None) -> None:
    """Entry point for the ``recover-signatures`` command.

    Returns exit code ``0`` on success, ``1`` for user errors and ``2`` for
    unexpected internal errors.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse errors
        sys.exit(1 if exc.code != 0 else 0)
    _configure_logging(args.verbose)
    try:
        code = args.func(args)
    except Exception as exc:  # pragma: no cover - defensive
        log_message(logging.ERROR, str(exc))
        logging.exception("cli error")
        code = 2
    sys.exit(code)


if __name__ == "__main__":  # pragma: no cover - manual use
    main()

