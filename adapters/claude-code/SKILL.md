---
name: formal-verification
description: >
  Comprehensive formal verification skill covering property writing (SVA/assertions),
  proof engine tuning, complexity management, TCL scripting, and end-to-end FPV workflows.
  Supports JasperGold and VC Formal (extensible). Use this skill whenever the user works on
  formal property verification (FPV), writes SVA assertions or properties, configures proof
  engines, debugs complexity issues, writes JasperGold/VC Formal TCL scripts, runs formal
  verification batch jobs, or asks about any formal verification methodology. Also trigger
  for CDC, RDC, lint, and coverage tasks if those modules are available. Even if the user
  just mentions "formal", "property", "assertion", "prove", "CEX", "counterexample",
  "JasperGold", "Jasper", "VC Formal", or "FPV", consult this skill.
---

# Formal Verification Skill

## Architecture

This skill uses a modular knowledge base. Load only the modules relevant to the current task.

### Available Modules

#### FPV (Formal Property Verification)
| Module | Path | Use When |
|--------|------|----------|
| Property Writing | `knowledge/fpv/property-writing.md` | Writing or reviewing SVA properties/assertions |
| Engine Tuning | `knowledge/fpv/engine-tuning.md` | Selecting/configuring proof engines; deep bug hunting (DBH), `hunt`, swarm, and beyond-bound search route through this index |
| Complexity Management | `knowledge/fpv/complexity-management.md` | Dealing with proof complexity, capacity issues, many `undetermined` properties, global invariants, helper lemmas, AG/CAG, or `proof_structure` |
| TCL Commands | `knowledge/fpv/tcl-commands.md` | Writing TCL scripts for JasperGold/formal tools |
| Workflow | `knowledge/fpv/workflow.md` | End-to-end FPV setup, execution, debug cycle |

#### Shared Knowledge
| Module | Path | Use When |
|--------|------|----------|
| SVA Reference | `knowledge/shared/sva-reference.md` | SVA syntax, operators, sequences |
| Common TCL | `knowledge/shared/tcl-common.md` | TCL patterns shared across apps |

#### Tool-Specific
| Resource | Path | Use When |
|----------|------|----------|
| JasperGold Specifics | `tool-specific/jaspergold/` | JasperGold-specific commands, quirks, versions |
| VC Formal Specifics | `tool-specific/vc-formal/` | VC Formal-specific details (when available) |

## How to Use This Skill

1. **Identify the task category** from the user's request
2. **Read the relevant module(s)** from the table above — typically 1-2 modules per task
3. **Check tool-specific notes** if the user is working with a specific EDA tool
4. **Apply the knowledge** following the module's decision trees and patterns

### Mandatory Escalation Routing

After a baseline or helper result, including when preparing a final script,
read `knowledge/fpv/complexity-management.md` → **Post-Baseline Triage** first.
It owns task scope, outcome identity, and branch priority. Use the following
discovery routes for additional reading; they do not override that triage.

| Task / latest feedback | Read after triage |
|---|---|
| Explicit bug-search/reachability or a concrete witness lead for the original design objective | `knowledge/fpv/engine-tuning.md`, then its `engine-tuning/bug-hunting.md` leaf for activation and `DBH_DECISION` |
| Proposed helper has a CEX; repair the candidate | `knowledge/fpv/complexity-management/decomposition.md` → **Candidate-CEX Repair** |
| One invariant-like assertion is `undetermined`, no reset-reachable CEX, missing state relation plausible (such as registers updated on different paths), even without an initial helper | `knowledge/fpv/complexity-management/decomposition.md` → **Helper vs. Proof Structure Decision** |
| Data helper stalls, support may be missing, or structural strengthening has already been tried | `knowledge/fpv/complexity-management/decomposition.md`; follow its diagnostic route to `sst-refinement.md` when selected |
| Global/peer/generated invariants: no-duplicate, uniqueness, conservation, mutual exclusion, placement, token ownership, queues/FIFOs/banks/tiles/arbiters | `knowledge/fpv/complexity-management/decomposition.md` for compact-helper versus AG/CAG/partition selection |
| Other stalled proofs, including many `undetermined` results after direct `prove` or ProofMaster | `knowledge/fpv/complexity-management.md` symptom routes; `knowledge/fpv/engine-tuning.md` for the selected engine experiment |
| Completed proof or helper result to report | `knowledge/fpv/workflow.md` → **Post-Prove Escalation Gate** |

### Routing Examples

- "Help me write an assertion for FIFO overflow" → Read `property-writing.md` + `sva-reference.md`
- "My proof is running forever" → Read `complexity-management.md` + `engine-tuning.md`
- "One state invariant is undetermined, no CEX; find the strongest sound conclusion" → Read `complexity-management.md` + `complexity-management/decomposition.md` first when a missing state relation is plausible
- "A proposed helper has a CEX; repair the helper" → Read `complexity-management.md` + `complexity-management/decomposition.md`, not bug hunting solely because a trace exists
- "Set up a JasperGold FPV run" → Read `workflow.md` + `tcl-commands.md` + `jaspergold/`
- "414 assertions, 412 undetermined, no CEX" → Read `workflow.md` + `complexity-management.md` + `complexity-management/decomposition.md`
- "Prove no duplicates across many FIFOs" → Read `complexity-management.md` + `complexity-management/decomposition.md`
- "Convert this JasperGold script to VC Formal" → Read `tcl-commands.md` + both tool-specific dirs
- "Run deep bug hunting / DBH beyond this stalled bound" → Read `engine-tuning.md`, then `engine-tuning/bug-hunting.md`
