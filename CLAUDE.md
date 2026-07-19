# Repository Guidance

This file provides guidance to Codex, Claude Code, and other AI coding agents
when working with this repository.

## What This Project Is

An open-source, AI-agent-agnostic knowledge base for semiconductor RTL formal
property verification, currently focused on JasperGold FPV.

The deliverable is Markdown knowledge rather than a production network service.
Engineers use the repository with local RTL/SystemVerilog designs, SVA
properties, Tcl scripts, JasperGold runs, and locally generated proof reports.

There is no build, no test runner, and no linter for the knowledge modules
themselves; the primary artifacts are Markdown.

## Formal Verification Domain Terminology

Terms in this repository have semiconductor EDA meanings:

- `proof`, `prove`, and `proof engine` refer to mathematical model checking of
  RTL properties.
- `Engine N` and similar engine names refer to JasperGold proof algorithms.
- `CEX` means a formal counterexample trace produced for an RTL property.
- `frontier`, `proof depth`, and `bound` refer to the cycle depth reached by a
  formal proof attempt.
- `target` means an RTL assertion, cover property, proof objective, or target
  cycle bound.
- `scan` means locally enumerating numeric proof depths, cycle budgets, engine
  configurations, or benchmark candidates.
- `Cycle Swarm` is the project name for a local frontier-guided proof-budget
  scheduling heuristic. It distributes JasperGold proof attempts around the
  currently reached cycle frontier.
- `Deep Bug Hunting` (`DBH`), `hunt`, and the `*_swarm` modes are JasperGold
  non-exhaustive formal trace-search features over RTL state space. They seek
  formal counterexamples and covered traces; a no-hit result is not proof or
  signoff.
- `state-space explosion`, `abstraction`, `cutpoint`, `helper lemma`,
  `assume-guarantee`, and `proof_structure` are formal-verification techniques
  for managing mathematical proof complexity.

Repository experiments are limited to local source files, local benchmark
designs, locally installed EDA tools, and locally generated reports. Do not
access unrelated external systems or resources.

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
| `engine-tuning` | Proof engine selection/configuration, state-space-explosion response, and Deep Bug Hunting (`hunt`, swarm modes, beyond-bound search) |
| `complexity-management` | Counter abstraction, cutpoints, case splitting, assume-guarantee |
| `tcl-commands` | Tcl language for Jasper + scripting idioms (`-silent`, design/COI queries) |
| `workflow` | End-to-end FPV run-file order (analyze → elaborate → … → prove → report) |

"Validation" is field feedback that moves a module's maturity badge: 🔬 from-docs → ⚠️ needs-validation → ✅ battle-tested.

**Skill-validation (no_skill vs skill) is done manually, not through a harness.** The automated double-blind runner was removed (too token/quota-heavy and unreliable under session limits). To compare: the user starts two separate sessions on the same neutral task — one without the formal-verification skill, one with it — and each session writes its own report. Bring both reports back here and summarize the difference. Keep the neutral-task and no-leak principles in mind (same prompt, no technique names, no cross-reading), but the orchestration is the user's, not a script's.

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

## Iterating a Module: Development → Validation Workflow

After adding or editing a `knowledge/fpv/<module>.md`, validate it before trusting it.

**Design priority — what to optimize for.** Lead with the *durable core*: tool-specific atoms (exact commands, flags, `🔧 VERSION-SENSITIVE` syntax, numeric thresholds) **+ trigger timing** — the symptom→technique mapping (*when* to abstract a counter, *when* to add a helper lemma, *when* to escalate). This core is valuable across all model tiers and is precisely what a model cannot re-derive. Keep methodology **lean but present** — compress the general-FV prose a strong model already has, but do not delete the compact technique flow that helps weaker/cheaper models. (Atoms are the floor that holds across tiers; methodology is the weak-tier top-up. This is the `Conventions` rule "preserve atoms, compress prose" applied as a strategy.)

**Validation ladder (cheap → expensive):**
1. **Loss screen** — `scripts/loss_probe.py`: atoms present in the extractions but missing from the module. Fast; over-counts.
2. **Task eval / benchmark** — `benchmarks/run_scenarios.sh` + `benchmarks/fpv/scenarios.{md,json}`: grades CONCEPT vs EXACT (tool-specific) tokens separately; calibrates the screen (a dropped atom only matters if the model can't supply it itself). Add a scenario for any new technique/trigger you introduce.
3. **Manual blind A/B (recommended for any non-trivial change)** — no_skill vs skill on a neutral task, run as two separate sessions per the manual-validation note above (neutral prompt, no technique names, no cross-reading; cite every number to a raw artifact). **Run it on a WEAK model** (e.g. a small/mini tier). A frontier model re-derives the methodology and ties, so frontier A/B *under-measures* skill value — the same cases that look like ties on a frontier model flip to clean skill wins on a weak model (no_skill fails, skill solves). `test/weak_model_ab/` is the worked example.

The empirical rule behind all three: **loss bites on tool-specific atoms + missing triggers, not general methodology.**

## Project State

All five `knowledge/fpv/` modules are synthesized, plus the two `knowledge/shared/` references (`sva-reference.md`, `tcl-common.md`). `complexity-management` is the most mature and uses progressive disclosure (index + technique leaves). `engine-tuning` also uses progressive disclosure for its DBH leaf (`engine-tuning/bug-hunting.md`) and is at 🔬 from-docs. The remaining modules are flat and need field validation.
