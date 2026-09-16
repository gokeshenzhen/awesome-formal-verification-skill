# Epoch-return development pilot (evaluator only)

Do not mount this plan, calibration material, or other experiment results into
an agent or its waveform service. Mount only the neutral public case and one
selected skill snapshot. The public case is `test/epoch_return_orig`.

## Stage and hypothesis

This is **development-case qualification**, not a confirmatory old/new skill A/B.
Two manually launched independent sessions use the **same** fixed skill,
GPT-5.5/medium, task, tool versions and budgets. Labels a/b identify sessions,
not different treatments. No model run has been performed by the case author.

Question: does a session naturally propose a candidate that needs revision or
additional independently proven support, and does diagnostic evidence help it
converge? A correct first candidate is a valid success, not a protocol failure.
An author-selected candidate that stalls establishes only tool-level opportunity,
not the model's probability of choosing that candidate.

Run the two sessions once each. Preserve both outcomes, including first-try
success, failed refinement, timeouts and infrastructure failures. Do not change
the prompt/case/skill between them. Do not repeat silently until feedback wins.

## Evidence and classification

Audit raw scripts, proof logs, timestamps, waveform reads and the transcript;
do not rely solely on the final narrative. Record the first submitted candidate
and all subsequent expressions with their supporting dependencies.

- `first_try_success`: no failed candidate proof; refinement not exercised.
- `target_guided_discovery`: target diagnostic informed the first candidate;
  distinguish this from repair of a failed candidate.
- `feedback_refinement`: a candidate failed or remained inconclusive; classified
  trace values motivated a concrete revision/supporting fact; new obligations
  were proved before use; the original target then closed.
- `refinement_attempt_unclosed`: evidence-linked revision happened without final closure.
- `no_useful_feedback`: diagnosis did not produce a useful change.
- `environment_invalid`: integrity, license, isolation or client failure; retain
  the attempt and report the reason separately from formal proof failure.

Keep reset-reachable CEX, abstract-model CEX and Jasper `tag SST` distinct.
`undetermined` is not a false candidate. An SST call without reading signal
values, or a helper already stated before that call, does not demonstrate that
the feedback discovered that helper. Tool use alone earns no refinement credit.

Report all JG process wall time including help and final replay. Keep proof time
fields distinct from elapsed process time. Never promote an unproven helper,
weaken P0, constrain away legal inputs, or count author covers as agent coverage.

## Decision after the pilot

If both sessions solve on their first candidates, retain this case as a fast-path
regression and report that refinement was not exercised. If a natural failed
candidate occurs, preserve that checkpoint for a separately labeled conditional
recovery experiment; supplying it later is not a neutral discovery evaluation.

For a later efficacy A/B, freeze a separate comparison whose common routing,
compact-helper fast path and proof gates are identical; isolate the availability
of feedback/refinement instructions as the treatment. Keep both tool interfaces
available and disclose if a control agent discovers the technique independently.
The previous routing-only comparison, which gave both arms the same refinement
recipe, does not establish the recipe's incremental effect. Use independent
held-out cases before generalizing beyond this development pilot.

## Local tool calibration provenance (not model results)

The author-only directory is
`/home/robin/Projects/awesome-formal-verification-skill/test/.epoch_return_control`.
Its `CALIBRATION.md` points to raw logs, receipts and waveform readback. It is
intentionally excluded from the public case and manual session mounts. Preserve
it locally; do not include it in the task prompt or generic knowledge modules.
