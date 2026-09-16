# Assigned FPV task

Work in `/work`. Investigate the fixed case at:

`@CASE_PATH@`

Before proof work, read the installed skill using:

```bash
skill-read /home/robin/.codex/skills/formal-verification/SKILL.md
```

The command prints a numbered page, the resolved path, SHA256, total line count,
and a next-page command when necessary. Read through EOF. If the entry cannot
be read, stop and report an environment failure; do not proceed without skill.
Use the same command for knowledge files you select through the skill's own
routing. Every selected file must be read through EOF before the next JG run.
Do not load all modules indiscriminately. The receipts in `skill_reads.jsonl`
record delivery, not comprehension; actual transcript output is also audited.

Read the fixed case's README.md, all RTL files, baseline.tcl, and CHECKSUMS.sha256. Follow
its objective and integrity rules. Run its checksum check in the case directory
and save the result as `/work/integrity_before.txt`.

Run the supplied baseline unchanged:

```bash
jg-run baseline
```

After the baseline, use the installed skill and Jasper help to investigate the
strongest sound conclusion. For each subsequent non-interactive Tcl run:

```bash
jg-run run /work/your_run.tcl --project /work/runs/unique_name
```

Choose your own filenames and proof strategy. `jg-run status` reports remaining
time. All post-baseline JG process wall time shares the case's 180-second budget,
including failed attempts, help sessions, and reproductions. The wrapper limits
each process to the remainder, records start/exit/elapsed time, and stops a
launch that does not check out licenses promptly. If a wrapper check fails,
report it; do not bypass it with an absolute vendor path or rewrite the ledger.

The installed JG sometimes leaves its process alive after reporting a normal
Tcl/analysis exit. The wrapper may then perform `post_analysis_exit_cleanup`,
but only after the console exit request and both normal-exit messages. Its
receipt preserves the real vendor exit code and counts cleanup time. Disclose
this separately; it is neither a property verdict nor evidence of a design bug.

Preserve each raw JG project and its `*.stdout.log` and `*.run.json` sidecars.
Do not modify the RTL, P0, or baseline. Do not remove legal input behavior or
use an unproven fact to force a conclusion. Keep all added proof scripts and
artifacts under `/work`. Do not enumerate other experiments or skill versions.

When a waveform is generated, preserve its metadata, export it, and inspect
actual values. Explain how the evidence affected the next attempt. In the
report, give waveform filename, time unit, time points, signal names, and values
without conflating distinct traces. Prefer TraceWeave for signal readback.

Write `/work/FINAL_REPORT.md` and a non-interactive final reproduction Tcl.
Report each Jasper status, bound, engine, time, and trace with field names and
exact raw file/line citations. Do not claim stronger semantics than the tool
reports. Preserve `/work/integrity_after.txt` from the final checksum check.
