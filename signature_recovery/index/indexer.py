#!/usr/bin/env python3
"""Indexing helpers for signature recovery."""

import logging
from typing import Iterable

from ..core.extractor import SignatureExtractor
from ..core.pst_parser import PSTParser, log_message
from .search_index import SearchIndex


def index_pst(pst_path: str, index: SearchIndex) -> None:
    """Extract signatures from ``pst_path`` and add them to ``index``."""
    log_message(logging.INFO, f"Indexing {pst_path}")
    parser = PSTParser(pst_path)
    extractor = SignatureExtractor()
    for msg_id, body in parser.messages():
        sig = extractor.extract_signature(body, msg_id)
        if sig:
            index.add(sig)
