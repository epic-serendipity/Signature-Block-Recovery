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
  - Configuration & Tuning (**Complete**)
  - Confidence Scoring (**Planned**)
  - Metrics & Observability (**Planned**)
- **Files**
  - `signature_recovery/core/models.py` — dataclass for signature records and messages (**Complete**)
  - `signature_recovery/core/pst_parser.py` — streaming PST parser (**Complete**)
  - `signature_recovery/core/extractor.py` — extraction logic with heuristics and HTML normalization (**Complete**)
  - `signature_recovery/core/deduplicator.py` — fuzzy dedupe implementation (**Complete**)
  - `signature_recovery/core/parser.py` — parse names, emails, phones (**Complete**)
  - `signature_recovery/core/config.py` — load YAML configuration (**Complete**)
  - `signature_recovery/core/metrics.py` — runtime metrics aggregation (**Planned**)
  - `config.example.yaml` — sample configuration (**Complete**)

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
  - Expose `query` subcommand for on-demand search (**Complete**)
  - Export results to CSV/JSON/Excel (**Complete**)
  - Metrics dump (`--metrics`, `--dump-metrics`) (**Complete**)
  - Version flag and standardized exit codes (**Complete**)
- **Files**
  - `signature_recovery/cli/main.py` — full argparse interface with all subcommands and flags (**Complete**)
  - `tests/test_cli.py` — comprehensive CLI integration tests (**Complete**)
  - `setup.py` — project packaging and console entry point (**Complete**)
  - `signature_recovery/__init__.py` — package metadata including version (**Complete**)

### GUI
- **Features**
  - Basic Tkinter application (**Complete**)
  - Pagination controls and page size selector (**Complete**)
  - Filters & facets (date range, company, title) (**Complete**)
  - Sort options on columns (**Complete**)
- **Files**
  - `signature_recovery/gui/app.py` — full-featured Tkinter application with modular panels; FilterPanel dynamic population (**Complete**)
  - `tests/test_gui.py` — GUI integration tests (**Complete**)

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

### Storage & Search Backend
- **Features**
  - Search Backend Comparison (**Planned**)
  - Abstracted SearchIndex interface (**Complete**)

### Tests
- **Features**
  - Unit tests for extractor and deduplicator (**Complete**)
  - PST parser tests (**Complete**)
  - Benchmark tests for performance and index validity (**In Progress**)
  - Parser metadata tests (**Complete**)
  - Pipeline smoke test (**Complete**)
  - Exporter and API tests (**Complete**)
  - CLI integration tests (**Complete**)
  - Confidence scoring tests (**Planned**)
  - Metrics aggregation tests (**Planned**)
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
  - `tests/test_confidence.py` — confidence scoring logic tests (**Planned**)
  - `tests/test_metrics.py` — metrics aggregation tests (**Planned**)

### CI Configuration
- **Features**
  - Editable install of package for tests (**Complete**)
  - CLI help-grep step with threads flag validation (**Complete**)
  - Verify CLI entry point subcommands (**Complete**)
  - Headless display support for GUI tests (**Complete**)
  - Benchmark tests (**In Progress**)
  - Benchmark CI job (nightly) (**Planned**)
- **Files**
  - `.github/workflows/ci.yml` — CI workflow (**Complete**)

## Open Planning Questions

- **Data Sources & Scale**
  - Typical PST size: 2,000,000 KB to 5,000,000 KB
  - Expected volume of emails (e.g. millions of messages)
  - Throughput target: ≥1 PST per hour (scalable to more if possible)
- **Performance & Scaling**
  - Target throughput (messages/sec) per thread
  - Memory footprint per batch size
  - Desired latency for small vs. large PSTs
- **Extraction Logic & Heuristics**
  - Signature block definition: lines of plain text only
  - Rules for start/end detection (e.g. detect delimiter lines like "—" or "Regards,")
  - Search scope: Any substring match within a block returns the entire signature
  - Expected false-positive rate and how to tune heuristics
- **Deduplication Criteria**
  - What constitutes a duplicate signature (exact text match, fuzzy match, normalized fields)
  - Mode selection: Allow user to choose between Exact or Fuzzy matching
  - Tolerance for minor variations (e.g. different titles, phone formats)
- **Storage & Search Backend**
  - Target searchable format (SQLite, full-text index, Elasticsearch, etc.)
  - Query patterns (search by name, company, domain)
  - Retention and archival policies
  - Search Backend Comparison (**Planned**)
    - SQLite FTS5
      - Pros: zero-setup, ACID, built-in full-text, single file
      - Cons: limited distributed and concurrent performance
    - Elasticsearch/OpenSearch
      - Pros: distributed scale, rich DSL, REST API
      - Cons: requires separate servers, operational overhead
    - Whoosh
      - Pros: pure-Python, embedded
      - Cons: slower on large data
    - SQLite + JSON blobs
      - Pros: simplicity
      - Cons: only `LIKE` queries, no ranking
    - In-memory custom index
      - Pros: fastest small-scale
      - Cons: volatile, memory-heavy
    - Recommendation: Start with SQLite FTS5; abstract via `SearchIndex` for future ES migration.
- **CLI vs. GUI Requirements**
  - GUI: Python-based desktop application only
  - Command-line support and batch scheduling
- **Platform & Dependencies**
  - Primary OS: Windows (should still run on Linux/macOS)
  - Python version: No strict constraint—use the easiest supported version
  - Third-party libraries: Allowed but kept to a minimum; installers/requirements must be user-friendly for non-technical users
- **Error Handling & Logging** (**Planned**)
  - Layered exception handling at each pipeline stage (I/O, parsing, extraction, dedupe) with recoverable errors logged as `WARNING` and fatal errors as `ERROR`
  - Structured logs (JSON or key-value) including context (`msg_id`, `heuristic_used`, `duration_ms`, `confidence`)
  - Log levels: `DEBUG` for internals, `INFO` for progress, `WARNING` for recoverable skips, `ERROR/CRITICAL` for unrecoverable conditions
  - Handlers:
    - Console (INFO+, DEBUG if `--verbose`)
    - Rotating file handler (all levels)
  - Retries: Exponential back-off for transient I/O errors
  - GUI alerts: Show warnings/errors in a dedicated "Alerts" panel
- **Security & Privacy**
  - Handling of sensitive data (PII) in signatures
  - Access controls on extracted data
  - Data handling: No external data export; all processing is local
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
