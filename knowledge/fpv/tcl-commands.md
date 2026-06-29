# FPV: TCL Commands

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation. Content is [JG-specific] unless tagged [General Tcl].

## Overview

JasperGold-specific Tcl scripting: the `-silent` idiom, scripted design/COI introspection, and where Jasper Tcl deviates from standard Tcl. For the **Tcl language itself** — axioms, quoting/bracing, the HDL-vs-Tcl escaping pitfall, `catch`, procs, list/string commands, packages — see `knowledge/shared/tcl-common.md`. For the end-to-end FPV run-file command *sequence*, see `workflow.md`.

## Quick Decision Tree

```
Scripting JasperGold in Tcl?
├─ Referencing an HDL signal/bit-range/$func in a string? .. see escaping rules in tcl-common.md
├─ Command argument might be invalid (signal/file)? ........ catch {cmd} var  (see tcl-common.md)
├─ Writing a script (not interactive)? .................... add -silent to every Jasper cmd that supports it
├─ Need design / COI facts in a variable? ................. get_design_info / get_signal_info ... -silent
└─ A standard Tcl command behaving oddly? ................. check Jasper Tcl differences (clock→tcl_clock, pid)
```

## Core Rules (JasperGold-specific)

1. **In scripts, add `-silent` to every Jasper command that supports it** — the command then returns results as a clean Tcl value instead of printing. If a command lacks `-silent`, its results are already returned as a Tcl value.
2. **Use `get_design_info` / `get_signal_info` for scripted introspection** — modules, instances, flops, registers, COI membership, signal width/indexes. Add `-silent` so you get the value, not a printout.
3. **Know the Jasper Tcl differences**: standard `clock` is renamed `tcl_clock`; `pid` returns the analysis-session PID (not the Jasper console's); some standard packages are unavailable: `Thread`, `tdbc`, `tdbc::mysql`, `tdbc::odbc`, `tdbc::postgres`.
4. **The HDL-vs-Tcl escaping pitfall applies to every Jasper script** — brace/escape Verilog references (`sig\[0:7\]`, `\$func`). Full rules in `tcl-common.md`.

## Pattern Catalog

### Scripted design & COI queries
**When to use**: introspect the elaborated design inside a script.
**Template**:
```tcl
set modList  [get_design_info -list module -silent]
set instList [get_design_info -module Mod_B2 -list instance -silent]
set width    [get_signal_info -width  wdata0 -silent]     ;# 32
set idx      [get_signal_info -indexes wdata0 -silent]    ;# 1D_Array 31 0
set coiMods  [get_design_info -property myTask::addr_conn0 -list module -silent]
# modules NOT in COI:
set notCOI ""
foreach m [get_design_info -silent -list module] {
  if { [lsearch -exact $coiMods $m] < 0 } { lappend notCOI $m }
}
```
**Gotchas**: without `-silent` these print and return verbose values — unusable in a pipeline. COI queries feed abstraction/cutpoint decisions (see `complexity-management.md`).

### Reporting & per-property status queries
**When to use**: dump a run summary to a file, or read each property's status back in a script. These are non-derivable [JG-specific] syntax atoms — get them exactly. 🔧 VERSION-SENSITIVE (switch names verified on 2025.12).
**Template**:
```tcl
# Summary to a file — `report -file` ABORTS if the file exists (ERROR EFL012).
# Always pass -force (or `rm -f` the file first). There is NO `report -details`
# switch (ERROR ESW087: No such switch "-details").
report -summary -force -result -file proof_summary.rpt

# Per-property status in a script: query field "status", NOT a `-status` switch
# (`-status` → ERROR ESW087). General form: get_property_info -list <field> <prop>.
foreach p [get_property_list -silent] {
  puts "PROP_STATUS: [get_property_info -list status $p] :: $p"
}
```
**Gotchas**:
- `report -file f` without `-force` → `ERROR (EFL012): ... file already exists`.
- `report -details` and `get_property_info -status` do **not** exist → `ERROR (ESW087): No such switch`. Use `report -summary -result` and `get_property_info -list status`.
- **Reading an `<assert>:precondition1` auto witness cover as a bug.** JG auto-generates an anti-vacuity witness cover (`<assertion>:precondition1`) on each assertion's antecedent. Under default reset modeling `!rst_n` is held deasserted after the initial reset, so an antecedent guarded by reset never recurs in-trace → the assertion is *vacuously* proven and its witness cover comes back `unreachable` / `unprocessed`. This is a **benign artifact**, not a defect; it does not affect the soundness of the proven assertions or your real functional covers.

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| Omitting `-silent` in scripts | Command prints instead of returning a clean value | add `-silent` |
| Assuming `clock`/`pid` behave as standard Tcl | Jasper renames `clock`→`tcl_clock`; `pid`=analysis-session PID | use `tcl_clock`; know `pid` semantics |
| `package require Thread`/`tdbc*` in Jasper | Those standard packages aren't shipped | install/import another way or avoid; see `tcl-common.md` |
| `report -file f` without `-force` (file exists) | `ERROR (EFL012)` aborts the run | `report ... -force -file f` (or `rm -f f` first) |
| `report -details` / `get_property_info -status` | No such switch → `ERROR (ESW087)` | `report -summary -result`; `get_property_info -list status <prop>` |
| Treating `<assert>:precondition1 unreachable` as a defect | It's JG's auto anti-vacuity witness cover on a reset-guarded antecedent | benign — see Reporting subsection |

> For general Tcl anti-patterns (HDL escaping, `catch`, proc return, bare array names) see `knowledge/shared/tcl-common.md`.

## Tool-Specific Notes

### JasperGold
- `-silent` is the key scripting switch — returns results as Tcl values instead of printing. Use it on every command that supports it.
- `get_design_info` / `get_signal_info` are the workhorse introspection commands.
- Jasper Tcl deviates from standard: `clock`→`tcl_clock`; `pid`=analysis-session PID; some std packages unavailable.

### VC Formal
> 📝 GAP — No VC Formal Tcl content in the current sources. To be added.

## Command Reference

| Command | Purpose | Tool |
|---|---|---|
| `<cmd> -silent` | return results instead of printing | JG |
| `get_design_info [-list module\|instance\|input\|flop\|register] [-module M] [-property P] -silent` | design / COI queries | JG |
| `get_signal_info -indexes\|-width <sig> -silent` | signal bit range / width | JG |
| `report -summary -result -force -file <f>` | dump run summary to file (`-force` mandatory if file exists; no `-details` switch) | JG |
| `get_property_list -silent` / `get_property_info -list status <prop>` | enumerate properties / read one property's status (field name, not `-status`) | JG |
| `tcl_clock` (vs std `clock`); `pid` | Jasper Tcl differences | JG |

For core Tcl commands (`set`, `expr`, `catch`, `proc`, list/string ops, `package require`, …) see `knowledge/shared/tcl-common.md`. For the full FPV run-file command sequence (`clear`, `analyze`, `elaborate`, `clock`, `reset`, `assume`, `assert`, `cover`, `prove`, `report`) see `workflow.md`.

## Further Reading
- For the Tcl language itself (axioms, quoting/escaping, `catch`, procs, list/string, packages): see `knowledge/shared/tcl-common.md`
- For the end-to-end FPV run-file order: see `workflow.md`
- For property declaration syntax (`assert`/`assume`/`cover` bodies): see `property-writing.md`
- For proof/engine settings (`set_proofgrid_*`, `set_proofmaster_*`): see `engine-tuning.md`
- For complexity levers used in setup (`stopat`, `-bbox_*`): see `complexity-management.md`
