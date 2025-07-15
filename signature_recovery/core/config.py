#!/usr/bin/env python3
"""Configuration loader for Signature Recovery Core."""

# Imports
import json
import os
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover - runtime guard
    raise RuntimeError(
        "PyYAML is required for configuration support. Install with `pip install pyyaml`."
    ) from e

# Logging
from template import log_message

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
    """Load YAML configuration from ``path`` if provided."""
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    if path and os.path.isfile(path):
        log_message("info", f"Loading config from {path}")
        with open(path, "r", encoding="utf-8") as fh:
            user = yaml.safe_load(fh) or {}
        _merge(cfg, user)
    return cfg


def _merge(target: Dict[str, Any], src: Dict[str, Any]) -> None:
    """Merge ``src`` into ``target`` recursively."""
    for key, val in src.items():
        if isinstance(val, dict) and isinstance(target.get(key), dict):
            _merge(target[key], val)
        else:
            target[key] = val


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
