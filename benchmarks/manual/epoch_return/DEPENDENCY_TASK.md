# Assigned FPV continuation task

Work in `/work` on the unchanged case at `@CASE_PATH@`. A read-only unfinished
attempt is available at `/opt/experiment/checkpoint`. Continue the investigation
and obtain the strongest sound conclusion you can. Choose your own strategy;
the supplied script and candidate expressions are not mandatory.

Before proof work, read the installed skill through EOF using:

```bash
skill-read /home/robin/.codex/skills/formal-verification/SKILL.md
```

Follow its routing and use `skill-read` for each selected knowledge file. Read
all pages before the next JG run; retry truncated pages at a smaller page size.
If delivery fails, report an environment failure. Receipts show delivery, not
comprehension.

Read the case README, all RTL, baseline.tcl and CHECKSUMS.sha256. Save the checksum
check as `/work/integrity_before.txt`. Read the checkpoint's MANIFEST.json,
candidate.tcl and candidate.log completely. They are unchanged historical source
and raw execution evidence, not a solution or results imported into your session.
Paths in the historical log are not accessible handles in the new environment.
Do not manufacture a historical process receipt or wall-time estimate.

Run the unchanged baseline once to establish your current environment:

```bash
jg-run baseline
```

Continue with the installed skill and Jasper help. Every subsequent Jasper
process must use:

```bash
jg-run run /work/your_run.tcl --project /work/runs/unique_name
```

Use `jg-run status` to inspect remaining budget. All new post-baseline JG
processes share 180 seconds of wall time, including help, failures, diagnostics
and final reproduction. Baseline has a separate cap. Do not add historical
costs to the new ledger. Repeating the historical failed run is not required.
Do not bypass the wrapper or rewrite receipts. Preserve raw projects and logs.

Keep RTL, P0, reset, widths, parameters, legal input behavior and baseline
unchanged. Do not assume unestablished facts or import historical proof statuses
as current-session results. Put new scripts and evidence under `/work`; do not
access other experiments, reports, sessions or skill versions. No particular
proof technique, diagnostic call or candidate shape is required.

Write `/work/FINAL_REPORT.md` and a non-interactive final reproduction Tcl.
Report actual helper/target statuses, validity, bounds, engines and time with
raw file/line references; distinguish prior evidence from new results. Disclose
the scope of each proof attempt and unresolved obligations. Save the checksum
check again as `/work/integrity_after.txt` and report any reachability limitations.
