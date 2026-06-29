# Weak-model skill A/B — manual blind run

Goal: test the hypothesis that the formal-verification skill's value **amplifies
on a weaker model**. On a frontier model these two cases did NOT differentiate
(the no_skill arm independently rediscovered the technique). The bet: a weaker
model without the skill stalls, but with the skill applies the technique.

Run these on a **weak model** (e.g. `claude-haiku-4-5`), NOT a frontier model.

## Cases (both small, JG runs in seconds — cheap)

| Case | DUT | Technique the skill supplies | Why it may discriminate on a weak model |
|---|---|---|---|
| `cnt_abs/` | `cnt_abstract_eg.sv` (sha `de451f6…`) | counter abstraction (`abstract -counter -values`) | deep BMC (8.3M / 268M cycles) is unreachable; a weak model may not know the abstraction command |
| `helper_counters/` | `two_counters.v` (sha `6c9e3a2…`) | helper lemma (`assert -helper` + `-with_helpers`) | the `counter1==counter2` invariant is the non-obvious step a weak model may miss |

> Note: `cnt_abs` is **in-distribution** — the skill's `abstraction.md` contains
> this exact example. That is intentional here: it isolates "can the model *use*
> the spelled-out recipe" from "can it *invent* the technique". `helper_counters`
> is the more open test of the two.

## How to run each case (4 sessions total: 2 cases × 2 arms)

For each case, run TWO separate weak-model sessions and paste the matching prompt
verbatim as the first message:

- no_skill arm → paste `<case>/PROMPT_no_skill.txt`
- skill arm    → paste `<case>/PROMPT_skill.txt`

Each arm writes its own `<case>/no_skill/report.md` or `<case>/skill/report.md`.

## Keeping the no_skill arm honest (isolation)

The formal-verification skill is **globally installed** (`~/.claude/skills/
formal-verification`), so a no_skill session could auto-trigger it. The prompt
forbids it, but prompt-only prohibition is the weakest form. Pick one:

1. **Cleanest** — run the no_skill arm with the skill removed from the config it
   sees, e.g. a config dir that has no `skills/formal-verification`, or
   temporarily `bash scripts/install.sh --uninstall` for the no_skill session
   then re-run `bash scripts/install.sh` afterward. (Don't uninstall while the
   skill arm is running.)
2. **Acceptable** — keep it installed but, after the run, VERIFY the no_skill
   transcript never invoked the Skill tool and never read any
   `awesome-formal-verification-skill/(knowledge|adapters|tool-specific)` path.
   If it did, that arm is invalid — redo it.

Run the two arms of a case sequentially if you use option 1.

## What to bring back

Both `report.md` files per case (4 total). Hand them back here and I will do the
cited, dimension-by-dimension comparison (outcome / soundness / proof cost /
exploration cost / strategy), same as `test/cnt_abs/COMPARISON.md`.

The signal we are looking for: **does no_skill fail or flail on the weak model
while skill succeeds?** If yes on either case, the skill's value is real and just
wasn't visible on a frontier model. If both arms still tie, the skill's
methodology layer is redundant even for weak models and the value is purely in
tool-specific atoms / cost reduction.
