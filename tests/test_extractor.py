from pathlib import Path

from signature_recovery.core.extractor import SignatureExtractor


def test_extract_simple():
    body = "Hello\nRegards,\nJohn Doe\nCompany"
    extractor = SignatureExtractor()
    sig = extractor.extract_signature(body, "1")
    assert sig is not None
    assert "John Doe" in sig.text


def _fixture(name: str) -> str:
    path = Path(__file__).parent / "fixtures" / "html_bodies" / name
    return path.read_text()


def test_extract_simple_html():
    body = _fixture("simple.html")
    extractor = SignatureExtractor()
    sig = extractor.extract_signature(body, "html1")
    assert sig is not None
    assert "John Doe" in sig.text


def test_extract_html_hr_boundary():
    body = _fixture("hr.html")
    extractor = SignatureExtractor()
    sig = extractor.extract_signature(body, "html2")
    assert sig is not None
    assert "John Doe" in sig.text


def test_extract_html_signature_div():
    body = _fixture("signature_div.html")
    extractor = SignatureExtractor()
    sig = extractor.extract_signature(body, "html3")
    assert sig is not None
    assert "John Doe" in sig.text
