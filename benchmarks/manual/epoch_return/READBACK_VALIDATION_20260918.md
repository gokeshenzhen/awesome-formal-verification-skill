# Readback-only probe: preparation validation, 2026-09-18

Status: prepared and sealed; both model-free preflights passed. No model arm
has been launched. This note records infrastructure validation, not a result
about helper refinement, skill efficacy, or the model's reasoning ability.
The formal skill, DUT, TraceWeave source, and historical experiments were not
modified for this preparation. Only common preparation/probe code and its
documentation are committed; the experiment remains Git-ignored.

## Frozen comparison

Implementation: `cccff61b8c7fa865f7e63cec1fb0786edbb81bba`.
Experiment root:
`/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01`.

Both arms use skill `883d4812924a3f7e72f243bde0b2d1bff9513929` and
GPT-5.5 / medium. Their skill manifests are identical. A receives the raw
checkpoint; B additionally receives a mechanical, all-declaration/all-recorded-
timestamp VCD table. Only that attachment differs. This is a fixed single
pair in A → B order with no new proof execution, not an old/new skill trial.
See [source and treatment specification](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/source.json)
and [preregistered review plan](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/SCORING.md).

The raw files come from the first naturally unfinished helper/SST attempt in
`/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/blind/arm_a`.
An explicit pre-revision allowlist excludes final reports, subsequent helpers,
old sessions, and evaluator interpretations. The original bytes and source
paths are recorded in the checkpoint manifest and source provenance.
This selected development checkpoint is not a held-out benchmark.

TraceWeave code is reused from the earlier sealed experiment, at recorded
commit `093299cf123801bf5b5dda0a52153b17d886aff4`, and checked against that
experiment's runtime manifest. The current Python environment and client are
separately pinned for both arms; no claim is made that their versions equal
the earlier experiment's versions.
See [runtime and executable pins](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/pins.json).

Sealed pins SHA256:
`51e1463624c70b8425f63fa857e3104774e759cd5efc1ae73a999073d6fbf725`.
Both preflight receipts reference this digest.

## Checks and raw evidence

- `python3 -m unittest discover -s benchmarks/manual/tests -v`: **41 tests
  passed**, including legacy-mode regression tests, the exact attachment
  delta, checkpoint allowlisting, hidden/partial signal rejection, identical
  skill enforcement, and proof-tool mount exclusion.
  [Unit-test output](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/validation/unittest.log).
- Both preflights exited **0**. The checks cover read-only input, private
  filesystem boundaries, the native client's effective model/config/skill
  discovery, isolated stdio MCP access, and refused `jg`/`jg-run` commands.
  No model inference or JasperGold process is used by this preflight.
  [A receipt](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/receipts/preflight_a.json),
  [B receipt](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/receipts/preflight_b.json).
- The packet contains **83 declarations at 5 recorded timestamps**:
  `0, 5000, 10000, 15000, 20000 ps`. Every displayed binary value agrees with
  the isolated stdio MCP query in each preflight. This checks the presentation
  and MCP interfaces against one another; they share TraceWeave's parser and
  are not two independent VCD implementations.
  [A value checks](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/preflight/a.p91k5uwj/work/packet_mcp_checks.json),
  [B value checks](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/preflight/b.8xurg_25/work/packet_mcp_checks.json).
- A's attachment is **22 lines**, B's **119 lines**. B therefore needs more
  than the default input-reader page. The identical task instructs both arms
  to follow `NEXT` through `EOF`; actual transcript delivery, truncation, and
  subsequent use still require evaluation. A receipt alone is not comprehension.
  [A input/proof checks](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/preflight/a.p91k5uwj/work/diagnosis_only_checks.json),
  [B input/proof checks](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/control/preflight/b.8xurg_25/work/diagnosis_only_checks.json).

The evaluator packet is mounted only during model-free preflight, never into
the interactive arms. The real arm output directories are empty at handoff;
only preflight receipts exist. `git check-ignore -v` resolves this experiment
to the repository's existing `test` ignore rule; `git ls-files` lists no files
under the experiment root. These checks do not replace launch-time pin checks.

## Handoff and limits

Use [the generated run instructions](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_readback_probe_gpt55_01/README_RUN.md).
The user runs `check`, then arm A, exits the completed client, then runs arm B.
No extra investigator hints, mid-session corrections, or model-setting changes.
Do not reseal a drifted or used experiment; preserve the evidence and diagnose
the mismatch. The launcher is manual and never launches model turns in bulk.

After both UUIDs are returned, evaluate delivered evidence, its interpretation,
and the proposed next change. A proposal is not a proved helper. Readback
improvement would motivate an information-delivery change, not by itself a
claim of improved proof closure. Failure despite delivery does not establish
an intrinsic model limit: the trace may still lack necessary evidence, and
the task may require a different reasoning strategy. Any candidate proof is
a separately scoped subsequent stage.
