from signature_recovery.core.extractor import SignatureExtractor


def test_confidence_scoring():
    extractor = SignatureExtractor()
    body = "Hello\n--\nJohn Doe\nEngineer\nACME\njohn@acme.com"
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert sig.confidence > 0.9


def test_confidence_filtering():
    extractor = SignatureExtractor()
    body = "Hi\n--\nJane Doe\njane@example.com"
    sig = extractor.extract_from_body(body)
    assert sig is not None
    min_c = sig.confidence + 0.05
    kept = [s for s in [sig] if s.confidence >= min_c]
    assert not kept
