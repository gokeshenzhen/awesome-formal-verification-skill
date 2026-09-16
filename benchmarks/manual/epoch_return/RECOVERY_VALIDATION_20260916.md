# Recovery packaging/environment validation — 2026-09-16

Prepared `test/epoch_return_recovery_ab_gpt55_01`, outside Git tracking. This
records packaging and environment checks, **not model or refinement efficacy**.
No model session and no epoch-return proof was run by the preparer.

- Old skill `82a7408`, new skill `883d481`; the only exported skill difference
  is `knowledge/fpv/complexity-management/decomposition.md`.
  Source: local experiment `control/source.json` and the corresponding Git diff.
- Raw historical checkpoint files are byte-preserved and allowlisted; the
  public manifest has hashes, while absolute source provenance stays outside
  the agent mount. Source: `control/frozen/checkpoint/MANIFEST.json` and
  `control/source.json`. Interpretation/solution/session files were excluded.
- License-free regression: **28 tests passed**. Raw output:
  [unit_tests.log](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_recovery_ab_gpt55_01/control/unit_tests.log).
- Both isolated preflights returned **exit_code=0** with the same pins hash:
  [a receipt](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_recovery_ab_gpt55_01/control/receipts/preflight_a.json),
  [b receipt](/home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_recovery_ab_gpt55_01/control/receipts/preflight_b.json).
  Each receipt identifies its raw evidence directory: filesystem checks,
  native client/config/skill discovery, toy JG proof/cover, real stdio MCP
  readback, read-only checkpoint access and denied access to the original pilot.
- Both discovery aliases resolve to the same selected snapshot inside each
  arm. Preflight performs no model turn; toy EDA work is outside arm ledgers.

Generated README_RUN.md contains the exact manual launch instructions. Review
both recovery outcomes before running the separate neutral comparison. Do not
change the skill or reseal this prepared pair in response to model results.

Preparation preceded this packaging commit; source.json truthfully records the
then-current repository commit and the generator content hash. The frozen
runtime, policy, templates and source provenance are covered by pins.json.
