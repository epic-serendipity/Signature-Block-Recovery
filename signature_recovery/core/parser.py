#!/usr/bin/env python3
"""Structured signature parsing utilities."""

# Imports
import re
from typing import Dict, Any

from .models import SignatureMetadata
from .config import load_config
import logging

logger = logging.getLogger(__name__)

# Logging

# Globals
NAME_RE = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)*$")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
TITLE_KEYWORDS = ["Manager", "Engineer", "Director", "Officer", "Consultant"]

# Classes/Functions
class SignatureParser:
    """Parse a signature block into structured metadata."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or load_config()
        self.last_score: float = 0.0
        phone_patterns = self.config.get("parser", {}).get("phone_patterns", [])
        if phone_patterns:
            self.phone_res = [re.compile(p) for p in phone_patterns]
        else:
            self.phone_res = [re.compile(r"(\+?[\d(][\d\s\-\.\(\)]{7,}\d)")]

    def parse(self, text: str) -> SignatureMetadata:
        """Return ``SignatureMetadata`` parsed from ``text``.

        The parser runs several regexes in order of confidence: email, phone,
        URL, name, title, company, and address. Fields not detected are left as
        ``None``.
        """

        logger.debug("Parsing signature text")
        self.last_score = 0.0

        parts = []
        for line in text.splitlines():
            for piece in line.split("|"):
                piece = piece.strip()
                if piece:
                    parts.append(piece)

        lines = parts
        meta = SignatureMetadata()
        fields_found = 0

        # email
        for line in lines:
            m = EMAIL_RE.search(line)
            if m:
                meta.email = m.group(0)
                fields_found += 1
                break

        # phone
        for line in lines:
            for rx in self.phone_res:
                m = rx.search(line)
                if m:
                    meta.phone = m.group(0)
                    fields_found += 1
                    break
            if meta.phone:
                break

        # url
        for line in lines:
            m = URL_RE.search(line)
            if m:
                meta.url = m.group(0)
                fields_found += 1
                break

        # name
        for line in lines:
            if EMAIL_RE.search(line) or any(rx.search(line) for rx in self.phone_res) or URL_RE.search(line):
                continue
            if any(k.lower() in line.lower() for k in TITLE_KEYWORDS):
                continue
            if line.endswith(("Inc", "Inc.", "LLC", "Ltd", "Corp", "Co", "Company")) or line.isupper() or "consult" in line.lower():
                continue
            m = NAME_RE.match(line)
            if m:
                meta.name = m.group(0)
                fields_found += 1
                break

        # title
        for line in lines:
            if any(k.lower() in line.lower() for k in TITLE_KEYWORDS):
                meta.title = line
                fields_found += 1
                break

        # company
        for line in lines:
            if line.endswith(("Inc", "Inc.", "LLC", "Ltd", "Corp", "Co", "Company")) or line.isupper() or "consulting" in line.lower():
                meta.company = line.strip(",")
                fields_found += 1
                break

        # address
        for line in lines:
            if re.search(r"\d+\s+\w+", line) and ("," in line or any(w in line for w in ["St", "Ave", "Rd", "Road", "Blvd"])):
                meta.address = line
                fields_found += 1
                break

        self.last_score = 0.1 * fields_found
        return meta

# main entry

def main() -> None:
    sample = "John Doe\nEngineer\nACME Inc\n555-555-1234\njohn@example.com"
    parser = SignatureParser()
    meta = parser.parse(sample)
    print(meta)

if __name__ == "__main__":
    main()
