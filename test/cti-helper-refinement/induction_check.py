#!/usr/bin/env python3
"""Exhaustive, dependency-free teaching model; RTL signoff is in Jasper logs.

Enumerate the mathematical one-step induction query explicitly. This is not
an RTL parser, a simulator, or a claim to expose Jasper's internal IC3 state.
"""
import argparse
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAMES = ("valid", "data_a", "data_b", "data_c", "ref_a", "ref_b", "ref_c")
RESET = (0,) * 7
INPUTS = tuple(itertools.product(range(2), range(2), range(4)))


def transition(s, u):
    v, a, b, c, ra, rb, rc = s
    step, vin, data = u
    if not step:
        return s
    return (((v << 1) | vin) & 7,
            data if vin else a, a if v & 1 else b, b if v & 2 else c,
            data, ra, rb)


def facts(s):
    v, a, b, c, ra, rb, rc = s
    ha = not (v & 1) or a == ra
    hb = not (v & 2) or b == rb
    p = not (v & 4) or c == rc
    return {"P": p, "H0_B": hb, "H1_AB": ha and hb,
            "P_and_H0": p and hb, "P_and_H1": p and ha and hb}


def record(s):
    return dict(zip(NAMES, s))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-samples", type=Path, metavar="DIR",
                        help="optionally replay TraceWeave *_sst_samples.json files from DIR")
    args = parser.parse_args()

    # Reset transitions always lead to RESET; checking each base case covers
    # those transitions. Enumerate both step choices and every remaining input.
    counts = dict.fromkeys(facts(RESET), 0)
    witnesses = dict.fromkeys(counts)
    for s in itertools.product(range(8), *([range(4)] * 6)):
        before = facts(s)
        for u in INPUTS:
            ns = transition(s, u)
            after = facts(ns)
            for name in counts:
                if before[name] and not after[name]:
                    counts[name] += 1
                    if witnesses[name] is None:
                        witnesses[name] = {"before": record(s),
                            "input": dict(zip(("step", "in_valid", "in_data"), u)),
                            "after": record(ns)}

    # Reachability is a separate question from induction over arbitrary states.
    reached = {RESET}
    queue = deque([RESET])
    while queue:
        s = queue.popleft()
        for u in INPUTS:
            ns = transition(s, u)
            if ns not in reached:
                reached.add(ns)
                queue.append(ns)

    report = {
        "method": "complete finite-state enumeration; not random testing",
        "model_source": "induction_check.py",
        "model_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "rtl_source": "parcel_pipe.sv",
        "rtl_sha256": hashlib.sha256((ROOT / "parcel_pipe.sv").read_bytes()).hexdigest(),
        "state_count": 8 * 4**6,
        "input_count": len(INPUTS),
        "reachable_state_count": len(reached),
        "obligations": {},
    }
    for name in counts:
        report["obligations"][name] = {
            "base_case": facts(RESET)[name],
            "one_step_inductive": counts[name] == 0,
            "violating_state_input_pairs": counts[name],
            "first_cti": witnesses[name],
            "true_in_all_reachable_states": all(facts(s)[name] for s in reached),
        }

    # One valid input bubble already refutes an UNGUARDED equality helper.
    bubble = transition(RESET, (1, 0, 3))
    report["unguarded_equality_reachable_cex"] = {
        "before": record(RESET),
        "input": {"step": 1, "in_valid": 0, "in_data": 3},
        "after": record(bubble),
        "data_a_equals_ref_a": bubble[1] == bubble[4],
        "original_P": facts(bubble)["P"],
    }

    # Replaying locally captured diagnostic samples is optional. A fresh clone
    # needs neither Jasper output nor TraceWeave to run the exhaustive checks.
    report["sst_transition_replay"] = "not requested"
    if args.replay_samples is not None:
        report["sst_transition_replay"] = "requested"
        for stem in ("target_sst", "helper_sst"):
            sample_file = args.replay_samples / f"{stem}_samples.json"
            if not sample_file.is_file():
                parser.error(f"missing optional replay input: {sample_file}")
            samples = json.loads(sample_file.read_text())["samples"]
            values = []
            for sample in samples:
                values.append({k.split(".")[-1]: x["value_at_center"]["dec"]
                               for k, x in sample["signals"].items()})
            a, b = values
            # The helper VCD omits C's data; check only the supplied projection.
            s = tuple(a.get(k, 0) for k in NAMES)
            ns = record(transition(s, (a["step"], a["in_valid"], a["in_data"])))
            assert all(ns[k] == b[k] for k in NAMES if k in b), stem
            report[stem + "_transition_replay"] = "pass (available state projection)"

    assert all(facts(RESET).values())
    assert counts["P"] > 0 and counts["H0_B"] > 0 and counts["P_and_H0"] > 0
    assert counts["H1_AB"] == 0 and counts["P_and_H1"] == 0
    assert all(x["true_in_all_reachable_states"] for x in report["obligations"].values())
    assert not report["unguarded_equality_reachable_cex"]["data_a_equals_ref_a"]
    out = ROOT / "evidence" / "induction.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"states": report["state_count"], "inputs": len(INPUTS),
                      "reachable": len(reached), "step_violations": counts,
                      "result": str(out)}, indent=2))


if __name__ == "__main__":
    main()
