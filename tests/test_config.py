from signature_recovery.core.config import load_config
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
