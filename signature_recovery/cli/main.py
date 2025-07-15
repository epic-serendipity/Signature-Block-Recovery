#!/usr/bin/env python3
"""Command-line interface for signature recovery."""

import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from ..core.extractor import SignatureExtractor
from ..core.pst_parser import PSTParser
from ..core.models import Message, Signature
from ..index.indexer import add_batch
from ..index.search_index import SQLiteFTSIndex
from template import log_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover signatures from a PST")
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="Index signatures from a PST")
    extract.add_argument("--input", required=True, help="Path to PST file")
    extract.add_argument("--output", required=True, dest="index_db", help="Path to SQLite FTS index")
    extract.add_argument("--threads", type=int, default=1, help="Number of worker threads")
    extract.add_argument("--batch-size", type=int, default=1000, help="Messages per commit")
    extract.add_argument("--metrics", action="store_true", help="Print timing statistics")
    extract.add_argument("-v", "--verbose", action="count", default=0, help="Increase logging verbosity")

    query_p = sub.add_parser("query", help="Search an existing index")
    query_p.add_argument("--index", required=True, help="Path to SQLite FTS index")
    query_p.add_argument("--q", required=True, help="Search query")
    query_p.add_argument("-v", "--verbose", action="count", default=0, help="Increase logging verbosity")

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

        start = time.time()
        total_messages = 0
        total_signatures = 0
        batch: List[Signature] = []

        def worker(msg: Message) -> Signature | None:
            try:
                return extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
            except Exception:
                log_message(logging.ERROR, f"Failed to process message {msg.msg_id}")
                logging.exception("worker error")
                return None

        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            for sig in pool.map(worker, parser_obj.iter_messages()):
                total_messages += 1
                if sig:
                    batch.append(sig)
                    total_signatures += 1
                if len(batch) >= args.batch_size:
                    add_batch(indexer, batch)
                    log_message(logging.INFO, f"Committed {len(batch)} signatures")
                    batch.clear()

        if batch:
            add_batch(indexer, batch)
            log_message(logging.INFO, f"Committed {len(batch)} signatures")

        elapsed = time.time() - start
        if args.metrics:
            msg_rate = total_messages / elapsed if elapsed else 0
            sig_rate = total_signatures / elapsed if elapsed else 0
            print(
                f"Processed {total_messages} messages in {elapsed:.2f} seconds ({msg_rate:.0f} msg/sec)"
            )
            print(f"Extracted {total_signatures} signatures ({sig_rate:.0f} sig/sec)")
    elif args.command == "query":
        indexer = SQLiteFTSIndex(args.index)
        results = indexer.query(args.q)
        for sig in results:
            if args.verbose:
                print(f"{sig.source_msg_id}\t{sig.timestamp}\t{sig.text}")
            else:
                print(sig.text)


if __name__ == "__main__":
    main()
