from signature_recovery.core.models import Message
from signature_recovery.core.pst_parser import PSTParser
from signature_recovery.core.extractor import SignatureExtractor
from signature_recovery.core.deduplicator import dedupe_signatures


def _mock_parser(monkeypatch):
    msgs = [
        Message(body="hi\n--\nJohn Doe\njohn@ex.com", msg_id="1", timestamp=1),
        Message(body="hello\n--\nJohn Doe\njohn@ex.com", msg_id="2", timestamp=2),
        Message(body="hey\n--\nJane Smith\njane@ex.com", msg_id="3", timestamp=3),
    ]

    class FakeParser:
        def __init__(self, path):
            pass

        def iter_messages(self, *a, **k):
            for m in msgs:
                yield m

    import os
    monkeypatch.setattr("signature_recovery.core.pst_parser.PSTParser", FakeParser)
    globals()["PSTParser"] = FakeParser
    monkeypatch.setattr(os.path, "isfile", lambda x: True)
    import types, sys
    class FakePst:
        def open(self, path):
            pass
        def get_root_folder(self):
            return None

    monkeypatch.setitem(sys.modules, "pypff", types.SimpleNamespace(file=lambda: FakePst()))


def test_pipeline(monkeypatch):
    _mock_parser(monkeypatch)
    parser = PSTParser("dummy.pst")
    extractor = SignatureExtractor()
    sigs = []
    for msg in parser.iter_messages():
        sig = extractor.extract_signature(msg.body, msg.msg_id, msg.timestamp)
        if sig:
            sigs.append(sig)
    deduped = dedupe_signatures(sigs)
    assert len(deduped) == 2
    names = sorted(s.metadata.name for s in deduped)
    assert names == ["Jane Smith", "John Doe"]

