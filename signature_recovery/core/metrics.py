#!/usr/bin/env python3
"""Metrics collection utilities."""

# Imports
import json
from dataclasses import dataclass
from template import log_message

# Logging

# Globals

# Classes/Functions

@dataclass
class Metrics:
    """Accumulates processing metrics."""

    total_messages: int = 0
    signatures_found: int = 0
    total_time_ms: float = 0.0
    total_confidence: float = 0.0

    def record(
        self, msg_id: str, extracted: bool, confidence: float, num_lines: int, time_ms: float
    ) -> None:
        """Log message metrics and update counters."""
        log_message(
            "info",
            json.dumps(
                {
                    "msg_id": msg_id,
                    "extracted": extracted,
                    "confidence": round(confidence, 2),
                    "num_lines": num_lines,
                    "time_ms": round(time_ms, 2),
                }
            ),
        )
        self.total_messages += 1
        self.total_time_ms += time_ms
        if extracted:
            self.signatures_found += 1
            self.total_confidence += confidence

    def summary(self) -> dict:
        """Return aggregated metrics."""
        avg_time = self.total_time_ms / self.total_messages if self.total_messages else 0.0
        avg_conf = (
            self.total_confidence / self.signatures_found if self.signatures_found else 0.0
        )
        return {
            "messages": self.total_messages,
            "signatures_found": self.signatures_found,
            "avg_time_ms": round(avg_time, 2),
            "avg_confidence": round(avg_conf, 2),
        }


def main() -> None:  # pragma: no cover - manual test
    m = Metrics()
    m.record("1", True, 0.8, 5, 1.2)
    m.record("2", False, 0.0, 3, 0.5)
    print(json.dumps(m.summary(), indent=2))


if __name__ == "__main__":
    main()
