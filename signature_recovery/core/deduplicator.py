#!/usr/bin/env python3
"""Signature deduplication utilities."""

import logging
from difflib import SequenceMatcher
from typing import Iterable, List

from .models import Signature
from .pst_parser import log_message


class SignatureDeduplicator:
    """Collapse duplicate signatures using fuzzy matching."""

    def __init__(self, threshold: float = 0.9) -> None:
        self.threshold = threshold

    def _similar(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def dedupe(self, signatures: Iterable[Signature]) -> List[Signature]:
        log_message(logging.DEBUG, "Deduplicating signatures")
        uniques: List[Signature] = []
        for sig in signatures:
            if not any(
                self._similar(sig.normalized_text, u.normalized_text) >= self.threshold
                for u in uniques
            ):
                uniques.append(sig)
        return uniques
