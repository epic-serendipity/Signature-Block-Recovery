import json
import pytest

from signature_recovery.core.metrics import MetricsCollector, MessageMetric
from signature_recovery.core.models import Message


def test_metrics_summarize(tmp_path):
    collector = MetricsCollector()
    collector.record(MessageMetric("1", True, 0.8, 10))
    collector.record(MessageMetric("2", False, 0.0, 5))
    summary = collector.summarize()
    assert summary["total_messages"] == 2
    assert summary["signatures_extracted"] == 1
    assert round(summary["average_time_ms"], 2) == 7.5
    assert round(summary["average_confidence"], 2) == 0.4


def test_metrics_dump(tmp_path):
    collector = MetricsCollector()
    collector.record(MessageMetric("1", True, 0.8, 10))
    out = tmp_path / "m.json"
    collector.dump(str(out))
    data = json.loads(out.read_text())
    assert "per_message" in data
    assert "summary" in data
    assert data["per_message"][0]["msg_id"] == "1"


def test_cli_dump_metrics(tmp_path, monkeypatch):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    db = tmp_path / "out.db"
    metrics_path = tmp_path / "metrics.json"

    msgs = [
        Message(body="Hi\n--\nJohn Doe\nEngineer", msg_id="1", timestamp=1),
        Message(body="Hello\n--\nJane Smith\nManager", msg_id="2", timestamp=2),
    ]

    class FakeParser:
        def __init__(self, path):
            pass

        def iter_messages(self):
            for m in msgs:
                yield m

    from signature_recovery.cli import main as cli_main
    monkeypatch.setattr(cli_main, "PSTParser", FakeParser)

    with pytest.raises(SystemExit) as e:
        cli_main.main([
            "--batch-size",
            "1",
            "--dump-metrics",
            str(metrics_path),
            "extract",
            "--input",
            str(pst),
            "--index",
            str(db),
        ])
    assert e.value.code == 0
    assert metrics_path.exists()
    data = json.loads(metrics_path.read_text())
    assert "summary" in data and "per_message" in data

