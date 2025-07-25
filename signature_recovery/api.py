#!/usr/bin/env python3
"""Minimal REST API for signature search."""

# Imports
try:
    from flask import Flask, request, jsonify
except ImportError as e:
    raise RuntimeError(
        "Flask is required to run the API. Please install with `pip install flask`."
    ) from e

from .index.search_index import SQLiteFTSIndex
from template import log_message

# Globals
app = Flask(__name__)
index: SQLiteFTSIndex | None = None

# Classes/Functions
@app.route("/search")
def search() -> object:
    q_raw = request.args.get("q", "").strip()
    q = None if (q_raw == "" or q_raw == "*") else q_raw
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 10))
    min_conf = float(request.args.get("min_confidence", 0.0))
    if not index:
        return jsonify(results=[], total=0)
    results = index.query(q, min_confidence=min_conf)
    start = (page - 1) * size
    end = start + size
    subset = results[start:end]
    return jsonify(
        results=[s.text for s in subset],
        total=len(results),
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    global index
    index = SQLiteFTSIndex(args.index)
    app.run(port=args.port)


if __name__ == "__main__":
    main()
