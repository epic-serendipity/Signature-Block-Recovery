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

