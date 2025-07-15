from pathlib import Path

from signature_recovery.core.extractor import SignatureExtractor


def test_plain_text_only():
    body = "Hello\n--\nJohn Doe"
    extractor = SignatureExtractor()
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert sig.text == "--\nJohn Doe"
    assert sig.metadata.name == "John Doe"


def _fixture(name: str) -> str:
    path = Path(__file__).parent / "fixtures" / "html_bodies" / name
    return path.read_text()


def test_basic_html_normalization():
    body = _fixture("simple.html")
    extractor = SignatureExtractor()
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert "John Doe" in sig.text
    assert sig.metadata.name == "John Doe"


def test_html_hr_boundary():
    body = _fixture("hr.html")
    extractor = SignatureExtractor()
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert "Jane Smith" in sig.text
    assert "Jane" in (sig.metadata.name or sig.text)


def test_html_signature_div():
    body = _fixture("sig_div.html")
    extractor = SignatureExtractor()
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert "Alice" in sig.text
    assert sig.metadata.name.startswith("Alice")
