#!/usr/bin/env python3
"""Signature extraction logic."""

import logging
import re
import time
from typing import List, Optional, Tuple, Iterable, Dict, Any

from html import unescape

from .models import Signature
from .parser import SignatureParser
from .config import load_config
from template import log_message


MAX_SIGNATURE_LINES = 10




class Heuristic:
    """Boundary detection heuristic interface."""

    confidence: float = 0.0

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[Tuple[int, float]]:
        raise NotImplementedError


class RegexSignOffHeuristic(Heuristic):
    """Detects signature boundary via regex sign-off patterns."""

    def __init__(self, patterns: Iterable[str]) -> None:
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.confidence = 0.9

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[Tuple[int, float]]:
        for i, line in enumerate(reversed(lines)):
            if any(p.search(line.strip()) for p in self.patterns):
                return len(lines) - i - 1, self.confidence
        return None


class HtmlDividerHeuristic(Heuristic):
    """Detects boundaries indicated by <hr> or signature divs in HTML."""

    def __init__(self) -> None:
        self.confidence = 0.7

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[Tuple[int, float]]:
        match = re.search(r'<hr\b|<div\s+class=\"signature\"', raw_body, re.IGNORECASE)
        if not match:
            return None
        before = raw_body[: match.start()]
        normalized_before = SignatureExtractor()._normalize_body(before)
        if not normalized_before:
            return 0, self.confidence
        return len(normalized_before.split("\n")), self.confidence


class TrailingLinesHeuristic(Heuristic):
    """Fallback heuristic returning start of last N non-blank lines."""

    def __init__(self, max_lines: int) -> None:
        self.max_lines = max_lines
        self.confidence = 0.5

    def detect_boundary(self, lines: List[str], raw_body: str) -> Optional[Tuple[int, float]]:
        non_blank = [i for i, l in enumerate(lines) if l.strip()]
        if not non_blank:
            return None
        start = non_blank[-self.max_lines] if len(non_blank) >= self.max_lines else non_blank[0]
        return start, self.confidence


class SignatureExtractor:
    """Extracts signatures from message bodies."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or load_config()
        patterns = self.config.get("extraction", {}).get("signoff_patterns", [])
        max_lines = self.config.get("extraction", {}).get("max_fallback_lines", 5)
        self.heuristics: List[Heuristic] = [
            RegexSignOffHeuristic(patterns),
            HtmlDividerHeuristic(),
            TrailingLinesHeuristic(max_lines),
        ]

    def _normalize_body(self, body: str) -> str:
        """Strip HTML tags and collapse whitespace into normalized plain text."""
        from html.parser import HTMLParser

        class _Stripper(HTMLParser):
            def __init__(self):
                super().__init__()
                self._parts: List[str] = []
                self._skip = False

            def handle_starttag(self, tag: str, attrs):
                t = tag.lower()
                if t in {"br", "p", "div", "li", "tr"}:
                    self._parts.append("\n")
                if t in {"style", "script"}:
                    self._skip = True

            def handle_startendtag(self, tag: str, attrs):
                self.handle_starttag(tag, attrs)

            def handle_endtag(self, tag: str) -> None:
                t = tag.lower()
                if t in {"style", "script"}:
                    self._skip = False
                if t in {"p", "div", "li", "tr"}:
                    self._parts.append("\n")

            def handle_data(self, data: str):
                if not self._skip:
                    self._parts.append(data)

            def handle_entityref(self, name: str) -> None:
                self._parts.append(unescape(f"&{name};"))

            def handle_charref(self, name: str) -> None:
                self._parts.append(unescape(f"&#{name};"))

            def get_data(self) -> str:
                return "".join(self._parts)

        try:
            if '<html' in body.lower() or '<body' in body.lower():
                stripper = _Stripper()
                stripper.feed(body)
                text = stripper.get_data()
            else:
                text = body
        except Exception as exc:  # pragma: no cover - defensive
            log_message(
                logging.WARNING,
                f"html parse error: {exc}",
                component="extractor",
            )
            text = body

        collapsed = re.sub(r'[ \t]+', ' ', text)
        collapsed = re.sub(r'\r\n?', '\n', collapsed)
        collapsed = re.sub(r'\n+', '\n', collapsed).strip()
        return '\n'.join(line.strip() for line in collapsed.splitlines() if line.strip())



    def extract_from_body(self, body: str) -> Optional[Signature]:
        """Convenience wrapper when message metadata is not needed."""
        return self.extract_signature(body, "")

    def extract_signature(
        self, body: str, message_id: str, timestamp: Optional[str] = None
    ) -> Optional[Signature]:
        """Return a signature if detected in ``body``."""
        start_ts = time.time()
        log_message(logging.DEBUG, "Extracting signature", component="extractor")
        raw_body = body
        clean_body = self._normalize_body(body)
        lines = clean_body.split("\n") if clean_body else []
        boundary: Optional[int] = None
        base_conf = 0.0
        for h in self.heuristics:
            try:
                result = h.detect_boundary(lines, raw_body)
            except Exception as exc:  # pragma: no cover - defensive
                log_message(
                    logging.WARNING,
                    f"heuristic error: {exc}",
                    component="extractor",
                    msg_id=message_id,
                    heuristic_used=h.__class__.__name__,
                )
                continue
            if result is not None:
                boundary, base_conf = result
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
        parser = SignatureParser(self.config)
        meta = parser.parse(text)
        conf = base_conf
        if not (meta.email or meta.phone or meta.name):
            conf = min(conf, 0.5)
        if meta.email:
            conf += 0.05
        if meta.phone:
            conf += 0.05
        if meta.name:
            conf += 0.05
        confidence = min(conf, 1.0)
        sig = Signature(
            text=text,
            source_msg_id=message_id,
            timestamp=timestamp,
            metadata=meta,
            confidence=confidence,
        )
        duration_ms = (time.time() - start_ts) * 1000
        log_message(
            logging.INFO,
            "extracted signature",
            component="extractor",
            msg_id=message_id,
            duration_ms=round(duration_ms, 2),
            confidence=confidence,
        )
        return sig

