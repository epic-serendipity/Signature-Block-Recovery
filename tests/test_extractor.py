from signature_recovery.core.extractor import SignatureExtractor


def test_extract_simple():
    body = "Hello\nRegards,\nJohn Doe\nCompany"
    extractor = SignatureExtractor()
    sig = extractor.extract_signature(body, "1")
    assert sig is not None
    assert "John Doe" in sig.text
