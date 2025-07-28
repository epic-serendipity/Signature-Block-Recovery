#!/usr/bin/env python3
"""Indexing helpers for signature recovery."""

import logging
from typing import Iterable

from ..core.extractor import SignatureExtractor
from ..core.pst_parser import PSTParser
logger = logging.getLogger(__name__)
from ..core.models import Signature
from .search_index import SearchIndex


def add_batch(index: SearchIndex, signatures: Iterable[Signature]) -> None:
    """Add a batch of signatures to the index."""
    index.add_batch(signatures)


def index_pst(pst_path: str, index: SearchIndex) -> None:
    """Extract signatures from ``pst_path`` and add them to ``index``."""
    logger.info("Indexing %s", pst_path)
    parser = PSTParser(pst_path)
    extractor = SignatureExtractor()
    for msg in parser.iter_messages():
        try:
            sig = extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
            if sig:
                index.add(sig)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(
                "indexing failed: %s",
                exc,
                extra={"component": "indexer", "msg_id": msg.msg_id},
            )
