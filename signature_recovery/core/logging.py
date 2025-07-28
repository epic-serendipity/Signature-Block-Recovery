#!/usr/bin/env python3
"""Logging utilities with JSON formatting and retry decorator."""

# Imports
import json
import logging
import time
from functools import wraps
from logging.handlers import TimedRotatingFileHandler
from typing import Callable, Type

# Logging

class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting
        data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "component": getattr(record, "component", ""),
            "msg_id": getattr(record, "msg_id", ""),
            "heuristic_used": getattr(record, "heuristic_used", ""),
            "duration_ms": getattr(record, "duration_ms", 0),
            "confidence": getattr(record, "confidence", 0.0),
        }
        return json.dumps(data)

# Globals
DEFAULT_LOG_FILE = "recovery.log"

# Classes/Functions

def setup_logging(verbose: bool = False, log_file: str = DEFAULT_LOG_FILE) -> None:
    """Configure root logger with console and rotating file handlers."""
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)
    for h in list(root.handlers):
        root.removeHandler(h)
    formatter = JsonFormatter()
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    root.addHandler(console)


def retry(
    exceptions: Type[Exception],
    tries: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
) -> Callable[[Callable], Callable]:
    """Retry decorator with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for attempt in range(tries):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == tries - 1:
                        raise
                    time.sleep(_delay)
                    _delay *= backoff
        return wrapper

    return decorator

# main
if __name__ == "__main__":  # pragma: no cover - manual test
    setup_logging(True)
    log_message = logging.getLogger().info
    log_message("test structured logging", extra={"component": "selftest"})
