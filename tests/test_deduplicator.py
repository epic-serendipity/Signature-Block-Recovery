from signature_recovery.core.deduplicator import dedupe_signatures
from signature_recovery.core.models import Signature


def _sigs():
    sig1 = Signature(
        text="John Doe\nEngineer\nAcme Corp",
        source_msg_id="1",
        timestamp=1000,
    )
    sig2 = Signature(
        text="john doe\nEngineer\nAcme Corp",
        source_msg_id="2",
        timestamp=1100,
    )
    sig3 = Signature(
        text="Jane Smith\nManager\nAcme Corp",
        source_msg_id="3",
        timestamp=1200,
    )
    return sig1, sig2, sig3


def test_exact_duplicate_collapse():
    sig1, _, _ = _sigs()
    dup = Signature(
        text="John Doe\nEngineer\nAcme Corp",
        source_msg_id="dup",
        timestamp=1500,
    )
    result = dedupe_signatures([sig1, dup], threshold=1.0)
    assert len(result) == 1
    assert result[0].timestamp == 1000


def test_case_insensitive_merge():
    sig1, sig2, sig3 = _sigs()
    result = dedupe_signatures([sig1, sig2, sig3], threshold=0.9)
    assert len(result) == 2
    john = next(s for s in result if "john" in s.text.lower())
    assert john.timestamp == 1000


def test_high_threshold_keeps_all():
    sig1, sig2, sig3 = _sigs()
    result = dedupe_signatures([sig1, sig2, sig3], threshold=1.0)
    assert len(result) == 2


def test_metadata_merge_earliest_timestamp():
    sig1 = Signature(
        text="John Doe\nEngineer\nAcme Corp",
        source_msg_id="1",
        timestamp=1000,
    )
    sig2 = Signature(
        text="john doe\nEngineer\nAcme Corp",
        source_msg_id="2",
        timestamp=1100,
    )
    result = dedupe_signatures([sig2, sig1], threshold=0.9)
    assert len(result) == 1
    assert result[0].timestamp == 1000


def test_large_list_performance():
    base = Signature(text="John Doe", source_msg_id="0", timestamp=0)
    sigs = [
        Signature(text=f"John Doe {i%5}", source_msg_id=str(i), timestamp=i)
        for i in range(1000)
    ]
    sigs.append(base)
    uniques = dedupe_signatures(sigs, threshold=0.8)
    assert len(uniques) <= 5
