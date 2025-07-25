from signature_recovery.core.metrics import MetricsCollector, MessageMetric
import json
import subprocess
import sys


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


def test_cli_dump_metrics(tmp_path):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    db = tmp_path / "out.db"
    metrics_path = tmp_path / "metrics.json"
    cmd = [
        sys.executable,
        "-m",
        "signature_recovery.cli.main",
        "--batch-size",
        "1",
        "--dump-metrics",
        str(metrics_path),
        "extract",
        "--input",
        str(pst),
        "--index",
        str(db),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert metrics_path.exists()
    data = json.loads(metrics_path.read_text())
    assert "summary" in data and "per_message" in data