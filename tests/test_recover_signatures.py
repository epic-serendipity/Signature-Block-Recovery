import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.models import Message, Signature


def _build_index(tmp_path: Path) -> Path:
    db = tmp_path / "idx.db"
    index = SQLiteFTSIndex(str(db))
    index.add(Signature(text="John Doe\nEngineer", source_msg_id="1", timestamp="123", confidence=0.9))
    index.add(Signature(text="Jane Smith\nManager", source_msg_id="2", timestamp="456", confidence=0.8))
    return db


def _run(cmd, env=None):
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_cli_help():
    result = _run([sys.executable, "-m", "signature_recovery.cli.main", "--help"])
    assert result.returncode == 0
    assert "extract" in result.stdout
    assert "query" in result.stdout
    assert "export" in result.stdout
    assert "--threads" in result.stdout
    assert "--batch-size" in result.stdout
    assert "--min-confidence" in result.stdout


def test_subcommand_help():
    for sub in ["extract", "query", "export"]:
        res = _run([sys.executable, "-m", "signature_recovery.cli.main", sub, "--help"])
        assert res.returncode == 0
        assert "--help" not in res.stderr


def test_query_verbose_confidence(tmp_path):
    db = _build_index(tmp_path)
    res = _run([
        sys.executable,
        "-m",
        "signature_recovery.cli.main",
        "query",
        "--index",
        str(db),
        "--q",
        "John",
        "--verbose",
    ])
    assert "John Doe" in res.stdout
    assert "0.90" in res.stdout or "0.9" in res.stdout


def test_extract_query_export_flow(tmp_path, monkeypatch, capsys):
    pst = tmp_path / "dummy.pst"
    pst.write_text("dummy")
    db = tmp_path / "out.db"
    metrics = tmp_path / "metrics.json"
    csv_out = tmp_path / "out.csv"

    msgs = [
        Message(body="Hi\n--\nJohn Doe\nEngineer", msg_id="1", timestamp=1),
        Message(body="Hello\n--\nJane Smith\nManager", msg_id="2", timestamp=2),
    ]

    class FakeParser:
        def __init__(self, path):
            pass

        def iter_messages(self):
            for m in msgs:
                yield m

    from signature_recovery.cli import main as cli_main
    monkeypatch.setattr(cli_main, "PSTParser", FakeParser)

    with pytest.raises(SystemExit) as e:
        cli_main.main([
            "--batch-size",
            "1",
            "--metrics",
            "--dump-metrics",
            str(metrics),
            "extract",
            "--input",
            str(pst),
            "--index",
            str(db),
        ])
    assert e.value.code == 0
    assert db.exists()
    out = capsys.readouterr().out
    assert "Processed" in out
    data = json.loads(metrics.read_text())
    assert data["summary"]["total_messages"] == 2
    assert data["summary"]["signatures_extracted"] >= 2

    with pytest.raises(SystemExit) as e:
        cli_main.main(["query", "--index", str(db), "--q", "John"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert "John Doe" in out

    with pytest.raises(SystemExit) as e:
        cli_main.main([
            "export",
            "--index",
            str(db),
            "--format",
            "csv",
            "--out",
            str(csv_out),
        ])
    assert e.value.code == 0
    assert csv_out.exists()
    content = csv_out.read_text()
    assert "source_msg_id" in content


def test_cli_error_conditions(tmp_path):
    db = _build_index(tmp_path)
    res = _run([sys.executable, "-m", "signature_recovery.cli.main", "extract", "--index", str(db)], env=os.environ)
    assert res.returncode != 0

    res = _run([
        sys.executable,
        "-m",
        "signature_recovery.cli.main",
        "export",
        "--index",
        str(db),
        "--format",
        "bad",
        "--out",
        str(tmp_path / "f"),
    ])
    assert res.returncode != 0

    res = _run([
        sys.executable,
        "-m",
        "signature_recovery.cli.main",
        "query",
        "--index",
        str(tmp_path / "missing.db"),
        "--q",
        "x",
    ])
    assert res.returncode != 0


def test_version_flag():
    res = _run([sys.executable, "-m", "signature_recovery.cli.main", "--version"])
    assert res.returncode == 0
    assert "0.1.0" in res.stdout


def test_internal_error_exit_code(tmp_path):
    script = (
        "import sys, signature_recovery.cli.main as m;"
        "m.handle_extract=lambda a: (_ for _ in ()).throw(RuntimeError('boom'));"
        f"m.main(['extract','--input','{tmp_path}/x.pst','--index','{tmp_path}/x.db'])"
    )
    res = subprocess.run([sys.executable, "-c", script], text=True, capture_output=True)
    assert res.returncode == 2

