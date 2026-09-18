#!/usr/local/bin/python3.11
"""Explicitly refuse proof processes in a diagnosis-only experiment."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

row = dict(at_utc=datetime.now(timezone.utc).isoformat(), command=sys.argv,
           result='refused_diagnosis_only')
with Path('/work/proof_attempts.jsonl').open('a') as stream:
    stream.write(json.dumps(row) + '\n')
print('DIAGNOSIS_ONLY: no new proof processes in this stage; submit proposals without executing them.', file=sys.stderr)
raise SystemExit(2)
