# Input-presentation diagnostic probe (evaluator only)

## Question and fixed scope

Does mechanically pre-expanding an existing short waveform help the same model
and skill diagnose the same unfinished helper attempt? This tests information
access/presentation, not old-versus-new skill, proof efficacy, or model ability
in general. Retrieval effort, salience and attention can all change together;
do not claim this identifies a single cognitive cause.

Run one pair, once per arm, sequentially a then b. Both use GPT-5.5 / medium,
the same immutable skill revision (initially 883d481), the same source design,
raw checkpoint, client config, TraceWeave source and Python environment. Only
the attached MATERIALS.md differs. Preserve the entire pair, including failed
or incomplete attempts; do not extend the sample count to obtain a winner.

The selected source is the first neutral series' arm-a first helper/SST trial.
It occurred naturally, but was selected after reviewing its failure: this is
development diagnosis, not held-out or neutral end-to-end discovery. Absolute
source files, hashes and tool-runtime provenance are recorded in source.json.
No benchmark-specific diagnosis or helper answer enters the installed skill.

## Treatments and no-leak boundary

- a: original design, candidate script/log and raw diagnostic script/log/VCD.
- b: exactly the same, plus a mechanical VCD table in the supplied attachment.

Copy the raw checkpoint by an explicit pre-revision allowlist, preserving bytes.
Do not copy reports, prior agent sessions, interpreted values, oracle solutions,
later revised helpers, proof caches or evaluator readbacks.

Generate the attachment using the frozen TraceWeave parser, not hand-selected
values: every exported declaration, every recorded VCD timestamp including the
initial dump, full signal paths sorted lexicographically, declaration widths,
and binary recorded values. Include unknown/unrecorded values explicitly.
Do not highlight signals, compare payloads, calculate sums, label good/bad
states, infer reachability, or suggest relations. This is all dumped signals,
not a claim that every RTL object or necessary historical fact was exported.
For unsupported formats, aliases, precision or size, refuse instead of silently
dropping data. Preflight compares every table value with stdio MCP readback.

The same prompt asks for analysis and a next-step proposal, without prescribing
a particular technique or answer. The input-reader command delivers the local
attachment in numbered pages; both arms receive that identical instruction.
Audit actual transcript text for delivery/truncation, not only the receipt.
Neither attachment presence nor a read receipt proves comprehension or use.

Both skill discovery aliases select the same read-only snapshot inside each
arm. Both snapshots are byte-identical. TraceWeave shares the client's mount
and PID isolation. Only that arm's attachment is mounted; the evaluator packet
JSON and preflight outputs are not exposed in a model session. Preflight uses
separate, discarded client caches and never calls model inference.

## Budget and proof boundary

New JasperGold process budget is zero in both arms. Do not rerun the baseline,
candidate or SST. Neither JasperGold nor Verdi is mounted; jg/jg-run refuse
execution and record attempted calls. VCD readback remains available. The
model and reasoning setting are equal; no additional investigator prompts or
mid-session corrections are allowed. Record observed model/tool costs; do not
equate the interactive client's idle lifetime with model solving time.

No arm can receive new proof/signoff credit in this stage. An unexecuted
candidate is not refinement_attempt_unclosed under the earlier proof-trial
definition. Any later independent candidate proof has its own budget and
artifacts, and must distinguish the original proposal from evaluator repairs.

## Evidence-based review

Review each arm without requiring a preferred expression or output format:

1. Delivery: which raw or pre-expanded values actually entered the context?
   Was the observed predecessor/continuation available, and were query errors,
   missing signals, truncation and SVA sampling caveats handled accurately?
2. Interpretation: are the arithmetic widths and cited RTL update conditions
   consistent with the actual values? Does the account explain the transition,
   rather than only an undesirable final value or property pseudo-signal?
3. Proposal: is a concrete next assertion/support or proof change grounded in
   those facts? Record its effect on the supplied transition and the still-open
   reset/inductiveness/dependency obligations; a justified no-proposal result
   is distinct from fabricated certainty.
4. Integrity: no hidden-input reads, no new proof execution, no environment or
   target relaxation, no claim that an SST state is a confirmed reachable bug.

Do not infer reasoning inability when the attachment was not actually read.
Do not infer that a candidate is false merely because no proof is available.
Full input delivery still does not guarantee a sufficient invariant can be
discovered from one trace. All claims and numbers need raw artifact citations.

If b improves over an a that lacks necessary readback, treat that as preliminary
evidence to improve information access/presentation before adding skill rules.
If both fail after usable delivery, investigate reasoning/strategy and evidence
adequacy; do not declare an inherent model limit or blame skill strictness.
If both succeed, no skill change is justified by this probe alone. If the table
hurts, retain the negative result rather than deploying it by default.

This small selected pair cannot establish statistical efficacy. Do not pool it
with prior neutral discovery, conditional recovery or proof-success counts.
