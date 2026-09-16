# Epoch-tagged request return unit

This is an original, standalone RTL benchmark, not extracted from OpenTitan.
It models client request slots, a small completion transport, and delayed credit
returns. The modules use one rising-edge clock and an active-low initial reset.

## Interface and behavior

- There are two request slots, two transport entries, and 255 resource credits.
  An allocation accepts a nonzero 8-bit quantity no greater than current free
  credit, into a currently empty selected slot. It toggles that slot's epoch bit.
- An issue copies an allocated request into an empty selected transport entry.
  Each allocation issues at most once. Transport completion may select either
  occupied entry, so completions may be out of order.
- Completion moves the entry into a one-entry response register only when that
  register was empty at the start of the cycle. `take_i` consumes its old content.
  A response may be held indefinitely. No fairness or progress is assumed.
- A consumed response retires a live request only if slot and epoch match.
  Otherwise it is stale and is discarded. A matching completion refunds the
  quantity carried by the response, not a fresh read of the request quantity.
- Cancel releases a selected live request, including an issued request. Flush
  releases every live request. Neither operation deletes in-flight transport
  entries or held responses; those copies can complete later.
- Flush wins over allocation, issue, cancel and retirement. Without flush,
  cancellation wins over issue/retirement of the same slot. Other-slot operations
  may overlap. Completed/cancelled slots and transport entries are not reused in
  the same cycle: all acceptance checks inspect pre-edge state.
- Before allocation, check that its next epoch does not occur in a valid
  transport entry or held response for that slot. This permits reuse with an
  older response still outstanding, but prevents one-bit epoch wraparound from
  aliasing that old transaction. A blocked allocation may be retried later.
- Allocation consumes free credit immediately. Cancellation, flush and accepted
  completion enter a two-stage refund pipeline; its last stage credits the free
  counter. Transport draining continues during flush.
- `idle_o` means no client request and no pending refund. Old stale transport
  entries/responses may still exist while idle.

All non-clock/reset inputs are unconstrained. Requests that fail an acceptance
check do nothing; simultaneous input combinations are legal. Do not add input
assumptions to exclude inconvenient overlaps or delays.

## Task and integrity

Obtain the strongest sound conclusion for the embedded assertion
`epoch_return_orig.P0`: whenever client-visible work and refund processing are
idle, all credits have returned. Keep the RTL, target, reset, widths and baseline
unchanged. Added verification-only files are allowed but must be disclosed.

Run `sha256sum -c CHECKSUMS.sha256` before and after the work. First run the
provided `baseline.tcl` unchanged. Allow 180 seconds of total post-baseline
Jasper process wall time, including help, failed attempts and final replay;
preserve raw projects, logs and per-run timing receipts. Follow the assigned
workspace's execution instructions when running in an isolated experiment.

Record each result with its actual status, bound, engine, time and trace type.
Do not infer a proof from a search that found no trace. Keep candidate assertions
inactive unless their proof obligations have been discharged in the unchanged
model. Report any remaining limitations and whether reachability was checked.
