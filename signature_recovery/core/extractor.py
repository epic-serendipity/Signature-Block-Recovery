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

    def _normalize_body(self, body: str) -> str:
        """Return plain text with collapsed whitespace and consistent breaks."""
        text = body.replace("\r\n", "\n").replace("\r", "\n")
        if re.search(r"<[^>]+>", text, re.IGNORECASE):
            text = re.sub(r"(?i)<br\s*/?>", "\n", text)
            text = re.sub(r"(?i)</p>", "\n", text)
            text = re.sub(r"(?i)</div>", "\n", text)
            text = strip_tags(text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r" ?\n ?", "\n", text)
        return text.strip()

    def _html_boundary_hint(self, raw_body: str) -> Optional[int]:
        """Return boundary index if HTML contains explicit signature markers."""
        match = re.search(r"<hr\b|<div\s+class=\"signature\"", raw_body, re.IGNORECASE)
        if not match:
            return None
        before = raw_body[: match.start()]
        normalized_before = self._normalize_body(before)
        if not normalized_before:
            return 0
        return len(normalized_before.split("\n"))

    @classmethod
    def register_heuristic(cls, heuristic: Heuristic) -> None:
        cls.heuristics.append(heuristic)

    def extract_signature(
        self, body: str, message_id: str, timestamp: Optional[str] = None
    ) -> Optional[Signature]:
        """Return a signature if detected in ``body``."""
        log_message(logging.DEBUG, "Extracting signature")
        clean_body = self._normalize_body(body)
        lines = clean_body.split("\n") if clean_body else []
        boundary: Optional[int] = None
        for h in self.heuristics:
            boundary = h.detect_boundary(lines)
            if boundary is not None:
                break
        if boundary is None:
            boundary = self._html_boundary_hint(body)
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
