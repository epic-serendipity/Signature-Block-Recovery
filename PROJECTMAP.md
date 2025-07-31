# Project Map

## Modules

### Documentation
- **Features**
  - Quick-start README and project map (**Complete**)
- **Files**
  - `README.md` — quick-start guide
  - `AGENTS.md` — Codex automation rules
  - `PROJECTMAP.md` — project map
  - `.gitignore` — ignore build artifacts and local files

### Signature Recovery Core
- **Features**
  - PST parsing interface (**Complete**)
  - Signature extraction heuristics (**Complete**)
  - Deduplication utilities (**Complete**)
  - Metrics & logging (**Complete**)
- **Files**
  - `signature_recovery/core/models.py`
  - `signature_recovery/core/pst_parser.py`
      - imports `pypff` at module load; consumers must handle `ImportError`
  - `signature_recovery/core/extractor.py`
  - `signature_recovery/core/deduplicator.py`
  - `signature_recovery/core/parser.py`
  - `signature_recovery/core/metrics.py`
      - uses `threading.RLock` to allow nested summaries during dump
  - `signature_recovery/core/logging.py`
  - `signature_recovery/core/config.py`

### Indexing
- **Features**
  - SQLite FTS backend (**Complete**)
- **Files**
  - `signature_recovery/index/search_index.py`
  - `signature_recovery/index/indexer.py` – lazy-imports PST parser to avoid optional dependency

### CLI
- **Features**
  - `recover-signatures` extraction/query/export CLI (**Complete**)
- **Files**
  - `signature_recovery/cli/main.py` – extraction mode handles missing `pypff` gracefully
  - `setup.py` / `pyproject.toml` — entry points
  - `requirements.txt` — placeholder; core deps in `pyproject.toml`, PST support via `[pst]` extra
  - `tests/test_recover_signatures.py`

### GUI
- **Features**
  - `recover-gui` Tkinter interface (**Complete**)
- **Files**
  - `signature_recovery/gui/app.py`
  - `tests/test_recover_gui.py`

### Exporter
- **Features**
  - CSV and JSON exports (**Complete**)
- **Files**
  - `signature_recovery/exporter.py`
  - `tests/test_exporter.py`

### Tests
- **Features**
  - Unit and integration tests (**Complete**)
  - Benchmarks excluded from default runs (**Complete**)
  - Global 300s per-test timeout via `pytest-timeout` (**Complete**)
- **Files**
  - `tests/test_*` — unit tests
  - `tests/benchmarks/` — benchmark suite
  - PST parser tests import the module after injecting fake `pypff`
  - `pytest.ini` — config skips benchmark directory

### CI Configuration
- **Features**
  - Continuous integration tests (**Complete**)
  - Nightly benchmarks (**Complete**)
- **Files**
  - `.github/workflows/ci.yml`
  - `.github/workflows/benchmarks.yml`

### Release
- **Features**
  - Packaging wheels and source distributions (**In Progress**)
  - GUI installers on GitHub Releases (**Complete**)
- **Files**
  - `RELEASE.md`
  - `SignatureRecoveryGui.spec`

### Platform & Dependencies
- **Dependencies**
  - PST parsing via `pypff` is optional; users must install `pypff` themselves (e.g., `conda install -c conda-forge pypff`) and then `pip install signature-recovery[pst]`
  - Development extras `[dev]` provide `pytest`, `pytest-timeout`, and `pyvirtualdisplay` for local testing

## Status

- Repository cleanup of docs, completion scripts, and unused workflows (**Complete**)
