# Proven-dependency recovery comparison (evaluator only)

## Question and fixed comparison

Does the helper-classification/proof-selection skill patch improve recovery
from the same naturally stalled proof script? This is a development-case
conditional recovery test, not from-zero invariant discovery, CTI/SST efficacy,
or a held-out estimate of general success probability.

Run one pair once, sequentially a then b. A receives the old skill, B the new
skill; immutable revisions are recorded in source.json. Both use GPT-5.5/medium.
The only skill differences allowed are complexity-management.md, its existing
decomposition leaf, and workflow.md. All other skill files, task text, public
RTL, tool/runtime inputs and budgets are identical between arms.

Copy exactly the original proposed Tcl and its failed replay's raw session log.
Record source paths and SHA256 outside the client view. Do not include the
evaluator repair, successful replay, other arm's script, reports, transcripts,
SST interpretations or proof caches. The common MANIFEST names raw files only.
The source replay has no wrapper timing receipt: disclose that absence rather
than reconstructing an exact historical process duration from property times.

Both discovery aliases select the same read-only skill snapshot within an arm.
TraceWeave shares the client's filesystem/PID isolation. Only the public case,
common checkpoint, selected skill and that arm's work are mounted. The mapping,
this plan and successful evaluator runs are never mounted into the client.

Run a fresh unchanged baseline per arm, then allow 180 seconds total additional
JG process wall time, including help, failed attempts and final reproduction.
Historical costs remain separate. Model-free preflight uses a toy design only;
the user starts model sessions manually. Do not provide mid-session hints.

## Scoring and reporting

Evaluate original-target outcome first: valid proof under unchanged setup,
valid reachable counterexample, undetermined, or environment/integrity invalid.
Keep outcome independent from the chosen strategy. Sequential explicit support,
tool-managed batch proof and other sound methods are all eligible for success.
Do not require particular commands, helper names or an SST/refinement episode.

Audit the actual script, proof logs and transcript for:

- Which facts were established in this session before reuse, and which
  obligations were selected or proved together in each call.
- Whether the model recognized the stalled-script issue, or succeeded through
  a different sound strategy. Do not infer this merely from a command token.
- Correct distinction between helper classification, proven evidence and
  actual proof selection; do not penalize mere declaration of an unproven helper.
- Whether the original target closed and the final reproduction stands on its
  own without inherited caches or unproved assumptions. A support lemma alone
  is not target signoff, nor is a later cached result a fresh independent proof.
- Total new JG process wall time, attempt count, unresolved obligations and
  truthful reporting of limitations. Cite every number to raw artifacts.

Preserve both results, including incomplete/environment-invalid runs. Do not
repeat until a preferred winner appears, enlarge budgets after seeing results,
or patch frozen inputs. Any justified replacement needs a new directory and
explicit label. If both versions close, report the tie and process differences;
do not claim a necessary skill advantage. If the new version improves, retain
it as case-specific development evidence, not general refinement efficacy.
