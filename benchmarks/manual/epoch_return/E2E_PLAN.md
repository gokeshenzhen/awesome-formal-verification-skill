# Neutral-start helper-guidance comparison (evaluator only)

## Scope and preregistration

Compare the current SST guidance with the readback/trial-guidance patch from
an identical neutral RTL task. Both versions already support SST refinement.
This tests the incremental patch, not the presence/absence of SST instructions.
The case informed development of the patch; neutral task presentation does not
make it a held-out case or establish general efficacy.

The prepared series fixes its pair count, index, skill commits and launch order
in each source.json before any model run. The initial series uses two pairs:
pair 1 runs a then b; pair 2 runs b then a. In both pairs a is old and b is new.
Do not change the count or stop selectively after observing favorable results.
Do not infer a reliable success probability from this small development series.

Review the conditional-recovery pair before starting this series. These two
experiments have different starting information and must never be pooled.
If recovery leads to another skill/runtime change, do not edit these frozen
inputs: declare the unused series superseded and prepare a new versioned series.
Record the reason; retain any runs that already started.

## Controlled inputs

- GPT-5.5 / medium, tool binaries, TraceWeave runtime, common task and budgets
  are fixed; only the selected decomposition leaf differs between skill trees.
- Keep entry routing, compact-helper fast path, Jasper SST commands and proof
  activation gates identical. Inspect the Git diff and frozen source manifest.
- Use the neutral TASK.md without historical candidate, waveform, report,
  successful script, transcript, checkpoint or author calibration. No technique
  hints from the evaluator may be added to a running model session.
- Both skill discovery paths select the same read-only snapshot within an arm.
  Only that snapshot, the public case and the arm's own work are mounted;
  TraceWeave uses the same isolation boundary. Version mapping is evaluator-only.
- Run each arm in a fresh manually launched session, sequentially, with no shared
  context/cache. The baseline has its separate cap; every post-baseline JG
  process shares the same 180-second wall budget, including failed/help/final
  replay runs. Freeze the same dependencies across the entire series.

## Outcomes and process evidence

Record every arm in the final table, including invalid or incomplete attempts:
pair/order, input hashes, model/effort, first candidate, original-target result,
helper obligations/dependencies, discovery path, all JG process wall time,
waveform reads and independent final reproduction. Cite raw artifacts.

Score proof outcome independently from discovery path. Sound closure may come
from any valid strategy; neither a particular helper nor a diagnostic call is
mandatory. Keep reset-reachable CEX, abstract CEX and `tag SST` distinct.

Use these descriptive paths without rewriting their definitions after results:

- `first_try_success`: a first candidate closes without a failed candidate trial;
  report refinement not exercised, not an experimental failure.
- `target_guided_discovery`: target trace values inform the first candidate,
  rather than a revision of a failed candidate.
- `feedback_refinement`: failed/inconclusive candidate → classified trace values
  → concrete changed candidate or support → proven obligations → target closure.
- `refinement_attempt_unclosed`: a concrete trace-linked assertion is attempted
  but the original target does not close soundly.
- `rtl_guided_recovery`: a stalled candidate is supported/revised using RTL;
  retain its success/failure without attributing it to waveform feedback.
- `other_proof_path` or `no_useful_feedback`: disclose the actual strategy; a
  tool invocation, syntax fix or promise alone is not a refinement attempt.
- `environment_invalid`: integrity/isolation/license/client failure; preserve
  the attempt separately, do not silently drop or relabel it as a proof failure.

Gate on actual proven helper obligations before activation, with no circular
assumptions or target/environment changes. An unchanged guard/state model and
raw final proof status matter more than a narrative claiming success.

## Reporting and stopping

Complete the predeclared count unless an integrity/environment issue prevents
valid continuation. Preserve that reason rather than varying sample size to
obtain a desired winner. Any replacement needs a fresh directory and an explicit
label. Do not restart a partly used arm or subtract unsuccessful exploration.

Report both total target closure and evidence-linked refinement occurrence.
Keep missing opportunity (direct success) distinct from failure to use an
available opportunity. Do not compare only the subset that happened to emit
SST, or credit a relation already stated before the waveform was read.

Report process cost for all attempts; a timeout is censored/inconclusive, not
proof that the candidate is false. Separate final property time, JG wall time
and client/model time. If both versions solve directly, conclude refinement's
benefit was not demonstrated here. If the patch helps, retain this as development
evidence and use independent cases before making a general claim.
