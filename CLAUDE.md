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

**Before running any blind skill-validation / double-blind A/B (no_skill vs skill):** read `test/BLIND_TEST_PROTOCOL.md` (Part I neutrality + Part II enforcement) and drive the run through `benchmarks/blind_ab.sh` rather than hand-rolling it — this guarantees per-arm skill isolation, leak scan, auditable artifacts, Option-A cold replay, and write-back to the case's `EXPERIMENT_REPORT.md`. The `blind-ab` skill encapsulates this.

## Conventions for Knowledge Files

When writing or editing a `knowledge/fpv/<module>.md`:

- Imperative voice — "Use X", not "You should use X".
- Decision tree near the top; preserve exact Tcl/SVA syntax and JasperGold flag names; keep all numeric thresholds (cycles, ratios).
- Include an Anti-Patterns section. **Keep every file under 500 lines** (the cap is per file — see Module Structure below).
- **Preserve tool-specific atoms; compress general prose.** When distilling sources, exact command names, flags, and numeric thresholds are the high-value content — a capable model recovers general methodology on its own but cannot derive `setup_ndc` or `set_per_property_simplification`. When something has to be cut to fit, cut the prose, never the atoms.
- Tag tool-specific content `[JG-specific]` / `[VC-Formal-specific]`; keep general FV knowledge portable.
- Flag uncertainty inline: `⚠️ NEEDS VALIDATION` (sources contradict), `📝 GAP` (not in sources), `🔧 VERSION-SENSITIVE` (differs across JasperGold versions).
- Keep each module self-contained — link to sibling modules by name (e.g. `engine-tuning.md`), but do not depend on any non-`knowledge/` file.

## Module Structure: Flat vs. Progressive Disclosure

A module is one of two shapes:

- **Flat** — a single `knowledge/fpv/<module>.md` under 500 lines. Use this when the distilled content fits comfortably (most modules).
- **Progressive disclosure** — when a rich module would exceed 500 lines, split it into a lean **index** (`<module>.md`) plus **sub-topic leaves** (`<module>/<topic>.md`). The index holds the overview, decision tree, core rules, a sub-topic routing table, the cross-cutting anti-patterns, and the consolidated command reference; each leaf holds the full pattern bodies (templates, examples, gotchas) for one technique family. Every file — index and leaves — stays under 500 lines, so the module as a whole can hold far more than 500 lines without any single file blowing the cap. `complexity-management` is the reference example.

SKILL.md routing always points at the index `<module>.md`; the index routes onward to leaves, so adapters need no change when a module is split. Do not force a split prematurely — only split a module that has genuinely outgrown a flat file.

### Source ingestion — figures in PDF and Office docs (build-time)

Source documents carry their highest-value content (SVA/RTL/Tcl snippets, waveforms, state/block diagrams) *inside raster figures*, which markitdown/pdfminer drop 100% of. `scripts/pdf_prep.py` (build-time, local — needs `raw-docs/`, does not ship) recovers them before extraction for **PDF and Office DOCX/PPTX/XLSX**: prose via markitdown, PDF figures via page-render, Office figures via embedded media unzipped from `word|ppt|xl/media/*` and normalized to PNG — then each figure is transcribed to structured Markdown by the vision model configured in `scripts/providers.json` (`roles.figure_transcription`; override with `--provider`). For Office docs the transcriptions are **inlined at each image's original position** in the body (count-matched, else appended); legacy binary `.doc`/`.ppt` aren't zip-based — convert to `.docx`/`.pptx` first. Output lands in `extractions/fpv/<module>/prepared/`.

### Measuring distillation loss (when to split, and what to keep)

The pipeline compresses many sources into the knowledge file — a lossy step. Two local tools measure where that loss actually hurts (build-time only; both need `extractions/`, so neither ships):

- `scripts/loss_probe.py` — content-coverage screen: command/technique tokens present in the extractions but absent from the knowledge file (and from every sibling module). A fast screen that *over-counts* loss.
- `benchmarks/run_scenarios.sh` + `benchmarks/fpv/scenarios.{md,json}` — task-level eval: runs scenarios through a headless agent and grades CONCEPT vs EXACT (tool-specific) tokens separately. This *calibrates* the screen — a dropped token only matters if the model can't supply it itself.

The empirical rule these produced: **loss bites on tool-specific atoms, not general methodology.** When `loss_probe` flags a real on-topic atom and the task eval confirms the miss, restore it — splitting the module into progressive disclosure if the flat file is already at the cap.

## Project State

All five `knowledge/fpv/` modules are synthesized, plus the two `knowledge/shared/` references (`sva-reference.md`, `tcl-common.md`). `complexity-management` is the most mature and is structured as progressive disclosure (index + `complexity-management/` leaves); the other modules are flat and at 🔬 from-docs, needing field validation.
