import json
import csv
from pathlib import Path

from signature_recovery.core.models import Signature, SignatureMetadata
from signature_recovery.exporter import export_to_csv, export_to_json, export_to_excel


def _sample_signatures():
    meta = SignatureMetadata(name="John Doe", email="john@example.com")
    sig = Signature(text="John", source_msg_id="1", metadata=meta)
    return [sig]


def test_export_csv(tmp_path):
    path = tmp_path / "sigs.csv"
    export_to_csv(_sample_signatures(), str(path))
    rows = list(csv.reader(path.read_text().splitlines()))
    assert rows[0][0] == "source_msg_id"
    assert rows[1][3] == "John Doe"


def test_export_json(tmp_path):
    path = tmp_path / "sigs.json"
    export_to_json(_sample_signatures(), str(path))
    data = json.loads(path.read_text())
    assert data[0]["name"] == "John Doe"


def test_export_excel(tmp_path):
    path = tmp_path / "sigs.xlsx"
    export_to_excel(_sample_signatures(), str(path))
    assert path.exists()
