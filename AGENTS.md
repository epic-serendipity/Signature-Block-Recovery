## Overview

This document defines the agent behavior for using Codex within this repository. It specifies how and when Codex should update the project map file (`PROJECTMAP.md`) to ensure an up-to-date, detailed representation of the codebase and planned deliverables.

## Purpose

* **Ensure consistency**: After any code or documentation change, the agent must update the project map to reflect the current state and structure of the project.
* **Prevent drift**: By maintaining `PROJECTMAP.md`, the team always has a single source of truth for modules, features, and file locations.
* **Facilitate planning**: A clear project map aids in scoping work, onboarding new contributors, and tracking progress at a glance.

## Agent Guidelines

1. **Trigger Point**: Immediately after successfully applying any change (code, documentation, configuration), the agent must:

   * Open `PROJECTMAP.md`.
   * Integrate the changes into the map (new files, modified components, removed modules).
   * Commit the updated `PROJECTMAP.md` alongside the change.

2. **Map Structure**:

   * **Modules**: List high-level components or directories.
   * **Features**: Under each module, enumerate implemented and planned features.
   * **Files**: Provide a bullet entry for each significant file or sub-directory, with a one-line description.
   * **Dependencies**: Note external libraries or services used per module.
   * **Status**: Mark features as `Planned`, `In Progress`, or `Complete`.

3. **Formatting Conventions**:

   * Use markdown headings (`##`, `###`, `####`) to delineate levels.
   * Bulleted lists (`-`) for items; sub-bullets for nested details.
   * Inline code formatting (`` `file/path.js` ``) for file paths and commands.
   * Tables may be used sparingly for status overviews.

4. **Automation & Verification**:

   * Agents should verify that `PROJECTMAP.md` renders without markdown errors (e.g., missing headings or broken lists).
   * Optionally, integrate a CI check that fails if `PROJECTMAP.md` is out of sync after a PR.

## Workflow Example

1. Agent receives prompt to add a new API endpoint `auth/login`.
2. Agent implements changes in `src/api/auth.js` and updates tests in `tests/auth.test.js`.
3. Agent opens `PROJECTMAP.md` and under the `src/api` module:

   * Adds `auth.js` — implements login and token generation (`Complete`).
   * Updates status of `auth` feature to `Complete`.
4. Agent commits both code changes and the updated `PROJECTMAP.md` in one commit.

## Best Practices

* Keep descriptions concise but informative.
* Reflect only the current state—remove or archive outdated entries.
* Maintain chronological clarity: new features append to the bottom of their module section.

## Coding Standards & Guidelines

- **Project Structure & Templates**
  - All Python scripts follow `template.py` layout: shebang, sections (Imports → Logging → Globals → Classes/Functions → `main()`)
  - No inline scripts; use `if __name__ == "__main__":` entry point
- **Logging & Monitoring**
  - Use `log_message(level, msg)` helper for every operational message
  - Log exceptions with full traceback at `ERROR` level
  - Enqueue logs for GUI display when applicable
- **Error Handling & Validation**
  - Wrap PST reads and parsing in `try/except`
  - Validate input paths, memory usage, and PST integrity before processing
  - Fail gracefully with user-friendly messages in GUI or console
- **Dependency Minimization**
  - Avoid heavy third-party libraries; prefer built-in modules (`os`, `re`, `email`)
  - If PST parsing requires external library, wrap it behind a thin abstraction
- **Signature Extraction Module**
  - Expose a clean API: `extract_signatures(pst_path: str) → Iterator[Signature]`
  - Signature objects must normalize whitespace and HTML tags
  - Pluggable heuristics: allow adding new detection rules via a registry
- **Deduplication Module**
  - Provide `dedupe_signatures(signatures: Iterable[Signature]) → List[Signature]`
  - Configurable fuzzy matching thresholds
- **Search & Indexing**
  - Abstract backend behind `SearchIndex` interface (`add()`, `query()`)
  - Allow swapping SQLite FTS or other engine without code changes
- **Tkinter GUI Guidelines**
  - Follow `TemplateApp` styling: consistent frames, fonts, colors
  - Disable “Start Extraction” button while a run is active
  - Display real-time progress and logs in a scrollable text widget
- **Threading & Responsiveness**
  - Offload PST parsing and indexing to a background thread
  - Use `stop_event` to signal cancellation; re-enable UI controls on stop
- **Documentation & Testing**
  - Docstrings for every public function/class
  - Unit tests for extraction and deduplication logic
  - End-to-end tests with sample PST files

---

*This file is intended for internal use by Codex-powered agents to maintain a living project map.*
