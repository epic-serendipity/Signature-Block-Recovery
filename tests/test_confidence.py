import subprocess
import sys
from pathlib import Path

from signature_recovery.core.extractor import SignatureExtractor
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.models import Signature


def test_confidence_scoring():
    extractor = SignatureExtractor()
    body = "Hello\n--\nJohn Doe\nEngineer\nACME\njohn@acme.com"
    sig = extractor.extract_from_body(body)
    assert sig is not None
    assert sig.confidence >= 0.95


def test_confidence_filtering(tmp_path):
    db = tmp_path / "idx.db"
    index = SQLiteFTSIndex(str(db))
    index.add(Signature(text="Low", source_msg_id="1", confidence=0.4))
    index.add(Signature(text="High", source_msg_id="2", confidence=0.9))

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "signature_recovery.cli.main",
            "--min-confidence",
            "0.8",
            "query",
            "--index",
            str(db),
            "--q",
            "*",
        ],
        capture_output=True,
        text=True,
    )
    assert "High" in res.stdout
    assert "Low" not in res.stdout
