# Neutral-series packaging/environment validation — 2026-09-16

Prepared the fixed neutral-start series under
`test/epoch_return_e2e_ab_gpt55_01` and `_02`; both remain outside Git tracking.
No model session or epoch-return proof was run. Run recovery and review it first.

## Frozen experimental boundary

Both pairs use old skill `82a7408` on a and new skill `883d481` on b. Source
manifests fix **two pairs** with orders a→b and b→a. Each snapshot delta is only
the decomposition leaf. No checkpoint is included or mounted; the neutral
TASK.md files are byte-identical. Evidence:

- [pair 1 source](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/control/source.json)
- [pair 2 source](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_02/control/source.json)
- [pair 1 task](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/common/TASK.md)
- [pair 2 task](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_02/common/TASK.md)

## Checks

- **31 license-free tests passed**, including allowed treatment scope, checkpoint
  byte preservation/exclusions, no checkpoint on neutral tasks, fixed pair count,
  counterbalanced order, refusal of existing destinations and baseline/budget/
  skill-read gates. [Raw test output](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/control/unit_tests.log)
- All **four** isolated preflights returned **exit_code=0**. Each receipt points
  to full raw filesystem, client/config/discovery, toy Jasper proof/cover and
  stdio MCP readback/denied-cross-read checks:
  [1a](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/control/receipts/preflight_a.json),
  [1b](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/control/receipts/preflight_b.json),
  [2a](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_02/control/receipts/preflight_a.json),
  [2b](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_02/control/receipts/preflight_b.json).
- Wrong first-arm launches were refused before any client/session started:
  [raw refusal checks](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_e2e_ab_gpt55_01/control/order_refusal_checks.json).
  Arm workspaces remain empty and no launch receipts exist.
- `launch.sh check` passes for each prepared pair; original pilot/recovery copies
  are not patched to the newer preparation code. Global skill aliases and
  TraceWeave's repository are unchanged by packaging.

These checks establish operational readiness, not that the skill patch improves
proof outcomes. The scenario remains development data, not a held-out case.
Preparation preceded this commit; source.json records the then-current commit
and generator content hash, and pins.json seals the exact runtime and inputs.
