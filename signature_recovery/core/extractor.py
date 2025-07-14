#!/usr/bin/env python3
"""Signature extraction logic."""

import logging
import re
from html.parser import HTMLParser
from typing import List, Optional

from .models import Signature
from .pst_parser import log_message


SIGN_OFF_PATTERNS = [
    r"^--\s*$",
    r"^thanks[,\s]*$",
    r"^regards[,\s]*$",
    r"^best[,\s]*$",
    r"^cheers[,\s]*$",
    r"^sincerely[,\s]*$",
]
MAX_SIGNATURE_LINES = 10


class Stripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fed: List[str] = []

    def handle_data(self, d: str) -> None:
        self.fed.append(d)

    def get_data(self) -> str:
        return "".join(self.fed)


def strip_tags(html: str) -> str:
    stripper = Stripper()
    stripper.feed(html)
    return stripper.get_data()


class Heuristic:
    """Boundary detection heuristic interface."""

    def detect_boundary(self, lines: List[str]) -> Optional[int]:
        raise NotImplementedError


class RegexSignOffHeuristic(Heuristic):
    """Detects signature boundary via regex sign-off patterns."""

    def detect_boundary(self, lines: List[str]) -> Optional[int]:
        for i, line in enumerate(reversed(lines)):
            if any(re.match(p, line.strip(), re.IGNORECASE) for p in SIGN_OFF_PATTERNS):
                return len(lines) - i - 1
        return None


class SignatureExtractor:
    """Extracts signatures from message bodies."""

    heuristics: List[Heuristic] = [RegexSignOffHeuristic()]

    @classmethod
    def register_heuristic(cls, heuristic: Heuristic) -> None:
        cls.heuristics.append(heuristic)

    def extract_signature(
        self, body: str, message_id: str, timestamp: Optional[str] = None
    ) -> Optional[Signature]:
        """Return a signature if detected in ``body``."""
        log_message(logging.DEBUG, "Extracting signature")
        clean_body = strip_tags(body)
        lines = clean_body.strip().split("\n")
        boundary: Optional[int] = None
        for h in self.heuristics:
            boundary = h.detect_boundary(lines)
            if boundary is not None:
                break
        if boundary is None:
            return None

        collected: List[str] = []
        for line in lines[boundary : boundary + MAX_SIGNATURE_LINES]:
            if not line.strip():
                break
            collected.append(line)
        if len([l for l in collected if l.strip()]) < 2:
            return None
        text = "\n".join(collected).strip()
        return Signature(text=text, source_msg_id=message_id, timestamp=timestamp)
