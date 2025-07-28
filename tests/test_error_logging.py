import logging
import types
import builtins
import sqlite3
import time

import pytest

from signature_recovery.core.pst_parser import PSTParser
from signature_recovery.core.extractor import SignatureExtractor
from signature_recovery.core.deduplicator import dedupe_signatures
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.logging import retry
from signature_recovery.core.models import Signature
import sys


def _setup_fake_pst(monkeypatch):
    class FakePst:
        def open(self, path):
            pass

        def get_root_folder(self):
            class Folder:
                name = "Inbox"

                def get_number_of_sub_messages(self):
                    return 1

                def get_sub_message(self, i):
                    raise IOError("corrupt")

                def get_number_of_sub_folders(self):
                    return 0

            return Folder()

    monkeypatch.setitem(sys.modules, "pypff", types.SimpleNamespace(file=lambda: FakePst()))


def test_pst_parser_logs_warning(monkeypatch, tmp_path, caplog):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    _setup_fake_pst(monkeypatch)
    parser = PSTParser(str(pst))
    with caplog.at_level(logging.WARNING):
        list(parser.iter_messages())
    assert any("Failed to read message" in r.message for r in caplog.records)


def test_extractor_handles_exception(caplog):
    extractor = SignatureExtractor()

    class BadHeur:
        def detect_boundary(self, l, r):
            raise ValueError("boom")

    extractor.heuristics.insert(0, BadHeur())
    with caplog.at_level(logging.WARNING):
        sig = extractor.extract_signature("body", "1")
    assert sig is None
    assert any("heuristic error" in r.message for r in caplog.records)


def test_dedupe_logs_error(monkeypatch, caplog):
    monkeypatch.setattr(
        "signature_recovery.core.deduplicator._similar",
        lambda a, b: (_ for _ in ()).throw(ValueError("bad")),
    )
    sig = Signature(text="a", source_msg_id="1")
    with caplog.at_level(logging.ERROR):
        dedupe_signatures([sig, sig])
    assert any("dedupe error" in r.message for r in caplog.records)


def test_retry_decorator():
    attempts = []

    @retry(Exception, tries=3, delay=0.01)
    def flaky():
        attempts.append(time.time())
        if len(attempts) < 3:
            raise IOError("fail")
        return 42

    assert flaky() == 42
    assert len(attempts) == 3


def test_index_retry(tmp_path, monkeypatch):
    db = tmp_path / "idx.db"

    class FailOnceIndex(SQLiteFTSIndex):
        def __init__(self, path):
            super().__init__(path)
            self.calls = 0

        @retry(sqlite3.OperationalError, tries=2, delay=0.01)
        def _commit(self):
            self.calls += 1
            if self.calls < 2:
                raise sqlite3.OperationalError("locked")
            return super()._commit()

    idx = FailOnceIndex(str(db))
    idx.add(Signature(text="x", source_msg_id="1"))
    assert idx.calls >= 2

