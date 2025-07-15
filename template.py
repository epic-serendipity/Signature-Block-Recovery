#!/usr/bin/env python3
"""Shared helpers used across modules."""

import logging
from typing import Union


def log_message(level: Union[int, str], msg: str) -> None:
    """Log ``msg`` at the specified ``level``.

    ``level`` can be a logging level constant or a case-insensitive
    string like "info" or "warning".
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logging.log(level, msg)

