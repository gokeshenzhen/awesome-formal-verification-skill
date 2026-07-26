# JasperGold Deep Bug Hunting

> 🔬 **from-docs** — JasperGold-specific operational guidance. Validate commands, defaults, and signoff assumptions against the installed tool release and project policy.

## Overview

Use Deep Bug Hunting (DBH) after a meaningful exhaustive `prove` run leaves targets `undetermined`, or to reproduce a known bug, carry bug-search intent across a regression, or close reachable coverage. DBH searches non-exhaustively for CEX and covered traces; a miss is never proof, unreachability evidence, or signoff closure.

> 🔧 **VERSION-SENSITIVE** — Hunt modes, option availability, built-in defaults, and configuration displays vary across JasperGold releases. Inspect installed-version help and resolved strategy settings before copying a configuration.

## Mandatory Post-Run Gate

After every capped trace-oriented run, stop before writing the next Tcl. Fill
this record from raw logs and the task's wall-time policy:

```text
DBH_DECISION
objective = proof_closure | bug_search | mixed
first_trace_attempt = <cycle | none>
last_trace_attempt = <cycle | none>
candidate_cycles = <few explicit cycles | none>
fallback_depth_shape = none | broad | sparse | unknown
elapsed_wall = <all Jasper process wall time counted by task policy>
remaining_wall = <task budget - elapsed_wall>
reserved_hunt_wall = <nonzero for bug_search/mixed | 0 means stop>
next_action = focused | cycle_swarm | bound_swarm | proof_closure
```

Apply these hard gates:

1. Use `proof_closure` only for an explicit proof/signoff-only request, `bug_search` for falsification/risk, and `mixed` when asked for the strongest sound conclusion under a finite budget.
2. Count every completed exploratory or discarded Jasper process; use process wall time, not `-time_limit` or slot-seconds. Apply explicit task policy to setup failures.
3. For `bug_search` or `mixed`, unchanged first/last `Trace Attempt` is an exact-cycle stall. Run `cycle_swarm` first when `candidate_cycles` is nonempty; otherwise use `bound_swarm` for broad/sparse/unknown depth. Do not select generic `prove`/orchestration.
4. Treat `-max_trace_length` as a ceiling, not a scheduler over adjacent cycles. In Cycle Swarm, set `-max_first_trace_attempt` to the parallel attempt-group count, never to a cycle.
5. Permit one focused B/Hts probe only for a deterministic singleton or cheap justified interval; include reset/SVA sampling ambiguity. Put several candidates in `candidate_cycles`; classify input-dependent strides/skips as the fallback.
6. After one focused miss/stall, execute the named Hunt next. After a candidate Cycle Swarm miss, use its declared fallback only if budget remains. Never spend `reserved_hunt_wall` on proof closure; if the selected run cannot fit, report partial exploration.

## DBH Activation Gate

Complete these trace-first steps, then apply `DBH_DECISION`:

1. Inventory current-session CEX/covered status, `trace_length`, and `trace_id`; a prior report is not a usable trace.
2. Rank traces by target relevance, remaining suffix, and source-cone cost, not length alone; recreate and re-query a missing source under the same RTL/reset/environment/assumptions.
3. If one legal trace removes a relevant prefix, run a declared capped `prove -from` probe with expected suffix/progress criteria. Stop on CEX; no-hit stays `undetermined`; missing trace or command failure is setup failure.
4. If a generic source makes no quick progress, inspect the target cone and qualify a nearer reset-reachable observational milestone without assumptions or behavioral restrictions.
5. Treat finite-`-max_trace_length` B/Ht/Hts/J/K/L/U work as bounded trace search, not meaningful exhaustive proof; use `min_length` only as a frontier.
6. Activate DBH for unknown/broad depth, a direct miss/stall, uneven cycle difficulty, competing targets, or state/path/trace diversity.
7. Execute a named `hunt -config` + `hunt -run` (or AUTO) and archive limits, tag, seed, resolved settings, raw progress, and result.

Do not force Hunt when one deterministic extension is the cheapest decisive experiment. Do not claim DBH when the final flow contains only `prove -max_trace_length`.

## Use-Case Decision Tree

```text
What is the immediate objective?
├─ Undetermined after prove
│  ├─ One current-session legal trace removes a long relevant prefix
│  │  └─ capped `prove -from` probe
│  │     ├─ CEX ............................ stop target search
│  │     └─ no quick progress
│  │        ├─ generic endpoint ............ derive/qualify a nearer small-cone milestone
│  │        └─ relevant but broad suffix ... trace_swarm or trace_search
│  ├─ Several relevant traces, no decisive prefix trace_swarm or trace_search
│  ├─ Deterministic singleton/cheap interval .... focused B/Hts (not DBH)
│  ├─ Few candidates, sampling ambiguity, or hard cycle cycle_swarm
│  ├─ Unknown/broad or uneven depth range ....... bound_swarm after preflight
│  ├─ Useful unordered milestones ............... state_swarm or hunt -auto
│  └─ Known ordered milestones .................. guidepoint
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
6. Use resources for diverse cycles, segments, traces, loop lengths, or seeds. Archive the lifecycle evidence defined below; do not use post-run `IHT002` as a pre-run budget gate.
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
hunt -show -strategy <name>
hunt -run -strategy <name> -property {<targets>} -tag <unique_id>
# Use "-task <task>" instead of "-property {...}" for a task-wide run.

# Start from one stored trace/cycle; runtime may override jobs/time/seed.
hunt -run -strategy <name> -property {<targets>} \
    -from <source_property> [-trace_id <id>] [-cycle <n>] \
    -max_jobs <n> -time_limit <time> -seed <value>
```

| Phase | Artifact | Use |
|---|---|---|
| Pre-run declaration | `hunt -config` | Define the strategy |
| Pre-run inspection | `hunt -show -strategy <name>` | Audit declared settings and budget feasibility |
| Post-run resolved configuration | `IHT002` | Record actual run-time distribution, seed, and settings |
| Post-run execution | Trace Attempt, `IPF180` | Record attempts, progress, and termination evidence |
| Final result | Property status and CEX/covered trace | Classify the search outcome |

Use a scalar for every job, a positional list for per-job values, or a weighted distribution:

```tcl
{50%:[50..200] 50%:[201..1000]}
```

`IHT002` is a post-`hunt -run` log message, not a command or pre-launch
feasibility artifact. Source expressions alone do not identify run-time values.
Use `IHT012` to map work to threads/traces and `IPF031` to inspect engine
settings. `IPF047`/`IPF055` can identify hits but may not print for every hit.

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

## Stored-Trace Target Continuation

Before any reset-based bounded or Swarm work, distinguish a trace reported by a
prior run from one usable in the current Jasper session. If the current
property table lacks the source or a valid trace, recreate/load the source
property and run it under the same RTL, reset, environment, and assumptions
until covered/CEX, then re-query it. Rank candidates by endpoint relevance,
remaining suffix, and source-cone cost; trace length alone is insufficient.

```tcl
foreach source [get_property_list -silent] {
    set status       [get_property_info -list status $source]
    set trace_id     [get_property_info -list trace_id $source]
    set trace_length [get_property_info -list trace_length $source]
    if {$trace_id ne ""} {
        puts "STORED_TRACE: $source status=$status trace_id=$trace_id length=$trace_length"
    }
}

set source <covered_or_cex_property>
if {[lsearch -exact [get_property_list -silent] $source] < 0} {
    error "recreate/load and run the source property in this session"
}
set status       [get_property_info -list status $source]
set trace_id     [get_property_info -list trace_id $source]
set trace_length [get_property_info -list trace_length $source]
if {$trace_id eq ""} { error "source trace is unavailable in this session" }
prove -property <target> \
    -from $source -trace_id $trace_id -cycle -1 \
    -engine_mode Ht -first_trace_attempt <remaining_depth> \
    -time_limit <declared_probe_budget>
```

With a qualified reset-reachable source, a returned CEX is a concrete
falsification: stop the target's bug search; no extra Hunt is required. A
no-hit stays `undetermined` and cannot prove an assertion or make a cover
unreachable. Predeclare a probe slice instead of assigning the first source the
whole remaining investigation budget. Record the expected remaining suffix and
the trace-attempt progress required to continue. Archive `Trace Attempt`,
`IPF180`, termination reason, and final target status.

If a generic source probe shows no quick progress, do not merely raise its time
limit. Inspect the target cone and the source endpoint, then define a nearer
observational milestone over target-relevant architectural state. Prove the
milestone reachable from reset under the unchanged environment, qualify its
current-session trace, and repeat the capped continuation:

```tcl
visualize -property <target>
cover -name <milestone> {<target_relevant_reachable_state>}
prove -property <milestone> -time_limit <milestone_budget>
# Re-query status, trace_id, and trace_length before using -from.
```

The milestone is steering evidence, not a constraint or case split. If no
credible milestone exists, or a relevant source still leaves a broad suffix,
select Trace Swarm or Trace Search; only then consider reset-based Hunt.

## Hunt Beyond the Proof Bound

Only after trace-first and focused-extension branches are inapplicable or have
missed, select the smallest Hunt portfolio justified by the objective. Do not
add unrelated auxiliary properties merely because they are `undetermined`:

1. Use Cycle Swarm for one/few plausible cycles, sampling ambiguity, or an exact-cycle stall.
2. Use Bound Swarm after preflight when depth is unknown/broad, input-dependent strides/skips make it sparse, or traces cannot narrow it. Example: scan through `bound + 100`, start at `1s`, and multiply effort by `10`; these are not defaults.
3. After one focused miss/stall, run the selected named Hunt; do not spend its reserved slice on another direct probe.
4. Use `hunt -auto` when helper/state/path diversity is the objective. AUTO may remain within the proof bound; inspect helper depths.
5. Run selected modes in parallel when licenses permit; otherwise run sequentially.

```tcl
hunt -config -strategy CS -mode cycle_swarm \
    -first_trace_attempt {10 12 15} -max_first_trace_attempt 3 -max_trace_length <above_last_candidate> \
    -trace_attempt_time_limit <per_attempt_slice> \
    -engine_mode B -max_jobs 3 -time_limit <reserved_hunt_slice>
hunt -show -strategy CS
hunt -run -strategy CS -property {<targets>} -tag <tag> -seed <seed>

hunt -config -strategy BS -mode bound_swarm \
    -first_trace_attempt <bound> -max_trace_length <bound_plus_range> \
    -trace_attempt_time_limit 1s -trace_attempt_time_limit_factor 10
hunt -show -strategy BS
hunt -run -strategy BS -property {<targets>}

hunt -run -auto -property {<targets>} -time_limit <time>
```

`-first_trace_attempt` selects each group's initial cycle. In Cycle Swarm,
`-max_first_trace_attempt` is the maximum number of parallel trace-attempt
groups, not a cycle ceiling; the tool caps it by available start values and
`-max_jobs`. For B/B4/Hts, `max_jobs / max_first_trace_attempt` is the jobs per
group, so use divisible values; Bm/Ht ignore this option. The tool may tune
initial cycles/increments to avoid duplicate B-family attempts; audit `hunt -show`, `IHT002`, and actual
`Trace Attempt` lines. A practical per-attempt timeout range is `5m` to `10m`.

Enable full-range starts when jobs cluster near the lower bound:

```tcl
hunt -config -strategy <name> -mode <cycle_or_bound_swarm> \
    -first_trace_attempt <lo> -max_trace_length <hi> \
    -deeper_cycles_earlier true
```

Before `hunt -run`, record `[lo, hi]`, jobs, each job's assigned cycles `C_j`,
intended tier `K`, initial attempt limit, factor, per-job limit, and remaining
aggregate slot-second budget. Estimate:

```text
W_j = C_j * sum(scan=0..K,
                trace_attempt_time_limit * trace_attempt_time_limit_factor ^ scan)
W_aggregate = sum(jobs, W_j)
```

Require every `W_j` to fit its strategy limit and `W_aggregate` to fit the
remaining budget, assuming every assigned cycle reaches tier `K`. After
`hunt -config`, use `hunt -show -strategy <name>` for the pre-run audit. After
`hunt -run`, archive `IHT002`, Trace Attempt, `IPF180`, and final status to
audit dynamic assignments and actual execution.

If the target interval cannot reach its intended effort tier, either narrow it
using evidence, select a trace-directed search, or label the run as a partial
exploration. Do not describe a timed-out partial scan as a full-range rescan.
Do not copy example budgets as universal thresholds. Example configurations
include 100 cycles, `10m`, factor `6`, and three scans; or 100 cycles, 10 jobs,
`5m`, factor `2`.

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
| Treat a prior report's trace as current-session state | A fresh session may lack the property or valid trace ID | Recreate/run the source, then re-query status, ID, and length |
| Start focused bounded or Swarm work before checking current traces | Rebuilds a reachable prefix that a legal trace may bypass | Complete trace inventory, qualification, and a capped relevant-source probe first |
| Spend most of the budget on the first long but generic trace | Length does not show endpoint relevance or suffix difficulty | Cap the probe; on no progress derive/qualify a nearer small-cone observational milestone |
| Expect `-max_trace_length` to scan adjacent candidates | One hard starting cycle can consume the whole direct probe | Use an explicit Cycle Swarm candidate list with per-attempt time limits |
| Set `-max_first_trace_attempt` to a cycle number | It controls parallel attempt groups, not the trace ceiling | Set it to the intended group count; use `-max_trace_length` for the ceiling |
| Run Hunt after continuation already found the target CEX | Spends budget without changing the falsification conclusion | Stop that target's bug search and preserve the CEX |
| Use `IHT002` as a pre-run budget gate | The message is emitted after `hunt -run` starts | Preflight with `hunt -show`; archive `IHT002` after the run |
| Copy example numeric values as defaults | Many values are testcase or version choices | Inspect built-ins and budget from bounds/resources |
| Call a partial Bound Swarm a full-range rescan | The time limit may prevent the target interval from reaching its intended effort tier | Capacity-plan before launch; report actual resolved coverage and tiers |
| Call a deeper `prove -max_trace_length` run "DBH" | Hides whether Hunt/swarm atoms were actually exercised | Label it focused bounded deepening; show `hunt -config`/`hunt -run` artifacts for DBH |
| Call uncovered coverage unreachable | Hunt supplies reachability witnesses only | Use exhaustive proof for unreachability |

## Validation Flags

> ⚠️ **NEEDS VALIDATION** — Verify the release-specific default and boolean interpretation of `no_cover_traces`.
> ⚠️ **NEEDS VALIDATION** — Verify engine modes, maximum trace values, and configuration spellings with installed help and resolved output.
> ⚠️ **NEEDS VALIDATION** — Verify whether `get_signal_list` uses `-intersect` or `-intersection`; reject the suspicious `$set` form.

> 📝 **GAP** — No portable numeric threshold defines when a Hunt miss provides sufficient residual-risk confidence. Establish project-specific budgets and retain exhaustive signoff criteria.

## Consolidated Command Reference

| Command / option | Purpose |
|---|---|
| `hunt -config -strategy N -mode M` / `hunt -run -strategy N` | Define/run isolated strategies |
| `hunt -list strategy` / `hunt -show -strategy N` | Inspect built-ins and audit declared strategy settings before run |
| `hunt -run ... -from P [-trace_id I] [-cycle N]` | Initialize from a stored trace |
| `prove -property T -from P -trace_id I -cycle -1 ...` | Continue target CEX search from one legal stored trace; no-hit is non-exhaustive |
| `hunt -run ... -force` / `-tag ID` / `-seed S` | Preserve results / identify / reproduce a run |
| `hunt -run -auto` | Automatic helper + State/Trace Swarm flow |
| `hunt -report -trace_swarm -tag T -pending -silent` | List unconsumed Trace Swarm work |
| `-first_trace_attempt`, `-max_first_trace_attempt` | Set initial cycles / maximum parallel attempt-group count |
| `-max_trace_length`, `-deeper_cycles_earlier` | Set the trace ceiling / distribute cycle search |
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
