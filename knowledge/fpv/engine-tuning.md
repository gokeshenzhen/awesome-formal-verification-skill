# FPV: Engine Tuning

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation. Content is [JG-specific] unless noted.

## Overview

How to pick, combine, and tune JasperGold proof engines, and how to react when a proof stalls. Default to Proof Orchestration; reach for manual engine selection and the state-space-explosion playbook when convergence fails. Consult this module when a property won't converge, a proof runs too long or runs out of memory, or you need to choose engines for a specific objective (proof vs trace vs bounds signoff).

## Quick Decision Tree

```
Proof not converging / choosing engines?
├─ First run / don't know what to use? ......... leave Proof Orchestration ON (default)
│
├─ Pick engine by OBJECTIVE (orchestration off / manual):
│   ├─ Want PROOFS .......................... N, Tri  (also Hp, Hps, AM, C, I, R)
│   ├─ Want TRACES / CEX .................... B, Hts  (also Ht, L, U)
│   ├─ Liveness / infinite covers .......... M, N    (H does them one-by-one; J/K/L/Q3/U/U2/Oh/Tri IGNORE liveness)
│   ├─ Complex sequential (datapath/credit)  G/G2 or C/C2
│   ├─ Analysis region too complex ......... C, C2, I  (incremental COI)
│   ├─ Deep/hard covers (bug hunting) ...... L  (or `hunt`)
│   ├─ Bounded proofs ...................... K
│   ├─ First-pass / constraint dev ......... J, U, U2, Q3 (sim; run on property-free env)
│   └─ Minimal / quiet traces .............. TM (+prefer_shortest) / QT (QuietTrace)
│
├─ Proof STALLED? → State-Space Explosion playbook (see table)
│   └─ switch engine mode  OR  reduce complexity (abstract counters/FIFOs, stopats, decompose)
│
├─ Hard case, many cores? ...................... distributed BMC (B/Bm); multi-core proof (M, 2025.03)
├─ Repeated regression on evolving RTL? ........ ProofMaster / PPD (consecutive-run learning)
└─ Bounds signoff? ............................. COV meaningful bounds → push/aggregate → bounded_proven
```

## Core Rules

1. **Proof Orchestration is ON by default — keep it on for most work.** It dynamically adjusts engine selection, per-property time limits, and license use, respecting your max jobs/licenses and global time limits. Disable it only for single-pass runs or a known-good engine set.
2. **Orchestration treats your settings as hints, not hard constraints.** With `set_engine_mode {list}` it only chooses from your list (dynamically); `set_engine_mode auto` lets it choose freely. For strict control, turn orchestration off.
3. **Match the engine to the objective.** Proof-finding and trace-finding engines are different — using a trace engine (B/J/K/L) to find an exhaustive proof never converges (they only give CEX or bounded proofs).
4. **Run multi-engine / multi-job proofs on REMOTE hosts (ProofGrid).** Many engines/jobs in local mode overload the machine → poor performance or OOM crashes.
5. **With orchestration off, the default Engine Race is `{Hp Ht N B}`** — the best mode to find the first functional bugs / missing input constraints and build the analysis region.
6. **`set_engine_mode` is global to all tasks.** For task-specific engines, set the mode sequentially before each `prove -task`.
7. **Detect state-space explosion early and act** (switch mode OR reduce complexity). Don't wait out a >24h run — likelihood of completion is slim.
8. **Keep an invariant producer in the mode.** Only Mp/M/N/AM *produce* invariants; Mp/Hp/M/N/AM/Hps can *import* them. Invariant import (on by default under orchestration) speeds convergence but is scoped to the current `prove`.
9. **Abstract counters/FIFOs in the COI.** High cycle counts with constant inter-attempt runtime ⇒ counters in the analysis region — detect with `get_design_info` / `abstract -counter -find`.
10. **Use ProofMaster for repeated proofs on an evolving design** — expect partial (never 100%) cache restoration after RTL/env/property changes.

## Pattern Catalog

### Single-pass with a fixed engine for a fixed time
**When to use**: same engines for a predefined duration (orchestration varies them, so disable it).
**Template**:
```tcl
prove -property {P1 P2 P3} \
  -orchestration off \
  -engine_mode B \
  -per_property_time_limit_factor 0 \
  -per_property_time_limit 12h
```
**Gotchas**: `per_property_time_limit_factor 0` makes each single-property engine analyze each property exactly once for the given time.

### Focus on a known-good engine set
**When to use**: prior knowledge says a set converges well; can beat orchestration's dynamic learning.
**Template**:
```tcl
prove -task my_task \
  -orchestration off \
  -engine_mode {AM I} \
  -per_property_time_limit 15m
```
**Gotchas**: pair manual engine choice with a manual per-property time limit when you know typical prove time.

### Parallel bug-hunting instances via ProofGrid
**When to use**: deep cover/CEX search; run several instances of L racing with B/D.
**Template**:
```tcl
set_engine_mode {B L D}
set_proofgrid_per_engine_max_jobs 3   ;# launches 3 instances each; they engine-race together
prove -task ...
```
**Gotchas**: multiple L instances collaborate; the tool runs `<number-1>` extra jobs beyond the session. Keep it remote.

### Capture a custom engine from orchestration
**When to use**: persist an orchestration-derived configuration for reuse across runs.
**Template**:
```tcl
custom_engine -show              ;# retrieve the portable code_string
custom_engine -add <code_string>
set_engine_mode <custom>
```
**Gotchas**: the `code_string` is portable across runs; also discoverable via "custom engine code" log messages.

### Detect & abstract counters causing explosion
**When to use**: high cycle counts with roughly constant inter-attempt runtime.
**Template**:
```tcl
get_design_info -property <prop> -list counter   ;# list counters relative to a property
abstract -counter -find                          ;# list + abstract counters in analysis region
visualize -property <prop>                       ;# inspect the analysis region / structures
```
**Gotchas**: counters/FIFOs in the COI are prime abstraction targets — see `complexity-management.md`.

### Bounds signoff (assert bound + aggregation)
**When to use**: bounded-proof signoff to a meaningful target per property.
**Method**: (1) define meaningful coverage so the COV App yields meaningful target bounds (auto min bound → manual refine); (2) push bounds until `min_length >= target_bound` → property becomes **bounded_proven**.
**Template**:
```tcl
set_prove_stop_on_target_bound on   ;# stop engines on a property once its target bound is hit (default OFF)
```
**Gotchas**: Bound Aggregation lets independent engines (from `prove` and `hunt`) mark cycles/ranges complete across runs; the assert bound must be deep enough to include the deepest covered item in the COI.

### Extended coverage in a functional context
**When to use**: force a cover to be observed within a pre/post-condition context.
**Template**:
```tcl
cover -extend -property {cover property list} \
  -precondition  {expression} \
  -postcondition {expression}
```
**Example**:
```tcl
cover -name count3 {count=='d3}
cover -extend {count3} -precondition {count=='d7} -postcondition {count=='d0}
```
**Gotchas**: plan extensions as a team whiteboard exercise capturing high-level state (FSM states, queue levels, counter values, interrupts).

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| Many engines/jobs in **local** mode | Overloads machine → poor perf or OOM crash | Run multi-engine/job proofs on remote ProofGrid hosts |
| Trace engine (B/J/K/L) to find an exhaustive **proof** | These never find proofs (only CEX/bounded) | Use proof engines N/Tri/Hp/M/N/AM |
| Expecting orchestration to strictly honor `set_engine_mode`/time limits | Orchestration treats them as hints | Disable orchestration for strict single-pass/focused runs |
| Letting a proof run >24h hoping it converges | Completion likelihood is slim | Stop early; switch engine mode per the symptom table |
| Leaving counters/FIFOs in the analysis region | State-space explosion; constant inter-attempt time | Detect (`get_design_info`/`abstract -counter -find`) and abstract |
| Combining incompatible engines (Hp/Ht/Hps/Hts with H) | Not allowed | Don't combine the H-family variants with H |
| No invariant producer (Mp/M/N/AM) in the mode | Nothing produces invariants → no invariant-import speedup | Include at least one producer engine |
| Expecting 100% ProofMaster cache restoration after changes | "Small" changes can be big for engines | Expect partial restoration; PPD applies past-good strategies |
| Assert bound shallower than the deepest covered item | Coverage unreachable within bound → invalid signoff | Make the bound deep enough; verify the coverage model first |
| Engines grinding on already bounded-proven properties | Wastes compute past the target | `set_prove_stop_on_target_bound on` |

## State-Space Explosion Playbook

| Symptom | Action |
|---|---|
| Proof running **out of memory** | Switch engine mode OR abstract queues/FIFOs/counters in the analysis region |
| **"Ran out of gates"** on engine D/AD/I | Try `set_engineD_optimization high`; if not on D/AD/I, reduce complexity (stopats, black boxing, assumptions, helper properties) or pick another engine |
| Proof running **>24 hours** | Stop; switch mode — C/C2 in place of G/G2, or I in place of D/H |
| **Inter-attempt runtime >1000s and rising** | Stop; switch mode — G/G2 in place of H/D |
| **Per-cycle structure size huge** (e.g., 2,000,000 on G; 100,000 on D) | Switch mode or reduce complexity (abstract FIFOs/counters) |
| `get_design_info` shows a signal **structure size >500** (e.g., `cur_state[0] has size 1234`) | Abstract that complex structure (e.g., a large mux) |
| **High cycle counts, constant inter-attempt time** | Counters in the analysis region — detect with `get_design_info` / `abstract -counter -find`, then abstract |

## Reading the Bound Column (`get_property_info -list min_length/max_length`)

| Proof Status | Bound | Meaning |
|---|---|---|
| unprocessed | `1-` | not yet processed |
| undetermined | `7-` | if a trace exists it is ≥ 7 cycles |
| undetermined | `4-21` | minimal trace length is within this interval |
| cex | `18` | minimal-length trace found, 18 cycles |
| cex | `24- … 32600` | shortest trace ≥ 24 (min_length); ≤ 32600 (max_length) |
| proven | Infinite | no trace exists |
| covered | `18` | minimal-length cover trace, 18 cycles |
| unreachable | Infinite | no trace exists |

For undetermined liveness/infinite covers the bound shows `proof_effort` in parens (e.g., `(17)`); looping traces show `stem+loop` (e.g., `17 + 20`).

## Engine Cheat-Sheet (objective · concurrency · liveness)

| Engine | Focus | Notes |
|---|---|---|
| H | proofs+CEX, multi-prop concurrent | first-pass; safety concurrent, liveness one-by-one; can't combine with Hp/Ht/Hps/Hts |
| Hp / Hps | proofs (multi / single) | import invariants; Hps skips failed attempts; combine Hps with a trace engine |
| Ht / Hts | CEX (multi / single) | collaborate with Hp; Ht supports prefer_shortest |
| B / Bm | CEX/bounded (single / multi) | never exhaustive proof; builds analysis region; Bm supports prefer_shortest |
| B4 | CEX | ML-inferred B config; respects B settings except engine_threads |
| D | proofs+CEX, sequential | complements H first pass; on-the-fly compression; `set_engineD_optimization` |
| I | proofs+CEX, sequential | iterative COI inclusion; combine with C/C2/K/N |
| G / G2 | complex sequential | datapath credit/token; static\|dynamic\|adaptive ordering |
| C / C2 | complex sequential | like G but incremental COI; combine with I/K/N |
| J | traces, multi-prop concurrent | fastest sim, lowest memory; may "give up"; ignores liveness; prefer U/U2 for coverage |
| K | bounded proofs / traces | one prop at a time; exchanges with C/I/N |
| L | bug-hunting deep search | parallel instances via ProofGrid; non-minimal traces; ignores liveness |
| M / Mp | full proofs, sequential / multi | best on small COI, few non-pin constraints; liveness OK; produce+import invariants |
| N | full proofs, sequential | like M, less COI-limited; combine with C/I/K; best for proofs |
| Oh | proofs+unreachables, multi-prop | no CEX/cover traces; low memory; used by orchestration |
| Q3 | non-exhaustive search | solves constraints per cycle; never "gives up"; sanity traces; ignores liveness |
| R | proofs, multi-prop | M-like strategy; auto-restart with longer timeouts |
| Tri | one prop, multi-process (default 8) | non-minimal traces; best for proofs |
| U / U2 | constrained-random sim | overcome deep latencies/dead ends; U2 SAT-based multi-prop |
| TM / QT | minimal / quiet traces | TM runs outside engine race; QT needs soft constraints in COI |
| AB/AG/AM/AD | abstraction (of B/G/M/D) | gradual flop/gate addition (auto Design Tunneling); good for big COI / small witness; AM produces+imports invariants |
| W* (WHp,WB,WA1-3,…) | word-level | C2RTL App only; WA2 for multipliers; WECX1/2 for structurally-similar design compare |

## Tool-Specific Notes

### JasperGold
- **ProofMaster** (push-button: Proof Orchestration + Proof Cache + Proof Profiling Data) reuses historical proof knowledge across runs for faster convergence/deeper bounds. Off by default; enable with `set_proofmaster on`. Benchmark: ~2.95X repeat-run speedup. Compatible only with `prove`, `check_sec/spv/conn/csr/unr/xprop -prove`, `check_cov -measure`, `hunt -run`.
- **FormalAI / adaptive orchestration**: proof-stagnation detection (2024.03+) lets orchestration switch HL strategy mid-proof (e.g., to bug hunting). 🔧 VERSION-SENSITIVE
- **Engine Algorithm Selection** (`set_engine_algorithm_selection train|infer|auto`) trains onsite ML models to infer better-than-default configs for engines B, N, M, AM.
- **Solvers**: standard `solverE`; alternate `solverF` (helps the SEC App) via `set_engine_solver`.
- 🔧 VERSION-SENSITIVE — Multi-core engine M parallel proof (~8X on 48 cores) and Memory-Aware Proofs are roadmap items dated 2025.03 / "Restricted". Verify against the installed version before relying on them.

### VC Formal
> 📝 GAP — No VC Formal engine content in the current sources. To be added.

## Command Reference
| Command | Purpose | Tool |
|---|---|---|
| `set_prove_orchestration on\|off` / `prove -orchestration on\|off` | global / per-proof orchestration (default on) | JG |
| `set_engine_mode {ENGINES}` / `auto` / `-auto N` / `default` | choose engine mode (global to tasks) | JG |
| `prove -engine_mode {...}` / `prove -engine` | override mode for one proof | JG |
| `set_engine_algorithm_selection train\|infer\|auto` (+`_dir`) | ML engine config (B,N,M,AM) | JG |
| `custom_engine -show\|-add\|-remove` | portable custom engines | JG |
| `set_prove_invariants_import on\|off` | invariant sharing (default on w/ orchestration) | JG |
| `set_proofmaster on\|off` (+`_dir`/`_initial_dir`/`_max_data_age`) | ProofMaster enable & data mgmt | JG |
| `set_prove_cache_max_jobs` / `set_prove_cache_job_mode` | parallelize/distribute cache jobs | JG |
| `set_proofgrid_per_engine_max_jobs <n>` (+`_local_jobs`) | spawn engine instances (remote) | JG |
| `set_proofgrid_max_jobs` / `_max_local_jobs` / `_mode` / `_manager on` | ProofGrid job caps / mode / manager | JG |
| `set_proofgrid_engine*_max_jobs` (J,L,Q3,U,U2) | per-engine job control | JG |
| `prove -per_engine_max_jobs` | override per-engine jobs (works w/ `prove -bg`) | JG |
| `set_engine_threads <1-8>` | threads/engine (default 1; helps B/Ht/L) | JG |
| `set_engine_solver solverE\|solverF` | choose SAT solver | JG |
| `set_engineD_optimization standard\|high` | extra D/I optimizations | JG |
| `set_engineC_optimization` / `set_engineG_optimization static\|dynamic\|adaptive` | var ordering C/C2/G/G2 | JG |
| `set_engineCG_max_mem <MB>` | C/G memory cap (default 4096MB) | JG |
| `set_engineM_optimization` | faster M proofs (default on) | JG |
| `set_engineJ_migrate on` / `_single_property` / `_attempts` / `_restarts` / `_max_trace_length` | engine J tuning | JG |
| `set_engineL_*` (cache, seed, max_segment_length, state_removal lru\|fifo) | engine L tuning | JG |
| `set_engineU_max_trace_length` (100) / `set_engineU2_*` (200) / `set_engineQ3_*` | U/U2/Q3 tuning | JG |
| `set_first_trace_attempt N` / `set_engineB_first_trace_attempt` | start trace search at length N | JG |
| `set_max_trace_length` | stop proof at depth (bounded-proof-like) | JG |
| `set_prove_time_limit` (default 24h) / `set_prove_per_property_time_limit` (default 1s) | proof / per-property limits | JG |
| `set_prove_per_property_max_time_limit[_factor]` | wall-clock per-property cap / progression | JG |
| `set_prove_prefer_shortest on` / `prove -prefer_shortest` | strong bounds (needs Ht or Bm) | JG |
| `set_prove_prefer_quiet on` / `prove -prefer_quiet` | quiet traces (engine QT) | JG |
| `set_proven_directive true\|false` / `prove -with_proven` | proven props as assumptions (order matters) | JG |
| `set_prove_stop_on_target_bound on` | stop on target bound (default off) | JG |
| `cover -extend -property {...} -precondition {} -postcondition {}` | extended coverage | JG |
| `get_property_info -list min_length\|max_length\|trace_length\|proof_effort` | bounded-proof / progress info | JG |
| `get_design_info -property <p> -list counter` | structure/counters in analysis region | JG |
| `abstract -counter -find` | list & abstract counters | JG |
| `set_prove_verbosity 7` | insight into orchestration | JG |

## Further Reading
- For abstraction, cutpoints, case splitting, helper properties (the responses to state-space explosion): see `complexity-management.md`
- For property authoring that determines which engines apply (liveness vs safety): see `property-writing.md`
- For the broader set of Tcl commands: see `tcl-commands.md`
- For end-to-end signoff (bounds signoff, regression flows): see `workflow.md`
