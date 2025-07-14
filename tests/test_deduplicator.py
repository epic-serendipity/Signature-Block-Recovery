from signature_recovery.core.deduplicator import SignatureDeduplicator
from signature_recovery.core.models import Signature


def test_dedupe():
    sig1 = Signature(text="John Doe", source_msg_id="1")
    sig2 = Signature(text="John Doe", source_msg_id="2")
    deduper = SignatureDeduplicator()
    uniques = deduper.dedupe([sig1, sig2])
    assert len(uniques) == 1
