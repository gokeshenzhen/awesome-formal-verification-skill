# Manual experiment runtime

These utilities meter JasperGold processes and record skill delivery. They do
not launch models, select proof techniques, score answers, or automate A/B runs.
The user starts independent sessions manually inside the experiment's isolation
boundary. Keep TraceWeave inside that same boundary.

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
