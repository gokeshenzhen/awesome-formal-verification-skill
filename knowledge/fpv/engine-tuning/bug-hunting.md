# JasperGold Deep Bug Hunting

> 🔬 **from-docs** — JasperGold-specific operational guidance. Validate commands, defaults, and signoff assumptions against the installed tool release and project policy.

## Overview

Use Deep Bug Hunting (DBH) after a meaningful exhaustive `prove` run leaves targets `undetermined`, or to reproduce a known bug, carry bug-search intent across a regression, or close reachable coverage. DBH searches non-exhaustively for CEX and covered traces; a miss is never proof, unreachability evidence, or signoff closure.

> 🔧 **VERSION-SENSITIVE** — Hunt modes, option availability, built-in defaults, and configuration displays vary across JasperGold releases. Inspect installed-version help and resolved strategy settings before copying a configuration.

## Use-Case Decision Tree

```text
What is the immediate objective?
├─ Undetermined after prove
│  ├─ One expensive frontier cycle ........ cycle_swarm
│  ├─ Uneven complexity over a cycle range  bound_swarm
│  ├─ Useful unordered milestones .......... state_swarm or hunt -auto
│  ├─ Existing valuable traces ............. trace_swarm
│  ├─ Search around whole traces ........... trace_search
│  └─ Known ordered milestones ............. guidepoint
├─ Liveness CEX
│  ├─ Search fixed loop lengths ............ loop_swarm
│  └─ Start from existing traces ........... trace_swarm with liveness-capable engines
├─ Known external bug
│  ├─ Known occurrence window .............. bound_swarm
│  ├─ Bug trace exists ..................... qualify trace; retain hit helpers
│  └─ Ordered failure path known ........... guidepoint
├─ Changed RTL/TB regression ............. history-driven cycle/bound/AUTO portfolio
└─ Critical uncovered item ............... convert to FPV cover; cycle/AUTO/guidepoint
```

## Core Rules and Signoff Boundary

1. Run `prove` first long enough to establish unresolved targets and meaningful bounds. Use Hunt to reduce bug risk, not to replace proof.
2. Accept only CEX and covered traces as DBH outcomes. Do not report a no-hit run as `proven`, `unreachable`, or exhaustive bound closure; most Hunt traces are non-minimal.
3. Select a mode from the complexity shape. Do not respond to every stall by only raising the global time limit.
4. Define named strategies with `hunt -config`; execute them with `hunt -run`. Strategy-local settings inherit unspecified task/global settings but do not propagate back.
5. Keep exploratory over-constraints in a `formal` Hunt strategy. Removed legal behavior invalidates proof/unreachability conclusions even if a local engine reports them.
6. Use resources for diverse cycles, segments, traces, loop lengths, or seeds. Archive tool version, tag, seed, `IHT002` resolved settings, source traces, limits, and results.
7. Store multiple traces selectively. `hunt -force` preserves existing results while seeking more traces; `prove -force` clears existing results.
8. Measure DBH by new CEX/covered traces, trace diversity, coverage movement, and `undetermined` to `covered` transitions. Treat bound movement as mode-dependent supporting data only.

## Mode Selection and Controls

| Mode | Use | Key controls / limits |
|---|---|---|
| `formal` | Search after local over-constraint | `-add_constraint`, optional `-bound`; accept only CEX/covered |
| `cycle_swarm` | Time-box each hard cycle and move deeper | `-first_trace_attempt`, `-max_first_trace_attempt`, `-trace_attempt_time_limit`, `-deeper_cycles_earlier` |
| `bound_swarm` | Rescan a bounded range with growing effort | Above plus `-max_trace_length`, `-trace_attempt_time_limit_factor` |
| `state_swarm` | Chain diverse Engine-L segments through helpers | Requires useful covers; `-tail_length`, `-max_segment_length`, `-segment_time_limit`; no liveness |
| `trace_swarm` | Search from existing or newly produced traces | Any engine; static or dynamic; use tail length to start earlier; supports liveness with suitable engines |
| `loop_swarm` | Find liveness CEX at fixed loop lengths | `-loop_length`, `-loop_length_incr`; a miss covers only tested lengths |
| `simulation` / `<sim_swarm>` | Cheap randomized deep paths | Engines `U*`, `Q*`, `J`; short lengths restart more, long lengths go deeper |
| `trace_search` | Uniform bounded neighborhoods along a few traces | `-target_depth` default `10`; `-interval_cycles` default equals target depth |
| `guidepoint` | Connect an ordered cover path then analyze target | `-path`; make covers cumulative when temporal order matters |
| `hunt -auto` | Generate/select helpers, State Swarm, optional Trace Swarm | `-auto_helper_num`, `-auto_cleanup_time_limit`, `-trace_swarm_ratio`, `-disable_trace_swarm` |

All modes except `trace_swarm` and `trace_search` can start from reset. All modes can start from an existing trace with `-from`.

## Strategy Lifecycle and Reproducibility

```tcl
# Inspect installed-version built-ins before freezing a strategy.
hunt -list strategy
hunt -show -strategy <state_swarm>

# Define once; run from reset.
hunt -config -strategy <name> -mode <mode> \
    -engine_mode {<engines>} -max_jobs <n> -time_limit <time>
hunt -run -strategy <name> -property {<targets>} -tag <unique_id>
# Use "-task <task>" instead of "-property {...}" for a task-wide run.

# Start from one stored trace/cycle; runtime may override jobs/time/seed.
hunt -run -strategy <name> -property {<targets>} \
    -from <source_property> [-trace_id <id>] [-cycle <n>] \
    -max_jobs <n> -time_limit <time> -seed <value>
```

Use a scalar for every job, a positional list for per-job values, or a weighted distribution:

```tcl
{50%:[50..200] 50%:[201..1000]}
```

Record the resolved distribution and seed from `IHT002`; source expressions alone do not identify the values assigned at run time. Use `IHT012` to map work to threads/traces and `IPF031` to inspect proof-engine settings. `IPF047`/`IPF055` can identify cover/CEX hits but may not print for every hit.

> 🔧 **VERSION-SENSITIVE** — One `<state_swarm>` configuration includes `max_jobs 20`, engine `L`, `first_trace_attempt {100%:[3..15]}`, `auto_helper_num 300`, `max_segment_length {100%:[50..300]}`, `auto_cleanup_time_limit 120m`, `segment_time_limit {100%:[100..600]}`, and `tail_length {50%:[1] 30%:[2] 20%:[3..5]}`. Treat these as example values, not portable defaults.

### Isolated Conditional Over-Constraint

Use `formal` mode when a temporary restriction makes a hard state reachable. Release the restriction at the target and keep it released so Hunt explores legal behavior afterward. Accept only CEX/covered results.

```tcl
virtual_net enable_oc
hunt -config -strategy OC -mode formal \
    -add_constraint {enable_oc} -bound 1 \
    -add_constraint {enable_oc && !<target_state> |=> enable_oc} \
    -add_constraint {enable_oc |-> <temporary_restriction>} \
    -add_constraint {enable_oc && <target_state> |=> !enable_oc} \
    -add_constraint {!enable_oc |=> !enable_oc}
hunt -run -strategy OC -property {<targets>}
```

`virtual_net` can clear existing proof results; preserve needed results before creating it.

## Hunt Beyond the Proof Bound

Start with this low-configuration portfolio:

1. Run Cycle Swarm from the lowest bound among undetermined targets. Its predefined flow uses an unlimited maximum trace length and seed-selected per-cycle effort.
2. Run Bound Swarm from that bound through `bound + 100`. A practical baseline starts at `trace_attempt_time_limit 1s` and multiplies effort by `10` per scan.
3. Run `hunt -auto` for state/path diversity. AUTO may remain within the proof bound; inspect helper depths rather than assuming it crossed the frontier.
4. Run modes in parallel when licenses permit; otherwise run sequentially.

```tcl
hunt -config -strategy CS -mode cycle_swarm \
    -first_trace_attempt {10 12 15} -engine_mode B -max_jobs 3
hunt -run -strategy CS -property {<targets>}

hunt -config -strategy BS -mode bound_swarm \
    -first_trace_attempt <bound> -max_trace_length <bound_plus_range> \
    -trace_attempt_time_limit 1s -trace_attempt_time_limit_factor 10
hunt -run -strategy BS -property {<targets>}

hunt -run -auto -property {<targets>} -time_limit <time>
```

Cycle jobs advance by `next_cycle = current_cycle + number_of_engine_jobs`. For `B`, `B4`, or `Hts`, use multiple jobs per start cycle for multiple properties; `-max_first_trace_attempt` defaults to `max_jobs` when omitted and is ignored for MPE. A practical Cycle Swarm timeout range is `5m` to `10m`.

Enable full-range starts when jobs cluster near the lower bound:

```tcl
hunt -config -strategy <name> -mode <cycle_or_bound_swarm> \
    -first_trace_attempt <lo> -max_trace_length <hi> \
    -deeper_cycles_earlier true
```

Capacity-plan Bound Swarm as:

```text
(cycles assigned per engine job) *
(trace_attempt_time_limit * trace_attempt_time_limit_factor ^ scan)
```

Do not copy example budgets as universal thresholds. Example configurations include 100 cycles, `10m`, factor `6`, and three scans; or 100 cycles, 10 jobs, `5m`, factor `2`.

## Helper, Trace, and Guidepoint Steering

Use meaningful, diverse helpers that span depth and are close enough for Engine L to connect, but not so close that no useful target analysis occurs between them.

```tcl
cover -generate -auto -num 1000
cover -generate -auto -property {<target>} -num <n> -seed <seed>
cover -extend -property <cover> -precondition {<expr>}

assert -set_store_trace unlimited {<assertions>}
cover  -set_store_trace unlimited {<covers>}
get_trace_info [get_property_info <property> -list trace_id]
```

For advanced AUTO, start with roughly `50` to `100` user helpers and reduce generated helpers to roughly `50` to `100`; a common reference value is `300`. If helpers do not reach beyond the bound, redefine, target, or extend them.

```tcl
hunt -run -auto -property {<helpers> <targets>} \
    -auto_helper_num 50 -auto_cleanup_time_limit 5m \
    -max_jobs 50 -trace_swarm_ratio 40
```

With 50 jobs and ratio 40, allocate 30 State Swarm and 20 Trace Swarm jobs. Use `-disable_trace_swarm` when only State Swarm is wanted.

### State and Trace Swarm

Interpret State Swarm controls per segment: skip near-start attempts with `first_trace_attempt`; back up from the prior endpoint with `tail_length`; cap forward distance with `max_segment_length`; backtrack on `segment_time_limit` expiry. Do not use State Swarm for liveness.

```tcl
hunt -report -trace_swarm -tag <tag> -pending -silent

# Static: consume traces already stored in the property table.
hunt -run -strategy <trace_swarm_strategy> \
    -from {<source_properties>} -property {<targets>}

# Dynamic: consume traces from a running formal/simulation/state_swarm producer.
hunt -run -strategy <producer> -use_strategy <trace_swarm_strategy> \
    -from {<source_properties>} -property {<targets>}
```

One Trace Swarm configuration uses `{B Ht}`, one SPE plus one MPE, and can analyze liveness. Query pending traces after a timed AUTO run instead of assuming all were consumed.

### Trace Search

```tcl
hunt -config -strategy TS -mode trace_search \
    -target_depth 20 -interval_cycles 10 \
    -max_jobs <n> -time_limit <time> -engine_mode {<engines>}
hunt -run -strategy TS -property {<targets>} \
    -from {<small_meaningful_trace_set>} [-trace_id <id>]
```

Use `-trace_id` only with a single `-property` target. Smaller intervals create more, easier stages; larger intervals create fewer, harder stages. Budget trace count × trace length × stages.

### Guidepoint and Liveness

```tcl
cover -name C1 {<milestone_1>}
cover -name C12 {<milestone_1> ##[0:$] <milestone_2>}
cover -name C123 {<milestone_1> ##[0:$] <milestone_2> ##[0:$] <milestone_3>}
hunt -config -strategy GP -mode guidepoint -path {C1 C12 C123}
hunt -run -strategy GP -property {<target>}

hunt -config -strategy LS -mode loop_swarm \
    -loop_length {5 7 12 17 23}
# Alternative: -loop_length 5 -loop_length_incr 3
# Alternative: -loop_length {40%:[10..20] 60%:[50..75]} -seed $S
```

Make guide covers cumulative: Guidepoint matches first occurrences already in a trace, so independent covers do not enforce requested temporal order.

## Known-Bug Reproduction and Fix Challenge

1. If an external VCD/FSDB/SHM trace exists, confirm it against the current design and environment. Fix assumptions that reject real behavior. Ensure an assertion expresses the failure signature.
2. Use Bound Swarm for a known occurrence window; use helper covers hit by the failing trace or an ordered architectural path for steering.
3. Before the RTL fix, retain/export hit helpers. After the fix, replay those helpers and add `50` to `100` generated helpers for variants.
4. If Hunt does not rediscover the bug, report only added search confidence and continue other modes plus exhaustive proof.

```tcl
# Select exactly one format option: -vcd, -fsdb, or -shm.
visualize -confirm -fsdb <trace_file>
set_trace_optimization standard
visualize -check_props -filter {<assumptions> <assertions> <covers>}

hunt -run -auto -property {<hit_helpers> <target_assertions>} \
    -auto_helper_num 0 -time_limit <time>
# After fix, add diversity:
hunt -run -auto -property {<hit_helpers> <target_assertions>} \
    -auto_helper_num 50 -force -time_limit <time>
```

Use `visualize -load` only when the design is fully coherent with the trace; it is faster but performs no consistency checks. `visualize -check_props` does not support liveness, `assume -reset`, X-Prop, or SPV properties.

## Regression Carryover

Persist `report -csv` and compare status, bound, and proof time with the next regression. Perform this comparison explicitly rather than assuming automatic previous-run analysis.

```tcl
report -csv -file <baseline>.csv
```

| Previous status | Current-run trigger | Action |
|---|---|---|
| `proven` | Near previous prove time, still not proven | Cycle Swarm from current `min_length`; preserve missing proof as a regression failure/signoff gap |
| `cex` | At about `70%` of run, current bound below old CEX depth | Bound Swarm through `previous_cex_bound + N`; choose `N` architecturally because fixes can shift bugs deeper |
| `undetermined` | Alongside prove, or at old bound / about `70%` | AUTO + user helpers, or Cycle/Bound Swarm from previous bound |
| no history tuning | After prove consumes about `50%` | Run Cycle Swarm, Bound Swarm, and AUTO with defaults |

Values such as `+20` cycles and rediscovery at depth `52` are example observations, not universal thresholds.

## Coverage Closure and Progress

Initialize coverage before elaboration when instrumentation/property creation requires it. Measure, identify critical uncovered items, convert them to FPV cover properties, then Hunt those covers. DBH can cover an item; it cannot prove an item unreachable.

```tcl
check_cov -measure
check_cov -list -status Uncovered -silent
check_cov -create_cover_item_property \
    -task {<tasks>} -cover_item_id {<ids>}
# Alternatively select items with -cover_item_name and optionally add
# -include_hierarchies / -exclude_hierarchies.

cover -generate -auto -property {<undetermined_cover>}
hunt -run -strategy <cycle_or_guide_strategy> -property {<covers>}
check_cov -measure -refresh
```

For extended covers, first retain/refresh a trace for the original cover, then continue from it:

```tcl
set_prove_no_cover_traces false
prove -property {<original_covers>} -force
prove -property <extended_cover> -from <original_cover> -bg -max_jobs 1
prove -wait
```

## Anti-Pattern Reference

| Anti-pattern | Why it fails | Correct action |
|---|---|---|
| Treat no Hunt CEX as proof | Search is seed/time/mode dependent and non-exhaustive | Preserve `undetermined`; return to `prove` for signoff |
| Accept proof from local over-constraint | Removed legal behaviors invalidate exhaustive conclusions | Accept only CEX/covered from `formal` Hunt |
| Use State Swarm for liveness | State Swarm does not analyze liveness | Use Loop Swarm or Trace Swarm with suitable engines |
| Run State Swarm without qualified helpers | Engine L cannot build relevant segments | Add meaningful, diverse, properly spaced helpers or AUTO |
| Assume AUTO crosses the proof bound | Generated helpers can remain shallow | Inspect cover depths; use cycle/bound/trace-directed modes |
| Use one random seed | One helper/path sample can miss reachable behavior | Repeat seeds and archive resolved settings |
| Feed every trace to Trace Search | Jobs scale with traces, length, and stages | Select a small, relevant trace set |
| Use independent ordered guide covers | First-occurrence matching can reorder milestones | Make later covers cumulative with `##[0:$]` |
| Discard pending Trace Swarm work | AUTO time can expire with queued traces | Report pending traces and run Trace Swarm separately |
| Keep one trace per valuable property | Loses path diversity | Set selective trace storage to `unlimited` |
| Copy example numeric values as defaults | Many values are testcase or version choices | Inspect built-ins and budget from bounds/resources |
| Call uncovered coverage unreachable | Hunt supplies reachability witnesses only | Use exhaustive proof for unreachability |

## Validation Flags

> ⚠️ **NEEDS VALIDATION** — The effective default and boolean interpretation of `no_cover_traces` can vary by release and context. Verify resolved settings before scripting it.

> ⚠️ **NEEDS VALIDATION** — Engine modes, maximum trace values, and configuration spellings can vary by release or flow. Use installed help and resolved strategy output rather than combining unverified values.

> ⚠️ **NEEDS VALIDATION** — Confirm whether `get_signal_list` uses `-intersect` or `-intersection` in the installed release. Do not use the suspicious `$set` argument form without validation.

> 📝 **GAP** — No portable numeric threshold defines when a Hunt miss provides sufficient residual-risk confidence. Establish project-specific budgets and retain exhaustive signoff criteria.

## Consolidated Command Reference

| Command / option | Purpose |
|---|---|
| `hunt -config -strategy N -mode M` / `hunt -run -strategy N` | Define/run isolated strategies |
| `hunt -list strategy` / `hunt -show -strategy N` | Inspect installed strategies/defaults |
| `hunt -run ... -from P [-trace_id I] [-cycle N]` | Initialize from a stored trace |
| `hunt -run ... -force` / `-tag ID` / `-seed S` | Preserve results / identify / reproduce a run |
| `hunt -run -auto` | Automatic helper + State/Trace Swarm flow |
| `hunt -report -trace_swarm -tag T -pending -silent` | List unconsumed Trace Swarm work |
| `-first_trace_attempt`, `-max_first_trace_attempt` | Set and parallelize initial cycle attempts |
| `-max_trace_length`, `-deeper_cycles_earlier` | Limit/distribute cycle search |
| `-trace_attempt_time_limit`, `-trace_attempt_time_limit_factor` | Set/grow per-cycle effort |
| `-tail_length`, `-max_segment_length`, `-segment_time_limit` | Control State Swarm segments |
| `-target_depth`, `-interval_cycles` | Control Trace Search neighborhood/staging |
| `-loop_length`, `-loop_length_incr` | Select liveness loop lengths |
| `-auto_helper_num`, `-auto_cleanup_time_limit` | Control AUTO helper generation/cleanup |
| `-trace_swarm_ratio`, `-disable_trace_swarm` | Allocate/disable AUTO Trace Swarm |
| `-add_constraint {E} [-bound N]` | Add strategy-local constraint |
| `cover -generate -auto ...` / `cover -extend ...` | Create steering/deeper covers |
| `assert|cover -set_store_trace unlimited ...` | Retain diverse source traces; invoke actual command, not literal pipe |
| `get_property_info ... -list trace_id` / `get_trace_info ...` | Relate traces to properties/runs |
| `visualize -confirm|-load ...` / `visualize -check_props` | Qualify external trace and evaluate properties |
| `report -csv -file F` | Persist regression baseline |
| `check_cov -measure` / `-create_cover_item_property` | Measure and convert coverage targets |

## Further Reading

- For exhaustive engine selection and orchestration, return to `engine-tuning.md`.
- For abstraction, decomposition, and proof closure after DBH, see `complexity-management.md`.
- For end-to-end signoff and regression discipline, see `workflow.md`.
- For helper-cover SVA syntax, see `property-writing.md` and `sva-reference.md`.
