#!/usr/bin/env python3
"""Search index interface and SQLite implementation."""

import logging
import sqlite3
import json
from typing import Iterable, List

from ..core.models import Signature, SignatureMetadata
from ..core.pst_parser import log_message


class SearchIndex:
    """Abstract search index."""

    def add(self, signature: Signature) -> None:
        raise NotImplementedError

    def add_batch(self, signatures: Iterable[Signature]) -> None:
        """Add multiple signatures at once."""
        for sig in signatures:
            self.add(sig)

    def query(self, q: str | None = None) -> List[Signature]:
        raise NotImplementedError


class SQLiteFTSIndex(SearchIndex):
    """SQLite full-text search implementation."""

    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS signatures "
            "USING fts5("
            "source_msg_id, timestamp, text, confidence UNINDEXED, metadata UNINDEXED"
            ")"
        )
        self.conn.commit()

    def add(self, signature: Signature) -> None:
        log_message(logging.DEBUG, "Indexing signature")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO signatures (source_msg_id, timestamp, text, confidence, metadata)"
            " VALUES (?,?,?,?,?)",
            (
                signature.source_msg_id,
                signature.timestamp or "",
                signature.text,
                signature.confidence,
                json.dumps(signature.metadata.__dict__),
            ),
        )
        self.conn.commit()

    def add_batch(self, signatures: Iterable[Signature]) -> None:
        log_message(logging.DEBUG, "Indexing batch of signatures")
        cur = self.conn.cursor()
        cur.executemany(
            "INSERT INTO signatures (source_msg_id, timestamp, text, confidence, metadata)"
            " VALUES (?,?,?,?,?)",
            [
                (
                    sig.source_msg_id,
                    sig.timestamp or "",
                    sig.text,
                    sig.confidence,
                    json.dumps(sig.metadata.__dict__),
                )
                for sig in signatures
            ],
        )
        self.conn.commit()

    def query(self, q: str | None = None) -> List[Signature]:
        log_message(logging.DEBUG, "Querying index")
        cur = self.conn.cursor()
        if q is None or q == "*" or not str(q).strip():
            cur.execute(
                "SELECT source_msg_id, timestamp, text, confidence, metadata FROM signatures"
            )
        else:
            cur.execute(
                "SELECT source_msg_id, timestamp, text, confidence, metadata "
                "FROM signatures WHERE signatures MATCH ?",
                (q,),
            )
        rows = cur.fetchall()
        result = []
        for row in rows:
            meta = SignatureMetadata(**json.loads(row[4])) if row[4] else SignatureMetadata()
            result.append(
                Signature(
                    text=row[2],
                    source_msg_id=row[0],
                    timestamp=row[1],
                    metadata=meta,
                    confidence=float(row[3]),
                )
            )
        return result
