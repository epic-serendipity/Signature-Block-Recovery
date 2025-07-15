#!/usr/bin/env python3
"""Configuration loader for Signature Recovery Core."""

# Imports
import os
import json
import logging
from typing import Any, Dict

logger = logging.getLogger("config")

# Globals
DEFAULT_CONFIG: Dict[str, Any] = {
    "extraction": {
        "max_fallback_lines": 5,
        "signoff_patterns": [
            r"--\s*$",
            r"thanks",
            r"regards",
            r"cheers",
            r"sincerely",
        ],
    },
    "parser": {
        "phone_patterns": [
            r"\(\d{3}\)\s*\d{3}-\d{4}",
            r"\+\d{1,2}\s\d{3}\s\d{3}\s\d{4}",
            r"\d{3}-\d{3}-\d{4}",
            r"\d{3}\.\d{3}\.\d{4}",
            r"\+?\d[\d\s-]{7,}\d",
        ]
    },
}


# Classes/Functions

def load_config(path: str | None = None) -> Dict[str, Any]:
    """Load configuration from a YAML file if provided, else return defaults."""
    if path is None:
        return DEFAULT_CONFIG

    if not os.path.isfile(path):
        logger.warning(f"Config file not found at {path}, using defaults")
        return DEFAULT_CONFIG

    try:
        import yaml
    except ImportError as e:  # pragma: no cover - runtime guard
        raise RuntimeError(
            "PyYAML is required to load configuration files. "
            "Please install with `pip install pyyaml`."
        ) from e

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg or {})
    return merged


def main() -> None:
    """Print loaded config for manual inspection."""
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?")
    args = p.parse_args()
    cfg = load_config(args.path)
    print(json.dumps(cfg, indent=2))


if __name__ == "__main__":  # pragma: no cover - manual entry
    main()
