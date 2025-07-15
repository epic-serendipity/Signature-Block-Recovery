#!/usr/bin/env python3
"""Signature extraction logic."""

import logging
import re
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




class Heuristic:
    """Boundary detection heuristic interface."""

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[int]:
        raise NotImplementedError


class RegexSignOffHeuristic(Heuristic):
    """Detects signature boundary via regex sign-off patterns."""

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[int]:
        for i, line in enumerate(reversed(lines)):
            if any(re.match(p, line.strip(), re.IGNORECASE) for p in SIGN_OFF_PATTERNS):
                return len(lines) - i - 1
        return None


class HtmlDividerHeuristic(Heuristic):
    """Detects boundaries indicated by <hr> or signature divs in HTML."""

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[int]:
        match = re.search(r'<hr\b|<div\s+class=\"signature\"', raw_body, re.IGNORECASE)
        if not match:
            return None
        before = raw_body[: match.start()]
        normalized_before = SignatureExtractor()._normalize_body(before)
        if not normalized_before:
            return 0
        return len(normalized_before.split("\n"))


class SignatureExtractor:
    """Extracts signatures from message bodies."""

    heuristics: List[Heuristic] = [RegexSignOffHeuristic()]

    def _normalize_body(self, body: str) -> str:
        """Strip HTML tags and collapse whitespace into normalized plain text."""
        from html.parser import HTMLParser

        class _Stripper(HTMLParser):
            def __init__(self):
                super().__init__()
                self._parts: List[str] = []

            def handle_starttag(self, tag: str, attrs):
                if tag.lower() in {"br", "p", "div"}:
                    self._parts.append("\n")

            def handle_data(self, data: str):
                self._parts.append(data)

            def get_data(self) -> str:
                return ''.join(self._parts)

        if '<html' in body.lower() or '<body' in body.lower():
            stripper = _Stripper()
            stripper.feed(body)
            text = stripper.get_data()
        else:
            text = body

        collapsed = re.sub(r'[ \t]+', ' ', text)
        collapsed = re.sub(r'\r\n?', '\n', collapsed)
        collapsed = re.sub(r'\n+', '\n', collapsed).strip()
        return '\n'.join(line.strip() for line in collapsed.splitlines() if line.strip())


    @classmethod
    def register_heuristic(cls, heuristic: Heuristic) -> None:
        cls.heuristics.append(heuristic)

    def extract_from_body(self, body: str) -> Optional[Signature]:
        """Convenience wrapper when message metadata is not needed."""
        return self.extract_signature(body, "")

    def extract_signature(
        self, body: str, message_id: str, timestamp: Optional[str] = None
    ) -> Optional[Signature]:
        """Return a signature if detected in ``body``."""
        log_message(logging.DEBUG, "Extracting signature")
        raw_body = body
        clean_body = self._normalize_body(body)
        lines = clean_body.split("\n") if clean_body else []
        boundary: Optional[int] = None
        for h in self.heuristics:
            boundary = h.detect_boundary(lines, raw_body)
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


# register HTML divider heuristic
SignatureExtractor.register_heuristic(HtmlDividerHeuristic())
