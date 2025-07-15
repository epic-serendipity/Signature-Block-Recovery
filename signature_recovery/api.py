#!/usr/bin/env python3
"""Minimal REST API for signature search."""

# Imports
from flask import Flask, request, jsonify

from .index.search_index import SQLiteFTSIndex
from template import log_message

# Globals
app = Flask(__name__)
index: SQLiteFTSIndex | None = None

# Classes/Functions
@app.route("/search")
def search() -> object:
    q = request.args.get("q", "*")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 10))
    if not index:
        return jsonify(results=[], total=0)
    results = index.query(q)
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
