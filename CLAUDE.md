# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI coding agents when working with this repository.

## What This Project Is

An open-source, **AI-agent-agnostic knowledge base for formal verification** (currently JasperGold FPV). The deliverable is Markdown knowledge, not code. Engineers point any AI coding agent (Claude Code, Codex, Gemini CLI, Cursor) at this repo and it gains deep FPV expertise — SVA property patterns, engine tuning, complexity reduction, TCL scripting, and end-to-end workflows.

There is no build, no test runner, and no linter — the artifacts are Markdown.

## Three-Layer Architecture

The repo separates source-of-truth knowledge from agent- and tool-specific wrappers:

- **`knowledge/`** — Agent-agnostic knowledge in plain Markdown. The single source of truth. `knowledge/fpv/<module>.md` for FPV modules; `knowledge/shared/` for cross-tool reference (SVA, common TCL). Each module file is **self-contained** — it never references any other directory at runtime.
- **`adapters/`** — Thin, per-agent wrappers that are **routers only**. `adapters/claude-code/SKILL.md` is a routing table pointing the agent at the right `knowledge/` file per task type — it contains no actual FPV content. Same idea for `codex/AGENTS.md`, `gemini-cli/GEMINI.md`, `cursor/.cursorrules`.
- **`tool-specific/`** — EDA-tool quirks (`jaspergold/`, `vc-formal/`) kept out of the shared knowledge so general guidance stays portable.

When adding FPV content, edit the `knowledge/` file. Do not duplicate content into adapters — only add a routing row if a new module is introduced.

## Modules

`knowledge/fpv/` covers five modules:

| Module | Covers |
|---|---|
| `property-writing` | SVA property/assertion writing rules and patterns |
| `engine-tuning` | Proof engine selection, configuration, and the state-space-explosion playbook |
| `complexity-management` | Counter abstraction, cutpoints, case splitting, assume-guarantee |
| `tcl-commands` | Tcl language for Jasper + scripting idioms (`-silent`, design/COI queries) |
| `workflow` | End-to-end FPV run-file order (analyze → elaborate → … → prove → report) |

"Validation" is field feedback that moves a module's maturity badge: 🔬 from-docs → ⚠️ needs-validation → ✅ battle-tested.

## Conventions for Knowledge Files

When writing or editing a `knowledge/fpv/<module>.md`:

- Imperative voice — "Use X", not "You should use X".
- Decision tree near the top; preserve exact Tcl/SVA syntax and JasperGold flag names; keep all numeric thresholds (cycles, ratios).
- Include an Anti-Patterns section. Keep total under 500 lines.
- Tag tool-specific content `[JG-specific]` / `[VC-Formal-specific]`; keep general FV knowledge portable.
- Flag uncertainty inline: `⚠️ NEEDS VALIDATION` (sources contradict), `📝 GAP` (not in sources), `🔧 VERSION-SENSITIVE` (differs across JasperGold versions).
- Keep each module self-contained — link to sibling modules by name (e.g. `engine-tuning.md`), but do not depend on any non-`knowledge/` file.

## Project State

All five `knowledge/fpv/` modules are synthesized. `complexity-management` is the most mature; the other four are at 🔬 from-docs and need field validation. `knowledge/shared/sva-reference.md` and `tcl-common.md` are still placeholders.
