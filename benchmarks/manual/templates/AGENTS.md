# Experiment execution rules (identical in both workspaces)

Use only the formal-verification skill installed in this environment. Read its
entry before proof work; follow its own routing, without searching for other
versions. Use `skill-read` to read selected knowledge files completely. If a
page is truncated in tool output, repeat with a smaller page size. Do not claim
to have understood a file merely because its hash or read receipt exists.

Run every JasperGold process via `jg-run`; do not bypass the run ledger using
the vendor executable directly. The launcher grants the wrapper network access
inside an externally isolated filesystem. No approval escalation is needed.

For formal artifacts, prefer TraceWeave `get_formal_paths`; do not treat a
Jasper log as a simulation log. For VCD/FSDB, prefer its waveform summary,
signal search, and signal readback tools before explaining values. Record the
wave file, time unit, sample times, signal paths, and decoded values supporting
the explanation. Tool errors are evidence to report, not permission to invent
values. Do not infer reachability from the mere presence of a waveform.

Do not read hidden evaluator material, other workspaces, historical sessions,
external project sources, or alternative skill installations. Do not change
client configuration, tools, permissions, model, or reasoning effort mid-run.
Do not launch subagents or install additional tools/plugins.

Keep proof work and reports under `/work`. Preserve raw evidence and report
exact result fields with names. Files outside `/work` that the client creates
for its own sessions/cache are operational state, not proof deliverables.
