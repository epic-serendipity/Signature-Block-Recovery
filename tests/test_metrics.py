from signature_recovery.core.metrics import Metrics


def test_metrics_aggregation():
    m = Metrics()
    m.record("1", True, 0.8, 4, 1.0)
    m.record("2", False, 0.0, 2, 0.5)
    summary = m.summary()
    assert summary["messages"] == 2
    assert summary["signatures_found"] == 1
    assert summary["avg_confidence"] == 0.8
    assert summary["avg_time_ms"] == 0.75
