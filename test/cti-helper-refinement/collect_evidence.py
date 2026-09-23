#!/usr/bin/env python3
"""Archive exact result lines with their original log locations and hashes."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEEP = re.compile(r"^(PROPERTY_FIELDS |PROPERTY_RESULT |TRACE_METADATA |SST_RETURN |"
                  r"PROOF_SELECTED |SUPPORT_BEFORE |TEACHING_|HELPER_OLD |"
                  r"INFO \(IPF(?:036|047|057|072)\):)")
lines = ["Exact Jasper session-log excerpts; paths are relative to this example.",
         "The complete original logs remain in runs/ (not version controlled).", ""]
for run in ("baseline", "target_sst", "helper_sst", "refined"):
    logs = list((ROOT / "runs" / run / "sessionLogs").glob("session_*/jg_session_*.log"))
    if not logs:
        raise SystemExit(f"Missing Jasper session log for {run}; run the README's Jasper commands first.")
    log = max(logs, key=lambda p: p.stat().st_mtime_ns)
    lines += [f"SOURCE {log.relative_to(ROOT)}",
              "SHA256 " + hashlib.sha256(log.read_bytes()).hexdigest()]
    for number, line in enumerate(log.read_text().splitlines(), 1):
        if KEEP.match(line):
            lines.append(f"{number}: {line}")
    lines.append("")
out = ROOT / "evidence" / "proof-results.txt"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n")
print(out)
