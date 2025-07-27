import sqlite3
from pathlib import Path

import pytest

from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.models import Signature


pytestmark = pytest.mark.benchmark


def test_index_size(tmp_path):
    db_path = tmp_path / "idx.db"
    index = SQLiteFTSIndex(str(db_path))
    signatures = [
        Signature(text=f"Sig {i}", source_msg_id=str(i), timestamp=str(i))
        for i in range(5)
    ]
    index.add_batch(signatures)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM signatures")
    count = cur.fetchone()[0]
    conn.close()
    assert count == len(signatures)
