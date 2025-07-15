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
  - PST parsing interface (**Complete**)
  - Folder/date range filters (**Complete**)
  - Signature extraction heuristics (**Complete**)
  - Deduplication utilities (**Complete**)
  - Structured signature parser (**Complete**)
  - Metadata parsing (**Complete**)
  - Configuration & Tuning (**In Progress**)
  - Confidence Scoring (**Planned**)
  - Metrics & Observability (**Planned**)
- **Files**
  - `signature_recovery/core/models.py` — dataclass for signature records and messages (**Complete**)
  - `signature_recovery/core/pst_parser.py` — streaming PST parser (**Complete**)
  - `signature_recovery/core/extractor.py` — extraction logic with heuristics and HTML normalization (**Complete**)
  - `signature_recovery/core/deduplicator.py` — fuzzy dedupe implementation (**Complete**)
  - `signature_recovery/core/parser.py` — parse names, emails, phones (**Complete**)
  - `signature_recovery/core/config.py` — load YAML configuration (**In Progress**)
  - `signature_recovery/core/metrics.py` — runtime metrics aggregation (**Planned**)
  - `config.example.yaml` — sample configuration (**In Progress**)

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
  - Expose `query` subcommand for on-demand search (**Planned**)
  - Export results to CSV/JSON/Excel (**Planned**)
- **Files**
  - `signature_recovery/cli/main.py` — argparse interface with batch-processing flags and metrics (**Complete**)
  - `setup.py` — project packaging and console entry point (**Complete**)

### GUI
- **Features**
  - Basic Tkinter application (**Complete**)
  - Pagination controls and filters (**In Progress**)
- **Files**
  - `signature_recovery/gui/app.py` — minimal GUI
  - `signature_recovery/gui/app.py` — add search panel and results display (**In Progress**)
  - `signature_recovery/gui/app.py` — pagination support (**In Progress**)

### Exporter
- **Features**
  - CSV, JSON, Excel export utilities (**Complete**)
- **Files**
  - `signature_recovery/exporter.py` — export helpers (**Complete**)

### API
- **Features**
  - REST search endpoint with pagination (**Complete**)
  - REST spec, filters, pagination (**In Progress**)
- **Files**
  - `signature_recovery/api.py` — Flask API server (**Complete**)

### Tests
- **Features**
  - Unit tests for extractor and deduplicator (**Complete**)
  - PST parser tests (**Complete**)
  - Benchmark tests for performance and index validity (**In Progress**)
  - Parser metadata tests (**Complete**)
  - Pipeline smoke test (**Complete**)
  - Exporter and API tests (**Complete**)
- **Files**
  - `tests/test_extractor.py` — extraction tests
  - `tests/test_deduplicator.py` — deduplication tests (**Complete**)
  - `tests/test_pst_parser.py` — PST parser tests (**Complete**)
  - `tests/fixtures/html_bodies/` — sample HTML messages for extractor tests (**Complete**)
  - `tests/fixtures/html_bodies/nested.html` — nested tag HTML fixture (**Complete**)
  - `tests/test_pipeline.py` — end-to-end pipeline test (**Complete**)
  - `tests/test_parser.py` — metadata parser examples (**Complete**)
  - `tests/test_exporter.py` — export format tests (**Complete**)
  - `tests/test_api.py` — REST API tests (**Complete**)
  - `tests/benchmarks/test_large_pst.py` — large PST benchmark (**In Progress**)
  - `tests/benchmarks/test_index_size.py` — index size benchmark (**In Progress**)

### CI Configuration
- **Features**
  - Editable install of package for tests (**Complete**)
  - CLI help-grep step with threads flag validation (**Complete**)
  - Benchmark tests (**In Progress**)
- **Files**
  - `.github/workflows/ci.yml` — CI workflow (**Complete**)

## Open Planning Questions

- **Data Sources & Scale**
  - Typical size, number, and location of `.pst` files to process
  - Expected volume of emails (e.g. millions of messages)
  - Target performance (e.g. signatures extracted per hour)
- **Performance & Scaling**
  - Target throughput (messages/sec) per thread
  - Memory footprint per batch size
  - Desired latency for small vs. large PSTs
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
- **Search Functionality**
  - Query syntax (full-text vs. fielded search)
  - UI/UX requirements (pagination, sorting)
- **Benchmark Targets**
  - Minimum acceptable throughput
  - Index size growth per signature
