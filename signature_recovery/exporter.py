#!/usr/bin/env python3
"""Export utilities for signatures."""

# Imports
import csv
import json
from typing import Iterable

try:
    from openpyxl import Workbook
except ImportError as e:
    raise RuntimeError(
        "openpyxl is required for Excel export. Please install with `pip install openpyxl`."
    ) from e

from .core.models import Signature
from template import log_message

# Logging

# Globals

# Classes/Functions

def export_to_csv(signatures: Iterable[Signature], path: str) -> None:
    """Write signatures to a CSV file."""
    log_message("info", f"Exporting CSV to {path}")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "source_msg_id",
            "timestamp",
            "text",
            "name",
            "title",
            "company",
            "phone",
            "email",
            "url",
            "address",
        ])
        for sig in signatures:
            m = sig.metadata
            writer.writerow([
                sig.source_msg_id,
                sig.timestamp or "",
                sig.text,
                m.name or "",
                m.title or "",
                m.company or "",
                m.phone or "",
                m.email or "",
                m.url or "",
                m.address or "",
            ])

def export_to_json(signatures: Iterable[Signature], path: str) -> None:
    """Write signatures to a JSON file."""
    log_message("info", f"Exporting JSON to {path}")
    data = []
    for sig in signatures:
        m = sig.metadata
        data.append(
            {
                "source_msg_id": sig.source_msg_id,
                "timestamp": sig.timestamp,
                "text": sig.text,
                "name": m.name,
                "title": m.title,
                "company": m.company,
                "phone": m.phone,
                "email": m.email,
                "url": m.url,
                "address": m.address,
            }
        )
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)

def export_to_excel(signatures: Iterable[Signature], path: str) -> None:
    """Write signatures to an Excel workbook."""
    log_message("info", f"Exporting Excel to {path}")
    wb = Workbook()
    ws = wb.active
    ws.append(
        [
            "source_msg_id",
            "timestamp",
            "text",
            "name",
            "title",
            "company",
            "phone",
            "email",
            "url",
            "address",
        ]
    )
    for sig in signatures:
        m = sig.metadata
        ws.append(
            [
                sig.source_msg_id,
                sig.timestamp or "",
                sig.text,
                m.name or "",
                m.title or "",
                m.company or "",
                m.phone or "",
                m.email or "",
                m.url or "",
                m.address or "",
            ]
        )
    wb.save(path)

# main

def main() -> None:
    sample = [Signature(text="John", source_msg_id="1")]
    export_to_csv(sample, "sigs.csv")

if __name__ == "__main__":
    main()
