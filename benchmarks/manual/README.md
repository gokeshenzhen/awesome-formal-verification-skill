# Manual experiment runtime

These utilities meter JasperGold processes, record skill delivery and prepare
isolated sessions. Manual launch remains the default. An explicitly authorized,
preregistered experiment may opt into one bounded `codex exec` attempt per arm;
the launcher does not select techniques, score answers, retry failures, or
continue until a favorable result. Keep TraceWeave inside the same boundary.

`runtime/` is the maintained source for **new** frozen experiment copies. Never
patch an already launched experiment or rewrite its receipts to apply a fix.

## Opt-in non-interactive launch

Only when the user authorizes autonomous model runs, prepare a **new** experiment
with this additional `control/source.json` field before sealing:

```json
{"execution": {"mode": "headless", "wall_seconds": 900,
               "authorization": "User explicitly requested autonomous A/B execution"}}
```

Preregister the number/order of runs, conditions, proof budgets and outcome
criteria separately. Seal and preflight as usual, then use `launch.sh a` or `b`.
No TTY is needed for the opt-in mode. Missing `execution` retains the manual
TTY requirement. Both modes use the same frozen config, skill aliases, private
authentication copy and outer mount/PID isolation. Headless mode preserves
JSONL events, stderr, native transcripts, usage and completion/timeout receipts;
the disposable credential copy is removed on exit. A model process completing
is **not** a proof or an evaluation success. Keep every failure and timed-out run.

The caller mounts this directory at `/opt/experiment/runtime`, creates executable
aliases `jg-run` and `skill-read`, and mounts a read-only
`/opt/experiment/common/case.json` containing:

```json
{"case_path": "/absolute/path/to/public/case", "target": "dut.P0"}
```

The selected skill is read-only at `/opt/formal-snapshot`; both client discovery
aliases must resolve to its `adapters/claude-code` entry. Output is `/work`.
Baseline wall cap is 60 seconds; post-baseline total process wall budget is
180 seconds, including help, failed runs, reproductions and cleanup. A process
must report successful license checkout within 10 seconds.

## Exit recognition regression

JasperGold 2025.12p002 can print a help-only console exit with `% INFO (IPL005)`;
elaborated sessions can print `[<embedded>] % INFO (IPL005)`. Accept either, or
the unprefixed form, **only together with both normal Tcl/analysis exit lines**.
After a two-second grace period the wrapper may stop leftover processes.
Preserve the real vendor exit code and charge the full elapsed time. This is
process cleanup, never a property verdict.

Origin: the local reservation-journal B run's
`runs/help_sst.stdout.log` and `runs/help_sst/jg_console.log`. The old receipts
remain authoritative for that old run; do not subtract the observed delay.

Run license-free tests:

```bash
python3 -m unittest discover -s benchmarks/manual/tests -v
```

## Development-case qualification

For the epoch-return case, `prepare_pilot.py` creates a fresh pair with the same
skill snapshot in both sessions. This is a **pilot, not an old/new efficacy A/B**.
It copies only allowlisted public case files and runtime-only TraceWeave files.
The launcher seals content/executable hashes, checks client discovery aliases,
and requires a passing model-free environment preflight before manual launch.

```bash
python3 benchmarks/manual/prepare_pilot.py \
  --dest test/epoch_return_pilot_gpt55_01 --skill-revision 82a7408
```

Follow the generated `README_RUN.md`; start a and b sequentially from a terminal.
Never overwrite a prior directory or relax pins to reuse a launched run. See
`epoch_return/PLAN.md` for the preregistered classification and later A/B boundary.

## Conditional recovery comparison

`prepare_recovery.py` prepares an old/new pair from the same raw failure
checkpoint. It never copies interpretations, solutions or sessions. This is
explicitly conditional recovery, not neutral discovery. Both skills already
contain SST; the comparison isolates the new readback/trial guidance in the
decomposition leaf. Other skill differences are refused.

```bash
python3 benchmarks/manual/prepare_recovery.py \
  --dest test/epoch_return_recovery_ab_gpt55_01 \
  --old-revision 82a7408 --new-revision 883d481 \
  --checkpoint-arm test/epoch_return_pilot_gpt55_01/blind/arm_b
```

Follow the generated README_RUN.md to seal, preflight and manually launch.
The new baseline and 180-second post-baseline budget are identical in both arms;
the supplied history is read-only and its prior costs are separate. The original
pilot and historical evidence are not changed. See `epoch_return/RECOVERY_PLAN.md`.

## Neutral-start old/new series

After reviewing recovery, use the separately frozen neutral-start series to
measure the patch from the original task. No historical checkpoint is mounted.
Declare the pair count before launch; retain all outcomes. The default prepares
two pairs with opposite sequential launch orders, keeping a=old and b=new.

```bash
python3 benchmarks/manual/prepare_e2e.py \
  --dest-prefix test/epoch_return_e2e_ab_gpt55 --pairs 2 \
  --old-revision 82a7408 --new-revision 883d481
```

This creates `_01` and `_02` directories; it never runs a model. Follow each
README_RUN.md. Do not pool these results with conditional recovery or the
same-snapshot pilot. Both versions already support SST; this isolates the
readback/trial patch on a development case, not general feedback efficacy.
See `epoch_return/E2E_PLAN.md`. If recovery prompts another skill change, leave
this series sealed and create a newly versioned one instead of editing its pins.

## Input-presentation diagnostic probe

`prepare_readback.py` freezes one raw-versus-mechanically-expanded input pair.
Both arms use the same skill. No new proof executable is mounted, and no model
is started by preparation or preflight. The attachment contains every exported
signal at every recorded VCD timestamp, not selected facts or helper answers.
Its values are checked against stdio MCP in model-free preflight. Historical
TraceWeave source is copied from a prior verified seal, so unrelated live tool
edits are neither imported nor modified. The shared Python environment is
freshly pinned and preflighted for both arms.

```bash
python3 benchmarks/manual/prepare_readback.py \
  --dest test/epoch_return_readback_probe_gpt55_01 --skill-revision 883d481 \
  --checkpoint-arm test/epoch_return_e2e_ab_gpt55_01/blind/arm_a \
  --traceweave-from test/epoch_return_e2e_ab_gpt55_01
```

Follow README_RUN.md: seal, check, preflight, then the user manually launches a
and b sequentially. Evaluate delivery, interpretation and proposed changes,
not full proof. Do not pool this selected diagnosis pair with skill efficacy
or end-to-end proof counts. See `epoch_return/READBACK_PLAN.md`.

## Proven-dependency recovery comparison

`prepare_dependency.py` prepares one manual old/new skill pair from an unchanged
candidate Tcl and its raw inconclusive replay log. Unlike SST recovery, no
diagnostic waveform or historical wrapper receipt is required or fabricated.
The explicit skill delta covers the complexity index, decomposition leaf and
workflow; older experiment kinds keep their original narrower boundary.

```bash
python3 benchmarks/manual/prepare_dependency.py \
  --dest test/epoch_return_dependency_ab_gpt55_01 \
  --old-revision 72cbbe0 --new-revision 757e0ba \
  --candidate-script /absolute/path/to/original_candidate.tcl \
  --replay-log /absolute/path/to/original/jg_session_0.log
```

Follow the generated README_RUN.md to seal, check, preflight and manually run A
then B. The same inputs, GPT-5.5/medium and budget apply to both arms. This tests
conditional recovery of a known stalled script, not invariant discovery or
general feedback efficacy. See `epoch_return/DEPENDENCY_PLAN.md`.

## Feedback-presence diagnosis

The `target_feedback_presence_ab` kind compares identical skills and a shared
unfinished target checkpoint, with or without a separately mounted raw SST
diagnostic and exhaustive mechanical readback. This is target-guided candidate
discovery, **not** failed-helper refinement or an old/new skill comparison.
Preparation is case-specific; keep cases, assignments and raw outcomes local
under ignored `test/`. Freeze conditions/order before launching. The common
checkpoint cannot contain diagnostic files, and the control attachment contains
only its material index. Neither model arm receives proof executables; evaluate
their proposals later with the same independent, preregistered proof budget.
Never include evaluator interpretations or reference solutions in attachments.

## Failed-helper routing comparison

The `helper_failure_routing_ab` kind isolates exactly the skill router and
complexity-index delta. Keep the same failed candidate, raw reachable CEX,
repair request and proof budget in both arms; freeze these shared inputs under
`common/` without evaluator interpretations. Preregister a fixed series/order
as for end-to-end comparisons. This is conditional repair, not neutral
invariant discovery. Score route selection, actual candidate revision, valid
helper proof and original-target closure separately; reading the intended
module alone is not a proof success. Other comparison kinds retain their
original, narrower allowed deltas.
