# Implementation validation (not model efficacy)

Changes are separated into skill routing, process-runtime repair, public RTL
case, and manual pilot packaging commits. No old frozen experiment was edited.
No model inference or manual pilot session was launched during preparation.

## Local raw evidence

All paths below are relative to the repository root. Raw EDA projects and private
calibration answers intentionally remain local and outside the pilot mounts.

- Runtime tests: `python3 -m unittest discover -s benchmarks/manual/tests -v`.
  All 23 tests passed, covering exit prefixes, missing/nonzero exit markers,
  license watchdog, time budget, delivery gates, case identity, public-file
  checksums, destination refusal and skill-only snapshot export.
- Real help-only run: `test/jg_help_exit_1rqj2fs3/stdout.log:4648` is the top-level
  `% INFO (IPL005)` exit request. Normal exits are at lines 4651 and 4652.
  `receipt.json:14` records 4.034743009135127 seconds; exit code -15 and
  `post_analysis_exit_cleanup` are preserved, not converted to a proof result.
- Public-case baseline: `test/.epoch_return_control/baseline_02/stdout.log:255`
  reports P0 `undetermined`, min_length 9, no trace.
- Author-selected candidate diagnostic:
  `test/.epoch_return_control/balance_01/stdout.log:198` reports `undetermined`;
  line 290 records `length 2 ... tag SST`.
- Author proof closure: `test/.epoch_return_control/refined_01/stdout.log:186`,
  line 292 and line 386 record the support, balance and original target proven
  with infinite bounds. Activation gates are at lines 187 and 293. This is
  tool-level calibration, not evidence that a model naturally chose or repaired
  the candidate. Detailed private provenance: `test/.epoch_return_control/CALIBRATION.md`.
- Reachability: `test/.epoch_return_control/covers_01/stdout.log:251` through the
  named results at lines 254, 257, 260, 263, 266 and 269 record seven explicit
  functional covers. They are not credited to future agent sessions.
- Prepared pilot:
  `test/epoch_return_pilot_gpt55_01/control/receipts/preflight_a.json` and
  `preflight_b.json` each record exit_code 0 for pins SHA256
  `d88e6e81c581fbc85f6ece7ec0b9646146dfe54447fc2ed96ea7e0aa545f3e49`.
  Their evidence directories contain real stdio MCP readback, denied private
  reads, equal skill aliases, client configuration/discovery, model catalog,
  and Jasper license/proof/cover smoke checks. They do not run the case proof.

## What remains unmeasured

The two user-run GPT-5.5/medium sessions are still pending. They use identical
skill snapshot `82a7408` and are a development qualification pilot. Natural
candidate failure rate, actual feedback-driven revision and incremental skill
benefit are not yet established. Keep first-try successes rather than forcing
diagnostics. Follow PLAN.md before designing any separate efficacy comparison.
