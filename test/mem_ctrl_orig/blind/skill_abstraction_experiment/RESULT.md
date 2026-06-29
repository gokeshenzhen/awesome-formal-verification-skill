# Skill Abstraction Experiment — Result Report

## Reproduce

Same launcher convention as `../no_skill` and `../skill`:

```bash
cd test/mem_ctrl_orig/blind/skill_abstraction_experiment
./run.sh                 # runs prove_abstraction.tcl in a fresh runs/<timestamp>/
```

Files in this directory:
- `run.sh` — launcher (sets `BENCH_DIR`/`EXP_DIR`, runs `jg -no_gui -proj … -tcl …`)
- `prove_abstraction.tcl` — the reproducible proof (bbox `u_mem.m1` + bind tracker + reconnect `assume` + `prove -all`)
- `mem_slot_bind.sv` — disclosed abstraction helper (single-slot tracker + `bind`); analyzed alongside the **unchanged** benchmark RTL
- `mem_slot_abs.sv` — earlier standalone helper variant, superseded by `mem_slot_bind.sv` (not analyzed)
- `runs/<timestamp>/` — per-run jgproject + `jg_console.log` + `prove_summary.rpt`
- `run_20260624_185303/` — the **original** blind agent run (frozen archive)

Expected result (seconds): `mem_ctrl_top.u_mem.mem_works_ndc` **proven** (engine AM),
its precondition covers hit (non-vacuous), flops drop from 16,523 → ~109 after
black-boxing. `ctrl_readback_ok` shows a CEX **under this abstraction** (expected —
the contract only constrains reads at `ndc_addr`; that property is proven on full
raw RTL in `../no_skill` / `../skill`).

---

## Classification

**DISCLOSED TRUSTED-ABSTRACTION RESULT** — not a raw-RTL signoff.

The target property `mem_ctrl_top.u_mem.mem_works_ndc` was **PROVEN** under a
disclosed memory abstraction that replaces the 512×32 `mem_imp` array instance
with a single-slot symbolic tracker. All modeling choices are disclosed below.

---

## Setup

| Item | Value |
|---|---|
| JasperGold version | 2025.12p002 (2026.02.24 13:13:22 UTC) |
| Host | workstation |
| Run timestamp | 2026-06-24 18:58 CST |
| Run directory | `run_20260624_185303/` |
| TCL script | `run_20260624_185303/prove_mem_abstraction_v3.tcl` |
| Invocation | `jg -no_gui prove_mem_abstraction_v3.tcl` |

### Benchmark RTL (unmodified)

| File | Note |
|---|---|
| `test/mem_ctrl_orig/simple_mem_design.sv` | Contains `mem_imp` (512×32 array), `simple_mem` (wrapper + assertion) |
| `test/mem_ctrl_orig/mem_ctrl_top.sv` | Top-level controller; contains `ctrl_readback_ok` |

These two files were analyzed exactly as shipped. No edits were made.

### Disclosed helper file (NOT original RTL)

| File | Purpose |
|---|---|
| `mem_slot_bind.sv` | Defines `mem_slot_abs` (single-slot tracker) and the SV `bind` statement that attaches it into every instance of `simple_mem` |

---

## Design Flop Counts

### Before abstraction (raw elaborate, no black-boxing)

From the first run (`jg_run.log`):

```
# Flops: 516 (16,523) (63 property flop bits)
```

Breakdown:
- `u_mem.m1.mem_content[0..511]` — 512 × 32 = 16,384 array flops
- `u_mem.m1.dout` — 32 flops (registered output)
- `state`, `saved_addr`, `saved_data` — ~67 controller flops
- Property-related bits — 63

Total per JasperGold: **16,523** (with property logic)

### After abstraction (black-box `u_mem.m1`)

From run v3 (`jg_run_v3.log`):

```
# Flops: 6 (172) (63 property flop bits)
```

Flop list after black-boxing:
```
saved_addr (9)
saved_data (32)
state (3)
u_mem.u_abs.rd_ndc_q (1)
u_mem.u_abs.tracked (32)
u_mem.u_abs.tracked_q (32)
```

Total structural flops: **6** (109 bits, including property bits: 172).

**Flop reduction: 16,523 → 172 (−99% of flop bits).**

---

## Strategy (Skill Reference)

This experiment followed the **Memory Abstraction** method from:

- `knowledge/fpv/complexity-management.md` — Decision tree branch:
  `Raw mem proof stalled? Yes → abstraction.md "Memory Abstraction" trigger checklist`
- `knowledge/fpv/complexity-management/abstraction.md` — Section:
  **"Memory Abstraction — Concrete Recipe: black-box one inner array instance, reconnect a single symbolic slot"**

Trigger checklist (all criteria met):
1. The `mem_imp` module contains a 512-entry × 32-bit array ≈ **16,384 flops** dominating the flop count.
2. The target `mem_works_ndc` is an **arbitrary-address write→read** assertion: uses `ndc_addr` (a `$stable` symbolic address) covering all addresses.
3. The property's **precondition cover is reachable** (non-vacuous): covered in 4 cycles (see below).
4. **No CEX** appeared during the prior raw `prove -all` runs on this property despite multiple engine scans / per-property time-limit expiries.

---

## Elaboration Command

```tcl
# Files analyzed (in order):
analyze -sv09 "<repo>/test/mem_ctrl_orig/simple_mem_design.sv"
analyze -sv09 "<repo>/test/mem_ctrl_orig/mem_ctrl_top.sv"
analyze -sv09 "<workspace>/mem_slot_bind.sv"    ;# disclosed helper only

# Elaborate with black-box on the mem_imp instance path (relative to top):
elaborate -top mem_ctrl_top -bbox_i {u_mem.m1}
```

JasperGold confirmed:
```
WARNING (WNL006): Instance "u_mem.m1" has been blackboxed due to "-bbox_i" ...
List of black boxes: 1 — u_mem.m1
```

---

## Disclosed Assumptions / Contracts

### 1. `mem_slot_bind.sv` — Single-slot abstract tracker

File: `test/mem_ctrl_orig/blind/skill_abstraction_experiment/mem_slot_bind.sv`

A `bind` statement instantiates `mem_slot_abs u_abs` into every instance of
`simple_mem`. The module registers:
- `tracked`: the last value written to `ndc_addr`
- `rd_ndc_q`: whether the previous cycle was a read at `ndc_addr`
- `tracked_q`: `tracked` delayed one cycle (for a `$past`-free contract)

This abstraction collapses the 16,384-flop `mem_content` array to **3 registers
(65 bits total)**: `tracked`, `tracked_q`, `rd_ndc_q`.

### 2. `mem_contract` assume (TCL, in `prove_mem_abstraction_v3.tcl`)

```tcl
assume -name mem_contract \
  {u_mem.u_abs.rd_ndc_q |-> u_mem.m1.dout == u_mem.u_abs.tracked_q}
```

**What this says:** When the previous cycle was a read at `ndc_addr`, the
black-boxed `m1.dout` (the registered read output) must equal the tracked value
for `ndc_addr`.

**What this leaves free:** Reads at any address other than `ndc_addr` leave
`m1.dout` unconstrained. This is sound for `mem_works_ndc` because its
consequent only fires when `addr == ndc_addr`, but it *does* invalidate
`ctrl_readback_ok` under this abstraction (see "Side Effect" below).

**Trust requirement:** This assume is not verified against the original `mem_imp`
RTL in this experiment. To upgrade to a full raw-RTL signoff, discharge this
contract separately as an assertion against the real `mem_imp`, then invoke the
theorem by `assert -set_helper mem_contract` after proving it.

### 3. Embedded assumptions (original RTL, not added by us)

```
mem_ctrl_top.u_mem.stable_addr: assume property (##1 $stable(ndc_addr));
mem_ctrl_top.u_mem.stable_data: assume property (##1 $stable(ndc_data));
```

These are part of the original benchmark design. They were preserved unmodified
and remain `temporary` (not marked approved) in the JasperGold task.

---

## Overconstraint Check

```
check_assumptions -dead_end
→ :noDeadEnd  proven (Infinite bound, 0.01 s)
→ :noConflict proven (Infinite bound, 0.01 s)
```

No assumption dead-ends detected. The constraints do not make the design
unreachable.

---

## Proof Results

From `results_detail_v3.txt` (JasperGold 2025.12p002, run 2026-06-24):

| Property | Type | Result | Bound | Time | Engine |
|---|---|---|---|---|---|
| `mem_ctrl_top.u_mem.mem_works_ndc` | assert | **proven** | Infinite | 0.081 s | AM |
| `mem_ctrl_top.u_mem.mem_works_ndc:precondition1` | cover | **covered** | 4 cycles | 0.023 s | Hp |
| `precond_cover` (explicit non-vacuity) | cover | **covered** | 4 cycles | 0.023 s | Hp |
| `mem_ctrl_top.ctrl_readback_ok` | assert | **cex** | 4 cycles | 0.007 s | AM |
| `mem_ctrl_top.ctrl_readback_ok:precondition1` | cover | covered | 4 cycles | 0.007 s | AM |
| `mem_ctrl_top.ctrl_transaction_seen` | cover | covered | 4 cycles | 0.007 s | AM |
| `:noDeadEnd` | assert | proven | Infinite | 0.009 s | Q5 |
| `:noConflict` | assert | proven | Infinite | 0.009 s | Q5 |

### PRIMARY RESULT: `mem_works_ndc` — PROVEN (Infinite, engine AM)

The assertion `mem_ctrl_top.u_mem.mem_works_ndc`:

```systemverilog
mem_works_ndc: assert property (
  symbol_write ##1 (!addr_write)[*1:$] ##1 addr_read |=> (dout_final == ndc_data)
);
```

is **proven under the disclosed memory abstraction**. The AM (Abstraction of M)
engine found an Infinite bound in 0.081 s after the flop reduction.

### Non-vacuity (precondition cover): COVERED in 4 cycles

Both the auto-generated `mem_works_ndc:precondition1` cover and the manually
declared `precond_cover` were covered in 4 cycles. The assertion is not
vacuously true.

### Side effect: `ctrl_readback_ok` — CEX under abstraction

`ctrl_readback_ok` got a counterexample under this abstraction. This is
**expected and correct**: the `mem_contract` only constrains `m1.dout` when
`addr == ndc_addr`. The controller reads at `saved_addr`, which may differ from
`ndc_addr`; in that case, `m1.dout` is unconstrained after black-boxing.

`ctrl_readback_ok` was **proven on the original full RTL** in the prior raw
`prove -all` run (disclosed in the task description). The CEX here is a
spurious artifact of the narrow abstraction — it does not represent a real bug
in the design.

### 中文说明:为什么跑 `./run.sh` 会看到 `ctrl_readback_ok` 报反例(CEX)

**这是预期现象,不是设计 bug,也不是脚本出错。** 机理如下:

1. **本抽象只接回了一个地址。** 我们用 `-bbox_i {u_mem.m1}` 把真实的 512×32
   数组黑盒掉了,然后只用这条契约把读出端口接回来:

   ```tcl
   assume mem_contract { u_mem.u_abs.rd_ndc_q |-> u_mem.m1.dout == u_mem.u_abs.tracked_q }
   ```

   `rd_ndc_q` 仅在"上一拍读的是符号地址 `ndc_addr`"时为真。**对其它任何地址的读,
   `m1.dout` 完全自由、不受约束**(因为真数组没了,我们只跟踪了 `ndc_addr` 一格)。

2. **`ctrl_readback_ok` 读的是另一个地址。** 它的属性是
   `state == S_CHECK |-> read_data == saved_data`,而 `read_data = m1.dout`。
   控制器读写的是自己的地址 `saved_addr`(来自 `req_addr`),**一般不等于 `ndc_addr`**。
   于是 `S_CHECK` 读 `saved_addr` 时 `rd_ndc_q` 为假 → 契约不约束 `m1.dout`
   → `m1.dout` 可取任意值 ≠ `saved_data` → 形式工具立刻找到反例。

3. **这是过近似(over-approximation)产生的"伪反例"。** 本抽象把除 `ndc_addr`
   外所有地址的读放成自由,是一个过近似模型。过近似的性质是:
   **抽象下证出的"proven"对真设计成立(sound);但抽象下的反例可能是伪的(spurious)。**
   - `mem_works_ndc` 只依赖 `ndc_addr` 的行为(契约恰好保住了)→ **sound 地证明**。
   - `ctrl_readback_ok` 依赖被放自由的其它地址行为 → 得到的是**伪反例**。

4. **`ctrl_readback_ok` 本身是对的。** 它在 `../no_skill` 和 `../skill` 两臂的
   **完整 raw RTL** 上已被证明(proven)。这里的 CEX 只是本窄抽象的副作用,不代表真 bug。

**想要"干净复现"(不出现这条伪反例)**:把脚本里的 `prove -all` 收窄为只证目标即可——

```tcl
prove -property {mem_ctrl_top.u_mem.mem_works_ndc}   ;# 只证这个实验的目标
prove -property {precond_cover}                      ;# 非空真(前件可达)
```

这样只会显示 `mem_works_ndc proven` + 覆盖,而 `ctrl_readback_ok` 的真证明留给
raw 臂,职责清晰。本目录默认仍用 `prove -all`,是为了一次性展示所有内嵌属性在
该抽象下的状态(并明示这条伪反例),与原始盲测 run 保持一致。

---

## Exact Commands Run (Chronological)

```bash
# Create workspace
mkdir -p test/mem_ctrl_orig/blind/skill_abstraction_experiment/run_20260624_185303

# First attempt: wrong -bbox_i path format, bind is not a TCL command in JG
jg -no_gui run_20260624_185303/prove_mem_abstraction.tcl   # ERROR — learning run

# Second attempt: fixed -bbox_i path; bind replaced with SV analyze+bind
jg -no_gui run_20260624_185303/prove_mem_abstraction_v2.tcl   # ERROR — wrong property name

# Property name probe
jg -no_gui run_20260624_185303/probe_properties.tcl   # get_property_info -list name ERROR

# Final run: prove -all to cover all embedded properties by JG-assigned names
jg -no_gui run_20260624_185303/prove_mem_abstraction_v3.tcl   # SUCCESS
```

---

## Files Created

All files are under `test/mem_ctrl_orig/blind/skill_abstraction_experiment/`:

```
mem_slot_bind.sv                          — Disclosed abstraction helper (SV bind)
mem_slot_abs.sv                           — Standalone module (not used directly; superceded by bind variant)
run_20260624_185303/
  prove_mem_abstraction.tcl               — Attempt 1 (errors, kept for audit trail)
  prove_mem_abstraction_v2.tcl            — Attempt 2 (errors, kept for audit trail)
  prove_mem_abstraction_v3.tcl            — FINAL working script
  probe_properties.tcl                    — Property name discovery utility
  jg_run.log                             — Attempt 1 log
  jg_run_v2.log                          — Attempt 2 log
  jg_run_v3.log                          — FINAL run log
  results_summary_v3.txt                 — JG summary report (final run)
  results_detail_v3.txt                  — JG detailed report (final run)
  jgproject/                             — JasperGold session directory
```

---

## Summary

| Question | Answer |
|---|---|
| Was `mem_works_ndc` resolved? | **Yes — PROVEN** (Infinite bound, 0.081 s, engine AM) |
| Method | Memory abstraction: `-bbox_i {u_mem.m1}` + single-slot `mem_slot_abs` tracker + `mem_contract` assume |
| Flops before abstraction | 16,523 (with property bits) |
| Flops after abstraction | 172 (with property bits) — **−99%** |
| Non-vacuity (precond cover) | **Covered** (4 cycles) — not vacuous |
| Overconstraint check | **No dead-ends** (`:noDeadEnd` and `:noConflict` both proven) |
| `ctrl_readback_ok` status | CEX under abstraction (expected artifact; proven on full RTL separately) |
| Classification | **DISCLOSED TRUSTED-ABSTRACTION RESULT** |

To upgrade to raw-RTL signoff for `mem_works_ndc`:
1. Prove `mem_contract` as an assertion against the full `mem_imp` RTL.
2. Re-run this script with the proven helper activated via `assert -set_helper mem_contract`.
3. The resulting proof transfers the trust from the abstracted model to the original design.
