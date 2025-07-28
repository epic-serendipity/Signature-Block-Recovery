#!/usr/bin/env python3
"""Benchmark extraction and indexing throughput."""

import pytest

pytestmark = pytest.mark.benchmark

# Imports
import argparse
import csv
import logging
import time
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor

from template import log_message
from signature_recovery.core.extractor import SignatureExtractor
from signature_recovery.core.models import Message, Signature
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.index.indexer import add_batch

# Logging

# Globals

# Classes/Functions

def _dummy_messages(n: int):
    for i in range(n):
        yield Message(body="dummy", msg_id=str(i), timestamp=float(i))


def _run_once(num_messages: int, threads: int, batch_size: int) -> float:
    extractor = SignatureExtractor()
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "idx.db"
        index = SQLiteFTSIndex(str(db))
        start = time.time()
        batch = []
        total = 0
        def worker(msg: Message) -> Signature | None:
            try:
                return extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
            except Exception:
                logging.exception("extract error")
                return None
        with ThreadPoolExecutor(max_workers=threads) as pool:
            for sig in pool.map(worker, _dummy_messages(num_messages)):
                if sig:
                    batch.append(sig)
                total += 1
                if len(batch) >= batch_size:
                    add_batch(index, batch)
                    batch.clear()
        if batch:
            add_batch(index, batch)
        elapsed = time.time() - start
        return total / elapsed if elapsed else 0.0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run extraction benchmark")
    parser.add_argument("--out", default="benchmark_large_pst.csv", help="CSV output path")
    parser.add_argument("--messages", type=int, default=1000, help="Number of dummy messages")
    parser.add_argument("--threads", nargs="*", type=int, default=[1, 2])
    parser.add_argument("--batch-size", nargs="*", type=int, default=[100])
    args = parser.parse_args(argv)

    results = []
    for t, b in product(args.threads, args.batch_size):
        log_message("info", f"Running threads={t} batch={b}")
        rate = _run_once(args.messages, t, b)
        results.append({"threads": t, "batch_size": b, "msgs_per_sec": rate})

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["threads", "batch_size", "msgs_per_sec"])
        writer.writeheader()
        writer.writerows(results)
    log_message("info", f"Results written to {args.out}")


if __name__ == "__main__":  # pragma: no cover
    main()
