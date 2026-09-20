# Assigned FPV continuation task

Work in `/work` on the fixed case at `@CASE_PATH@`.
A read-only historical checkpoint is available at `/opt/experiment/checkpoint`.
Continue the investigation and obtain the strongest sound conclusion you can.
Choose your own proof strategy; the supplied candidate is not mandatory.

Before proof work, read the installed skill using:

```bash
skill-read /home/robin/.codex/skills/formal-verification/SKILL.md
```

Read through EOF, following the next-page commands. Use `skill-read` for every
knowledge file selected through the skill's routing and read it completely
before the next JG run. If skill delivery fails, stop and report an environment
failure. Read receipts document delivery, not comprehension.

Read the case README, all RTL, baseline.tcl and CHECKSUMS.sha256. Preserve the
checksum check output as `/work/integrity_before.txt`. Read the checkpoint's
MANIFEST.json and raw scripts/logs to establish what was actually attempted:

- `baseline.*`: historical baseline stdout and process receipt;
- `candidate.*`: candidate Tcl, inconclusive proof stdout and process receipt;
- `diagnostic.*`: diagnostic Tcl, stdout, process receipt and exported VCD.

These are historical raw artifacts, not a solution or a signed-off proof.
Classify their results from their explicit log fields. Paths and trace IDs in
historical logs are not live handles in your new Jasper session. Do not modify
the checkpoint or activate a fact merely because it appears in a supplied
script. Keep historical evidence distinct from your newly executed runs.

Run the unchanged baseline once to establish your own current environment:

```bash
jg-run baseline
```

Then use the installed skill and Jasper help to continue. There is no requirement
to repeat the historical candidate/diagnostic runs. For every new Tcl run:

```bash
jg-run run /work/your_run.tcl --project /work/runs/unique_name
```

`jg-run status` reports the remaining budget. All new post-baseline Jasper
processes share 180 seconds of wall time, including help, failures, diagnostics
and final reproduction. Historical checkpoint costs are excluded and must not
be inserted into your new ledger. The baseline has its separate wrapper cap.
Do not bypass the wrapper, rewrite receipts, or invoke the vendor executable
directly. Report wrapper failures rather than evading them.

Preserve raw projects and their stdout/process receipts. A wrapper
`post_analysis_exit_cleanup` after matching Tcl/analysis exit statuses is process
cleanup, not a property verdict; its elapsed time still counts. Preserve the
outer process `exit_code` and inner `analysis_exit_code`; a nonzero analysis
status remains a failed run. Disclose cleanup separately.

Do not modify RTL, P0, reset, parameters or baseline; do not remove legal input
behavior or rely on unproven assumptions. Put added scripts and results under
`/work`. Do not access other experiments, reports or skill versions.

When interpreting a waveform, prefer TraceWeave and cite its file, units, sample
times, signal paths and values. Explain how the evidence affected your next
attempt; do not infer reachability from the existence of a waveform. Keep
historical and new traces distinct.

Write `/work/FINAL_REPORT.md` and a non-interactive final reproduction Tcl.
Report the helper/target statuses, bounds, engines, time fields and trace types
with exact raw file/line references, and preserve `/work/integrity_after.txt`.
Distinguish conclusions established in this session from supplied history.
