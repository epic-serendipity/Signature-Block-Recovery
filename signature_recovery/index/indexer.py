#!/usr/bin/env python3
"""Indexing helpers for signature recovery."""

import logging
from typing import Iterable

from ..core.extractor import SignatureExtractor
from ..core.pst_parser import PSTParser
from template import log_message
from ..core.models import Signature
from .search_index import SearchIndex


def add_batch(index: SearchIndex, signatures: Iterable[Signature]) -> None:
    """Add a batch of signatures to the index."""
    index.add_batch(signatures)


def index_pst(pst_path: str, index: SearchIndex) -> None:
    """Extract signatures from ``pst_path`` and add them to ``index``."""
    log_message(logging.INFO, f"Indexing {pst_path}")
    parser = PSTParser(pst_path)
    extractor = SignatureExtractor()
    for msg in parser.iter_messages():
        try:
            sig = extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
            if sig:
                index.add(sig)
        except Exception as exc:  # pragma: no cover - defensive
            log_message(
                logging.ERROR,
                f"indexing failed: {exc}",
                component="indexer",
                msg_id=msg.msg_id,
            )
