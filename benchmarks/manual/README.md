# Manual experiment runtime

These utilities meter JasperGold processes, record skill delivery and prepare
isolated manual sessions. They do not invoke model inference non-interactively,
select proof techniques, score answers, or automate A/B runs. The user starts
independent sessions manually inside the experiment's isolation boundary. Keep
TraceWeave inside that same boundary.

`runtime/` is the maintained source for **new** frozen experiment copies. Never
patch an already launched experiment or rewrite its receipts to apply a fix.

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
