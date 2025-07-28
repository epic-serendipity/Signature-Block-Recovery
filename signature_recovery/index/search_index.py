#!/usr/bin/env python3
"""Search index interface and SQLite implementation."""

import logging
import sqlite3
import json
from typing import Iterable, List

from ..core.models import Signature, SignatureMetadata
from ..core.logging import retry
from template import log_message


class SearchIndex:
    """Abstract search index."""

    def add(self, signature: Signature) -> None:
        raise NotImplementedError

    def add_batch(self, signatures: Iterable[Signature]) -> None:
        """Add multiple signatures at once."""
        for sig in signatures:
            self.add(sig)

    def query(self, q: str | None = None, *, min_confidence: float = 0.0) -> List[Signature]:
        raise NotImplementedError


class SQLiteFTSIndex(SearchIndex):
    """SQLite full-text search implementation."""

    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_schema()

    @retry(sqlite3.OperationalError, tries=3, delay=0.1)
    def _commit(self):
        self.conn.commit()

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
        self._commit()

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
        self._commit()

    def query(self, q: str | None = None, *, min_confidence: float = 0.0) -> List[Signature]:
        """Return all matching signatures.

        ``q`` may be ``None`` to retrieve every row. ``"*"`` or blank strings are
        also treated as ``None`` for convenience.
        """

        log_message(logging.DEBUG, "Querying index")
        cur = self.conn.cursor()

        # Normalize wildcard queries
        if q is not None and str(q).strip() == "*":
            q = None

        where_clauses: list[str] = []
        params: dict[str, object] = {}
        if q:
            where_clauses.append("text MATCH :q")
            params["q"] = q
        if min_confidence > 0:
            where_clauses.append("confidence >= :minc")
            params["minc"] = min_confidence

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        sql = (
            "SELECT source_msg_id, timestamp, text, confidence, metadata "
            f"FROM signatures {where_sql}"
        )

        cur.execute(sql, params)
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
