#!/usr/bin/env python3
"""Structured signature parsing utilities."""

# Imports
import re

from .models import SignatureMetadata
from template import log_message

# Logging

# Globals
NAME_RE = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)*$")
PHONE_RE = re.compile(r"(\+?[\d(][\d\s\-\.\(\)]{7,}\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
TITLE_KEYWORDS = ["Manager", "Engineer", "Director", "Officer", "Consultant"]

# Classes/Functions
class SignatureParser:
    """Parse a signature block into structured metadata."""

    def parse(self, text: str) -> SignatureMetadata:
        parts = []
        for l in text.splitlines():
            for p in l.split("|"):
                p = p.strip()
                if p:
                    parts.append(p)
        lines = parts
        meta = SignatureMetadata()
        for line in lines:
            if not meta.email:
                m = EMAIL_RE.search(line)
                if m:
                    meta.email = m.group(0)
                    continue
            if not meta.phone:
                m = PHONE_RE.search(line)
                if m:
                    meta.phone = m.group(0)
            if not meta.url:
                m = URL_RE.search(line)
                if m:
                    meta.url = m.group(0)
        for line in reversed(lines):
            if any(c.isdigit() for c in line) or "@" in line or "www" in line or "http" in line:
                continue
            if any(k.lower() in line.lower() for k in TITLE_KEYWORDS):
                continue
            if line.endswith(("Inc", "Inc.", "LLC", "Ltd", "Corp", "Co")) or line.isupper() or "consulting" in line.lower():
                continue
            if line.lower() == "title":
                continue
            m = NAME_RE.search(line)
            if m:
                meta.name = m.group(0)
                break
        for line in lines:
            if any(k.lower() in line.lower() for k in TITLE_KEYWORDS):
                meta.title = line
                break
        for line in lines:
            if line.endswith(("Inc", "Inc.", "LLC", "Ltd", "Corp", "Co", "Company")) or line.isupper() or "Consulting" in line:
                meta.company = line.strip(',')
                break
        for line in lines:
            if re.search(r"\d+\s+\w+", line) and ("," in line or "St" in line or "Ave" in line):
                meta.address = line
                break
        return meta

# main entry

def main() -> None:
    sample = "John Doe\nEngineer\nACME Inc\n555-555-1234\njohn@example.com"
    parser = SignatureParser()
    meta = parser.parse(sample)
    print(meta)

if __name__ == "__main__":
    main()
