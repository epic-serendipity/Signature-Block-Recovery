#!/usr/bin/env python3
"""Runtime metrics collection utilities."""

# Imports
from dataclasses import dataclass, asdict
from typing import List
import time
import threading

from template import log_message

# Logging

# Globals

# Classes/Functions

@dataclass
class MessageMetric:
    """Per-message metric record."""

    msg_id: str
    extracted: bool
    confidence: float
    time_ms: float


class MetricsCollector:
    """Thread-safe collector for per-message metrics and aggregates."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._metrics: List[MessageMetric] = []
        self.start_time = time.time()

    def record(self, metric: MessageMetric) -> None:
        """Add ``metric`` to the collection."""
        with self._lock:
            self._metrics.append(metric)

    def summarize(self) -> dict:
        """Return aggregate statistics for all recorded metrics."""
        with self._lock:
            total = len(self._metrics)
            extracted = sum(1 for m in self._metrics if m.extracted)
            avg_time = sum(m.time_ms for m in self._metrics) / total if total else 0
            avg_conf = sum(m.confidence for m in self._metrics) / total if total else 0
        return {
            "total_messages": total,
            "signatures_extracted": extracted,
            "average_time_ms": avg_time,
            "average_confidence": avg_conf,
            "duration_s": time.time() - self.start_time,
        }

    def dump(self, path: str) -> None:
        """Write all recorded metrics and summary to ``path`` as JSON."""
        import json

        with self._lock:
            data = {
                "per_message": [asdict(m) for m in self._metrics],
                "summary": self.summarize(),
            }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":  # pragma: no cover - manual run
    collector = MetricsCollector()
    collector.record(MessageMetric("1", True, 0.9, 10))
    collector.record(MessageMetric("2", False, 0.0, 5))
    collector.dump("metrics.json")
    log_message("info", "Metrics written to metrics.json")
