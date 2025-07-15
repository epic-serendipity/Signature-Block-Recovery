#!/usr/bin/env python3
"""Command-line interface for signature recovery."""

import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from ..core.extractor import SignatureExtractor
from ..core.pst_parser import PSTParser
from ..core.metrics import Metrics
from ..core.models import Message, Signature
from ..index.indexer import add_batch
from ..exporter import export_to_csv, export_to_json, export_to_excel
from ..index.search_index import SQLiteFTSIndex
from template import log_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover signatures from a PST")
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=1,
        help="Number of worker threads for extraction",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="Index signatures from a PST")
    extract.add_argument("--input", required=True, help="Path to PST file")
    extract.add_argument("--output", required=True, dest="index_db", help="Path to SQLite FTS index")
    extract.add_argument("--batch-size", type=int, default=1000, help="Messages per commit")
    extract.add_argument("--metrics", action="store_true", help="Print timing statistics")
    extract.add_argument("--min-confidence", type=float, default=0.0, help="Minimum confidence to keep a signature")
    extract.add_argument("--dump-metrics", help="Write aggregated metrics to JSON file")
    extract.add_argument("-v", "--verbose", action="count", default=0, help="Increase logging verbosity")

    query_p = sub.add_parser("query", help="Search an existing index")
    query_p.add_argument("--index", required=True, help="Path to SQLite FTS index")
    query_p.add_argument("--q", required=True, help="Search query")
    query_p.add_argument("-v", "--verbose", action="count", default=0, help="Increase logging verbosity")

    export_p = sub.add_parser("export", help="Export signatures from an index")
    export_p.add_argument("--index", required=True, help="Path to SQLite FTS index")
    export_p.add_argument("--format", choices=["csv", "json", "excel"], required=True)
    export_p.add_argument("--out", required=True, help="Output file path")

    args = parser.parse_args()

    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    if args.command == "extract":
        parser_obj = PSTParser(args.input)
        extractor = SignatureExtractor()
        indexer = SQLiteFTSIndex(args.index_db)
        metrics = Metrics()

        start = time.time()
        batch: List[Signature] = []

        def worker(msg: Message) -> Signature | None:
            begin = time.time()
            try:
                sig = extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
            except Exception:
                log_message(logging.ERROR, f"Failed to process message {msg.msg_id}")
                logging.exception("worker error")
                metrics.record(msg.msg_id, False, 0.0, len(msg.body.splitlines()), 0.0)
                return None
            elapsed_ms = (time.time() - begin) * 1000
            metrics.record(
                msg.msg_id,
                sig is not None,
                sig.confidence if sig else 0.0,
                len(msg.body.splitlines()),
                elapsed_ms,
            )
            return sig

        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            for sig in pool.map(worker, parser_obj.iter_messages()):
                if sig and sig.confidence >= args.min_confidence:
                    batch.append(sig)
                if len(batch) >= args.batch_size:
                    add_batch(indexer, batch)
                    log_message(logging.INFO, f"Committed {len(batch)} signatures")
                    batch.clear()

        if batch:
            add_batch(indexer, batch)
            log_message(logging.INFO, f"Committed {len(batch)} signatures")

        elapsed = time.time() - start
        summary = metrics.summary()
        if args.metrics:
            msg_rate = summary["messages"] / elapsed if elapsed else 0
            sig_rate = summary["signatures_found"] / elapsed if elapsed else 0
            print(
                f"Processed {summary['messages']} messages in {elapsed:.2f} seconds ({msg_rate:.0f} msg/sec)"
            )
            print(
                f"Extracted {summary['signatures_found']} signatures ({sig_rate:.0f} sig/sec), avg conf {summary['avg_confidence']:.2f}"
            )
        if args.dump_metrics:
            import json

            with open(args.dump_metrics, "w", encoding="utf-8") as fh:
                json.dump(summary, fh, indent=2)
    elif args.command == "query":
        indexer = SQLiteFTSIndex(args.index)
        results = indexer.query(args.q)
        for sig in results:
            if args.verbose:
                print(f"{sig.source_msg_id}\t{sig.timestamp}\t{sig.text}")
            else:
                print(sig.text)
    elif args.command == "export":
        indexer = SQLiteFTSIndex(args.index)
        results = indexer.query("*")
        fmt = args.format
        if fmt == "csv":
            export_to_csv(results, args.out)
        elif fmt == "json":
            export_to_json(results, args.out)
        else:
            export_to_excel(results, args.out)


if __name__ == "__main__":
    main()
