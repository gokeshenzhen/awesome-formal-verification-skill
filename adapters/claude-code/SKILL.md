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

When a JasperGold baseline leaves an assertion `undetermined` and the task asks
for the strongest conclusion, a falsification witness, deeper reachability, or
risk investigation, read `knowledge/fpv/engine-tuning.md` and
`knowledge/fpv/engine-tuning/bug-hunting.md` before writing the next run. Apply
the leaf's DBH activation gate: distinguish one focused bounded deepening from
an actual Hunt strategy, and do not label the former as DBH.

When a JasperGold/formal run leaves many properties `undetermined` after a sane
direct `prove`, do not continue only with longer time limits, engine racing,
ProofMaster, or ad-hoc local helpers. Read `knowledge/fpv/complexity-management.md`.

If the hard assertions are global invariants over many peers or generated
instances — especially no-duplicate, uniqueness, conservation, mutual exclusion,
placement, token ownership, queues/FIFOs/banks/tiles/arbiters — also read
`knowledge/fpv/complexity-management/decomposition.md` before choosing the next
proof shape. Treat these labels as routing triggers, not as a mandatory CAG
choice; the decomposition decision tree selects a proven compact helper or
`proof_structure` AG/CAG/partition and defines the required signoff gate.

### Routing Examples

- "Help me write an assertion for FIFO overflow" → Read `property-writing.md` + `sva-reference.md`
- "My proof is running forever" → Read `complexity-management.md` + `engine-tuning.md`
- "Set up a JasperGold FPV run" → Read `workflow.md` + `tcl-commands.md` + `jaspergold/`
- "414 assertions, 412 undetermined, no CEX" → Read `workflow.md` + `complexity-management.md` + `complexity-management/decomposition.md`
- "Prove no duplicates across many FIFOs" → Read `complexity-management.md` + `complexity-management/decomposition.md`
- "Convert this JasperGold script to VC Formal" → Read `tcl-commands.md` + both tool-specific dirs
- "Run deep bug hunting / DBH beyond this stalled bound" → Read `engine-tuning.md`, then `engine-tuning/bug-hunting.md`

## Key Principles

1. **Formal verification is exhaustive** — unlike simulation, it proves properties hold for ALL inputs. Guide users to leverage this strength.
2. **Complexity is the enemy** — most FPV failures are capacity issues, not property errors. Always consider complexity implications.
3. **Properties should be meaningful** — a proven trivial property gives false confidence. Push for properties that capture real design intent.
4. **Incremental verification** — start simple, add complexity gradually. Don't try to prove everything at once.
5. **Tool awareness** — know the specific tool's strengths and quirks. Check `tool-specific/` when in doubt.
