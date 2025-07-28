#!/usr/bin/env python3
"""Shared helpers used across modules."""

import logging
from typing import Union


def log_message(level: Union[int, str], msg: str, **extra) -> None:
    """Log ``msg`` at the specified ``level`` with optional structured fields."""

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().log(level, msg, extra=extra)

