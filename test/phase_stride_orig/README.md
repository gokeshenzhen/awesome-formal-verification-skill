# Phase Stride Original

The fixed design under investigation is `phase_stride_orig.sv`, with top
module `phase_stride_orig`. The supplied formal objective is the opaque
assertion `P0`; do not assume an expected result from its identifier or from
this task description. No cover property or source trace is supplied.

## Objective

Run the common `baseline.tcl`, then determine the strongest sound conclusion
supported by JasperGold for `P0`.

The investigation is complete when all of the following evidence is preserved:

1. Record the common baseline status and all reported bounds for `P0`.
2. Continue investigating `P0` until JasperGold reports a conclusive result, or
   until 2 minutes of total Jasper wall time after the baseline have been
   consumed.
3. Preserve a reproducible raw JasperGold witness for a falsified assertion, or
   the exhaustive result for a proven assertion.
4. Clearly distinguish exhaustive conclusions from bounded or otherwise
   non-exhaustive results. A search that finds no trace is not proof,
   unreachability, or signoff.
5. Provide one non-interactive final run that reproduces the strongest result
   for `P0`, and cite exact log lines or generated reports for every status,
   bound, trace length, runtime, seed, and resource-use claim.
6. Report both wall time and aggregate ProofGrid slot-seconds whenever more than
   one engine job is used.
7. Preserve `integrity_before.txt` and `integrity_after.txt`, each containing a
   successful `sha256sum -c CHECKSUMS.sha256` transcript.

## Integrity rules

- Do not edit, replace, bind over, or re-elaborate a modified copy of
  `phase_stride_orig.sv`.
- Analyze the shared RTL file from this directory directly.
- Do not add assertions, cover properties, assumptions, constraints, helper
  properties, or guidepoints. Investigate the supplied `P0` directly.
- Write scripts, projects, logs, traces, and reports only below the assigned arm
  directory.
- Do not read the other arm, another testcase, prior reports, `raw-docs/`, or
  `extractions/`.
- Treat `P0` as an identifier, not a description of its expected result.
