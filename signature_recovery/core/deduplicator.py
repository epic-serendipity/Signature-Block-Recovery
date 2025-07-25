#!/usr/bin/env python3
"""Signature deduplication utilities."""

import logging
import re
import string
from difflib import SequenceMatcher
from typing import Iterable, List

from dataclasses import fields
from .models import Signature, SignatureMetadata
from .pst_parser import log_message


logging.basicConfig(level=logging.INFO)


def _normalize(text: str) -> str:
    """Normalize text for fuzzy comparison."""
    collapsed = re.sub(r"\s+", " ", text)
    stripped = collapsed.translate(str.maketrans('', '', string.punctuation))
    return stripped.strip().lower()


def _similar(a: str, b: str) -> float:
    """Return similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()


def dedupe_signatures(
    signatures: Iterable[Signature], threshold: float = 0.85
) -> List[Signature]:
    """Collapse near-duplicate signatures based on a similarity threshold."""
    sig_list = list(signatures)
    uniques: List[Signature] = []
    norms: List[str] = []
    for sig in sig_list:
        sig_norm = _normalize(sig.text)
        merged = False
        for idx, u in enumerate(uniques):
            ratio = _similar(sig_norm, norms[idx])
            if ratio >= threshold:
                if sig.timestamp and (
                    not u.timestamp or sig.timestamp < u.timestamp
                ):
                    u.timestamp = sig.timestamp
                for f in fields(SignatureMetadata):
                    if getattr(u.metadata, f.name) is None:
                        val = getattr(sig.metadata, f.name)
                        if val is not None:
                            setattr(u.metadata, f.name, val)
                if sig.confidence > u.confidence:
                    u.confidence = sig.confidence
                log_message(
                    logging.INFO,
                    f"Merged signature {sig.source_msg_id} into {u.source_msg_id} (ratio={ratio:.2f})",
                )
                merged = True
                break
        if not merged:
            uniques.append(sig)
            norms.append(sig_norm)
    log_message(logging.INFO, f"Reduced {len(sig_list)} → {len(uniques)} signatures")
    return uniques


def main() -> None:
    """Quick manual test stub."""
    sig1 = Signature(text="John Doe\nEngineer", source_msg_id="1", timestamp="1")
    sig2 = Signature(text="john  doe\nEngineer", source_msg_id="2", timestamp="2")
    uniques = dedupe_signatures([sig1, sig2])
    for u in uniques:
        print(u)


if __name__ == "__main__":
    main()
