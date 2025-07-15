import builtins
import sys
from pathlib import Path

import pytest

from signature_recovery.core.pst_parser import PSTParser


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        PSTParser("/no/such/file.pst")


def test_missing_pypff(monkeypatch, tmp_path):
    # create dummy pst file so path check passes
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")

    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pypff":
            raise ImportError("not installed")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError):
        PSTParser(str(pst))


def test_iter_messages_filters(monkeypatch, tmp_path):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    _setup_fake_pst(monkeypatch)
    parser = PSTParser(str(pst))
    msgs = list(parser.iter_messages(folders=["Inbox"], start=150, end=250))
    assert len(msgs) == 1
    assert msgs[0].body == "B"


def test_corrupt_message_skipped(monkeypatch, tmp_path):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    _setup_fake_pst(monkeypatch)
    parser = PSTParser(str(pst))
    msgs = list(parser.iter_messages())
    # one corrupt message should be skipped
    assert len(msgs) == 3


def _setup_fake_pst(monkeypatch):
    import types

    class FakeMessage:
        def __init__(self, body, ts, bad=False):
            self._body = body
            self.html_body = ""
            self.client_submit_time = ts
            self.identifier = b"id"
            self.bad = bad

        @property
        def plain_text_body(self):
            if self.bad:
                raise ValueError("corrupt")
            return self._body

    class FakeFolder:
        def __init__(self, name, msgs, subs=None):
            self.name = name
            self._msgs = msgs
            self._subs = subs or []

        def get_number_of_sub_messages(self):
            return len(self._msgs)

        def get_sub_message(self, i):
            return self._msgs[i]

        def get_number_of_sub_folders(self):
            return len(self._subs)

        def get_sub_folder(self, i):
            return self._subs[i]

    root = FakeFolder("root", [])
    inbox = FakeFolder(
        "Inbox",
        [FakeMessage("A", 100), FakeMessage("B", 200), FakeMessage("C", 300, bad=True)],
    )
    other = FakeFolder("Other", [FakeMessage("D", 400)])
    root._subs = [inbox, other]

    class FakePst:
        def open(self, path):
            pass

        def get_root_folder(self):
            return root

    monkeypatch.setitem(sys.modules, "pypff", types.SimpleNamespace(file=lambda: FakePst()))

