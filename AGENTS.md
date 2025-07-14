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

---

*This file is intended for internal use by Codex-powered agents to maintain a living project map.*
