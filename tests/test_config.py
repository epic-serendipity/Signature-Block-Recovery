import builtins
import logging

import pytest

from signature_recovery.core.config import load_config, DEFAULT_CONFIG
from signature_recovery.core.extractor import SignatureExtractor


def test_override_fallback_lines(tmp_path):
    cfg_path = tmp_path / "conf.yaml"
    cfg_path.write_text(
        """
extraction:
  max_fallback_lines: 3
  signoff_patterns:
    - "nomatch"
"""
    )
    cfg = load_config(str(cfg_path))
    extractor = SignatureExtractor(cfg)
    body = "one\ntwo\nthree\nfour\nfive"
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert sig.text.splitlines() == ["three", "four", "five"]


def test_defaults_without_yaml(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "yaml":
            raise ImportError("missing")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    cfg = load_config()
    assert cfg == DEFAULT_CONFIG


def test_missing_file_logs_warning(caplog, tmp_path):
    missing = tmp_path / "nope.yaml"
    with caplog.at_level(logging.WARNING):
        cfg = load_config(str(missing))
    assert cfg == DEFAULT_CONFIG
    assert any("Config file not found" in r.message for r in caplog.records)
