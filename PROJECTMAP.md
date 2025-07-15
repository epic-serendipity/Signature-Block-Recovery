# Project Map

## Modules

### Documentation
- **Features**
  - Repository overview and contribution guidelines (**Complete**)
- **Files**
  - `README.md` — project overview
  - `AGENTS.md` — Codex automation rules
  - `PROJECTMAP.md` — project map and planning questions

### Signature Recovery Core
- **Features**
  - PST parsing interface (**Planned**)
  - Signature extraction heuristics (**In Progress**)
  - Deduplication utilities (**In Progress**)
- **Files**
  - `signature_recovery/core/models.py` — dataclass for signature records
  - `signature_recovery/core/pst_parser.py` — stub PST parser
  - `signature_recovery/core/extractor.py` — extraction logic with heuristics and HTML normalization (**Complete**)
  - `signature_recovery/core/deduplicator.py` — fuzzy dedupe implementation

### Indexing
- **Features**
  - Abstract search index interface (**Complete**)
  - SQLite FTS backend (**Complete**)
- **Files**
  - `signature_recovery/index/search_index.py` — index classes
  - `signature_recovery/index/indexer.py` — PST-to-index glue code

### CLI
- **Features**
  - Headless extraction entry point (**Complete**)
- **Files**
  - `signature_recovery/cli/main.py` — argparse interface

### GUI
- **Features**
  - Basic Tkinter application (**Complete**)
- **Files**
  - `signature_recovery/gui/app.py` — minimal GUI

### Tests
- **Features**
  - Unit tests for extractor and deduplicator (**In Progress**)
- **Files**
  - `tests/test_extractor.py` — extraction tests
  - `tests/test_deduplicator.py` — deduplication tests
  - `tests/fixtures/html_bodies/` — sample HTML messages for extractor tests (**Complete**)

## Open Planning Questions

- **Data Sources & Scale**
  - Typical size, number, and location of `.pst` files to process
  - Expected volume of emails (e.g. millions of messages)
  - Target performance (e.g. signatures extracted per hour)
- **Extraction Logic & Heuristics**
  - Definition of a "signature block" (lines in plain text, HTML, attachments?)
  - Rules for start/end detection (e.g. detect delimiter lines like "—" or "Regards,")
  - Expected false-positive rate and how to tune heuristics
- **Deduplication Criteria**
  - What constitutes a duplicate signature (exact text match, fuzzy match, normalized fields)
  - Tolerance for minor variations (e.g. different titles, phone formats)
- **Storage & Search Backend**
  - Target searchable format (SQLite, full-text index, Elasticsearch, etc.)
  - Query patterns (search by name, company, domain)
  - Retention and archival policies
- **CLI vs. GUI Requirements**
  - Will there be a desktop GUI for ad-hoc extraction?
  - Command-line support and batch scheduling
- **Platform & Dependencies**
  - Supported OSes (Windows, Linux, macOS)
  - Python version constraints (3.8+?)
  - Allowed third-party modules (pst-parser, regex libraries)
- **Error Handling & Logging**
  - Failure modes (corrupt PST, malformed messages)
  - Retry strategies and reporting
  - Log verbosity levels and log file rotation policy
- **Security & Privacy**
  - Handling of sensitive data (PII) in signatures
  - Access controls on extracted data
- **Timeline & Milestones**
  - Prototype extraction engine
  - Deduplication module
  - Search/indexing integration
  - GUI proof-of-concept
  - Testing and performance tuning
