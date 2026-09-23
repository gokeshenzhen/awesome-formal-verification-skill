#!/usr/bin/env python3
"""Collect this clone's Jasper results with raw log locations; never prove RTL."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGES = {
    "baseline": ROOT / "neutral/runs/baseline",
    "initial_helpers": ROOT / "runs/initial_helpers",
    "helper_sst": ROOT / "runs/helper_sst",
    "refined": ROOT / "runs/refined",
}
FIELDS = ("status", "validity_status", "min_length", "max_length", "engine", "time", "trace_id")
HELPERS = ("H_fill_ptr", "H_fill_range", "H_empty_fill", "H_full_fill", "H_mem_watch_live",
           "H_rd_data_mem", "H_bypass_head_data", "H_rd_head_data")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(project):
    logs = list(project.glob("sessionLogs/session_*/jg_session_*.log"))
    if not logs:
        return {"missing": str(project.relative_to(ROOT)), "properties": {}}
    log = max(logs, key=lambda p: int(p.parent.name.removeprefix("session_")))
    result = {"log": str(log.relative_to(ROOT)), "sha256": sha256(log),
              "properties": {}, "diagnostics": [], "exit_zero": False}
    for number, line in enumerate(log.read_text(errors="replace").splitlines(), 1):
        if line.startswith("RESULT "):
            _, name, *values = line.split()
        elif line.startswith("BASELINE_RESULT "):
            name, values = "testbench.P0", line.split()[1:]
        else:
            if line.startswith(("SST_METADATA ", "RUN_ERROR ", "BASELINE_ERROR ")):
                result["diagnostics"].append({"line": number, "raw": line})
            if "Exiting the analysis session with status 0." in line:
                result["exit_zero"] = True
            if line.startswith("Jasper Apps "):
                result["version"] = line
            continue
        if len(values) != len(FIELDS):
            raise ValueError(f"Unexpected property fields: {log}:{number}: {line}")
        result["properties"][name] = dict(zip(FIELDS, values), line=number, raw=line)
    return result


def proven(prop):
    return all(prop.get(k) == v for k, v in zip(FIELDS[:4],
                                               ("proven", "proven", "infinite", "infinite")))


def main():
    stages = {name: collect(project) for name, project in STAGES.items()}
    def prop(stage, name):
        return stages[stage]["properties"].get(name, {})
    checks = {
        "all_sessions_completed": all(s.get("exit_zero") for s in stages.values()),
        "baseline_unresolved": prop("baseline", "testbench.P0").get("status") == "undetermined",
        "initial_helper_unresolved": prop("initial_helpers", "H_mem_watch_live").get("status") == "undetermined",
        "diagnostic_tag_sst": any("tag SST" in d["raw"] for d in stages["helper_sst"].get("diagnostics", [])),
        "refined_dependencies_and_target_proven": all(proven(prop("refined", p)) for p in (*HELPERS, "testbench.P0")),
        "read_cover_reached": all(prop("refined", "testbench.C_read").get(k) == "covered"
                                  for k in ("status", "validity_status")),
    }
    sources = [p for p in ROOT.glob("*.tcl")] + list((ROOT / "neutral").glob("*"))
    result = {
        "claim": "scripted refinement replay; not a no-skill/skill agent comparison",
        "time_note": "Property-reported time is not end-to-end runtime.",
        "sources_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in sorted(sources) if p.is_file()},
        "stages": stages, "expected_demonstration": checks,
    }
    destination = ROOT / "evidence/results.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(destination)
    for name, ok in checks.items():
        print(f"{name}: {ok}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
