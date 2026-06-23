# Complexity: Proof Decomposition

> Leaf of `complexity-management.md`. Break one hard proof into smaller obligations: assume-guarantee / compositional AG, helper lemmas, and state-space tunneling. Soundness rule: **only the propagated ROOT result is a verified signoff result** — local decomposition nodes are not.

## Proof Decomposition (AG / CAG)

**When to use**: Single property too complex; can be decomposed via helper lemmas or compositional reasoning.

**Template** (Assume-Guarantee):
```tcl
task -create SETUP -copy_assert -set
# Build helpers (e.g., virtual_net + assert)
proof_structure -init ROOT -from SETUP -copy_all
proof_structure -create assume_guarantee \
  -from ROOT -op_name AG1 -imp_name {AG1.G AG1.A} \
  -property [list helper1 target_prop]
prove -property AG1.A::target_prop    ;# prove target assuming helper
prove -property AG1.G::helper1        ;# prove helper independently
```

**Template** (Compositional Assume-Guarantee):
```tcl
proof_structure -init ROOT -from SETUP \
  -copy_assumes -copy_abstractions all -copy_stopats
proof_structure -create compositional_assume_guarantee \
  -from ROOT -op_name CAG -property [list prop1 prop2 ...]
prove -task {CAG.0} -assert -engine {N} -time_limit 100s
prove -task {CAG.1} -assert -engine {N} -time_limit 100s
# Check ROOT status — that is the sound result
```

**Template** (Multi-Stage AG for scaling):
```tcl
set ML_helpers_2:5 "helper2 helper3 helper4 helper5"
set ML_helpers_1:5 "helper1 ${ML_helpers_2:5}"
proof_structure -init ROOT -from SETUP -copy_all
# Stage 1: prove helpers 2:5
proof_structure -create assume_guarantee -from ROOT \
  -op_name AG_stage1 -property [list ${ML_helpers_2:5}]
# Stage 2: use helpers 1:5 to prove target
proof_structure -create assume_guarantee -from ROOT \
  -op_name AG_stage2 -property [list ${ML_helpers_1:5} addN.target]
```

**Runtime data** (adderN benchmark):
| N | Direct proof | With AG decomposition |
|---|---|---|
| 8 | ~1 min | — |
| 12 | ~50 min | ~90 s |
| 16 | ~3.6 h | ~11 min |

**Gotchas**:
- CAG supports embedded SVA only (no bind-style assertions)
- `-copy_abstractions all` is required — env constraints must propagate to CAG nodes
- `::jasper::psu::prove_all ROOT` auto-proves all obligations in the proof tree
- Local CAG node results are NOT sound; only propagated ROOT is valid for signoff

## Helper Assertions (Lemmas)

**When to use**: Target property needs intermediate invariants to converge.

**Template**:
```tcl
assert -helper -name helper1 {<invariant_expression>}
prove -property helper1
assert -set_helper helper1
prove -property target_prop -with_helpers
```

**Example** (loop-generated FIFO tag helpers):
```tcl
for {set i 0} {$i < 16} {incr i} {
  assert -helper -name help_tag_$i \
    "(id_fifo.fifo_valid\[$i\] && id_fifo.fifo_out\[$i\]\[0\]) |-> \
     (id_fifo.fifo_out\[$i\]\[75:68\] == v_top.ID)"
}
prove -property {top.v_top.ast_has_same_id_on_ID} -time_limit 2m -with_helpers
```

**Gotchas**:
- `-with_helpers` is **required** — omitting it ignores declared helpers
- `assert -mark_proven helper`: injects externally verified result (soundness depends on external proof)
- Loop-generated helpers must escape `[` and `]` in Tcl strings

## State Space Tunneling (SST)

**When to use**: Proof stalls in irrelevant initialization cycles before reaching interesting states.

**Template**:
```tcl
prove -property {target} -sst <N>    ;# N = tunnel depth
set_sst_default_trace_length 8
```

**Gotchas**: Set `-sst N` based on design init depth; too shallow is ineffective.

## See Also
- Shrinking the cone before decomposing (stopat/cutpoints/free vars): `cone-reduction.md`
- Index, soundness rules, anti-patterns: `../complexity-management.md`
