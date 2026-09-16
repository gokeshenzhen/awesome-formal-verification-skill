# Conditional helper-recovery comparison (evaluator only)

## Question and treatment

Does more operational diagnostic-readback guidance improve recovery from the
same naturally occurring inconclusive candidate and raw SST checkpoint?
This is a development experiment selected after observing a failure, **not** a
neutral end-to-end discovery test or an estimate of general success probability.

Run one predeclared pair, once per arm, sequentially (a then b). Arm a receives
the old skill; arm b receives the new skill. The mapping and immutable commits
are in evaluator-only source.json. Neither label/treatment nor the evaluator
plan is mounted into the client or TraceWeave. Both arms use GPT-5.5/medium.

The selected skill trees may differ only in the existing decomposition leaf.
Review the archived diff: entry routing, compact-helper fast path, SST commands
and proof gates remain common. Both versions already offer SST refinement;
this measures the incremental readback/trial guidance, not SST versus no SST.

## Common starting material

Both arms get identical unchanged case files and an allowlisted, byte-preserved
checkpoint: baseline log/receipt, candidate script/log/receipt, diagnostic
script/log/receipt and VCD. Keep the historical source paths/hashes in evaluator
provenance. Never copy final reports, analysis/value summaries, solutions,
author calibration, later proof runs, client sessions or caches.

Run a fresh unchanged baseline in each arm for environment comparability.
It does not erase or repeat the supplied candidate experiment. The new
post-baseline JG process budget is 180 seconds per arm; inherited costs are
reported separately and never charged to a fresh ledger. Include every new
help/failure/diagnostic/final-replay process. Keep process time, property time
and client/model elapsed time separate. Never run the arms concurrently.

## Scoring before looking at results

Audit scripts, logs, transcript and waveform-tool calls, not just the narrative.
Record proof outcome independently of discovery path:

- Outcome: sound original-target proof, valid original-model reachable CEX,
  undetermined, or environment/integrity invalid.
- `feedback_refinement`: classified trace values motivate a new expression or
  support fact; its obligations are proved before use and the target closes.
- `refinement_attempt_unclosed`: a concrete evidence-linked assertion is tried,
  but sound target closure is not obtained.
- `rtl_guided_recovery`: new support/revision comes from RTL rather than decoded
  trace values; report success/failure, without claiming waveform causality.
- `other_proof_path`: a different sound method closes the target.
- `no_useful_feedback`: metadata, partial readback or commentary produces no
  concrete evidence-linked trial; distinguish this from a trial that failed.

Do not require particular signal names, helper shapes or use of SST for credit
on proof outcome. Retain valid direct/RTL-led successes. Do not count a printing
fix, unchanged expression, failed tool call, or promise as a helper revision.
Keep `tag SST` distinct from internal CTI and reset-reachable CEX. A candidate's
`undetermined` status does not establish that it is false. No unproven helper
activation, circular assumptions or relaxed target/environment may earn proof
credit. Cite every metric to raw artifacts.

## Stop and next stage

Retain both outcomes, including failed/inconclusive runs. Do not retry until
the treatment wins. Preflight is model-free and runs only a toy EDA check.
Environment failures remain recorded; any replacement uses a new directory and
is labeled a replacement, never an erased attempt.

Review this pair before launching the separately prepared neutral comparison.
If the skill/runtime needs another change, preserve this pair and prepare a
new explicitly versioned comparison; do not patch sealed inputs. Improvements
learned from this development case require held-out cases before generalization.
