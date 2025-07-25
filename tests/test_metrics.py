import json
import os
import subprocess
import sys
from pathlib import Path

from signature_recovery.core.metrics import MetricsCollector, MessageMetric


def test_metrics_summarize():
    mc = MetricsCollector()
    mc.record(MessageMetric("1", True, 0.8, 50))
    mc.record(MessageMetric("2", False, 0.0, 100))
    summary = mc.summarize()
    assert summary["total_messages"] == 2
    assert summary["signatures_extracted"] == 1
    assert summary["average_time_ms"] == 75
    assert summary["average_confidence"] == 0.4


def test_metrics_dump(tmp_path):
    mc = MetricsCollector()
    mc.record(MessageMetric("1", True, 1.0, 10))
    out = tmp_path / "m.json"
    mc.dump(str(out))
    data = json.loads(out.read_text())
    assert "per_message" in data
    assert "summary" in data
    assert data["summary"]["total_messages"] == 1


def test_cli_metrics_dump(tmp_path):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    db = tmp_path / "out.db"
    metrics = tmp_path / "metrics.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path(__file__).parent}:{env.get('PYTHONPATH','')}"
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "signature_recovery.cli.main",
            "--batch-size",
            "1",
            "--dump-metrics",
            str(metrics),
            "extract",
            "--input",
            str(pst),
            "--index",
            str(db),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0
    assert metrics.exists()
    data = json.loads(metrics.read_text())
    assert "summary" in data
    assert data["summary"]["total_messages"] >= 2
