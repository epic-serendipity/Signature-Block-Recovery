import os
import sys
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _skip(request):
    if not request.config.getoption("--benchmark"):
        pytest.skip("benchmark tests skipped")


def test_large_pst(tmp_path):
    pst_path = os.environ.get("LARGE_PST_PATH")
    if not pst_path or not Path(pst_path).is_file():
        pytest.skip("LARGE_PST_PATH not set")
    db = tmp_path / "idx.db"
    cmd = [
        sys.executable,
        "-m",
        "signature_recovery.cli.main",
        "extract",
        "--input",
        pst_path,
        "--output",
        str(db),
        "--metrics",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    rate = 0.0
    for line in result.stdout.splitlines():
        if "msg/sec" in line:
            part = line.rsplit("(", 1)[1]
            rate = float(part.split()[0])
            break
    min_rate = float(os.environ.get("MIN_MSG_RATE", "10"))
    assert rate >= min_rate
