from signature_recovery.api import app
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.models import Signature


def test_search_endpoint(tmp_path):
    db = tmp_path / "idx.db"
    index = SQLiteFTSIndex(str(db))
    index.add(Signature(text="John Doe", source_msg_id="1"))

    app.testing = True
    client = app.test_client()
    # inject index
    from signature_recovery import api as api_mod
    api_mod.index = index

    res = client.get("/search?q=John")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] == 1
    assert "John Doe" in data["results"][0]
