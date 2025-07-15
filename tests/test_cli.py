import subprocess
import sys
from pathlib import Path

from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.models import Signature


def _build_index(tmp_path: Path) -> Path:
    db = tmp_path / "idx.db"
    index = SQLiteFTSIndex(str(db))
    index.add(Signature(text="John Doe\nEngineer", source_msg_id="1", timestamp="123"))
    index.add(Signature(text="Jane Smith\nManager", source_msg_id="2", timestamp="456"))
    return db


def test_cli_query_basic(tmp_path):
    db = _build_index(tmp_path)
    cmd = [sys.executable, "-m", "signature_recovery.cli.main", "query", "--index", str(db), "--q", "John"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "John Doe" in result.stdout


def test_cli_query_verbose(tmp_path):
    db = _build_index(tmp_path)
    cmd = [
        sys.executable,
        "-m",
        "signature_recovery.cli.main",
        "query",
        "--index",
        str(db),
        "--q",
        "Jane",
        "--verbose",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Jane Smith" in result.stdout
    assert "2" in result.stdout
