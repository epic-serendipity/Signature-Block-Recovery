#!/usr/bin/env python3
"""PST parsing utilities."""

import logging
from typing import Iterator, Tuple


def log_message(level: int, msg: str) -> None:
    """Simple logging helper."""
    logging.log(level, msg)


class PSTParser:
    """Streams messages from a PST file. Placeholder implementation."""

    def __init__(self, pst_path: str) -> None:
        self.pst_path = pst_path

    def messages(self) -> Iterator[Tuple[str, str]]:
        """Yield message_id and body text. Currently stubbed."""
        log_message(logging.DEBUG, "PSTParser.messages called - stub")
        return iter([])
