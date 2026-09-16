#!/usr/local/bin/python3.11
"""Local JG budget/receipt wrapper, not an AI evaluation harness."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import time

from skill_read import validate_complete

WORK = Path('/work')
CONFIG = Path('/opt/experiment/common/case.json')
JG = '/tools/cadence/jasper_2025.12p002/bin/jg'
LEDGER = WORK / 'jg_runs.jsonl'
PENDING = WORK / '.jg_inflight.json'
BUDGET = 180.0


def license_checked_out(data):
    # This installed release prints plural in -no_gui, singular in -batch.
    return b'successfully checked out license' in data


def analysis_finished(data):
    lines = data.splitlines()
    exit_requested = any(re.fullmatch(
        rb'(?:(?:\[[^\]\r\n]+\] )?% )?INFO \(IPL005\): Received request to exit from the console\.', line)
        for line in lines)
    return exit_requested and all(marker in lines for marker in [
        b'INFO (IPL015): The Tcl-thread exited with status 0.',
        b'INFO (IPL016): Exiting the analysis session with status 0.',
    ])


def load_case_config(path=CONFIG):
    """Read the sealed case identity, never infer verdicts from filenames."""
    config = json.loads(path.read_text())
    case = Path(config['case_path'])
    target = config['target']
    if not case.is_absolute() or not isinstance(target, str) or not target.strip():
        raise ValueError('Case path must be absolute and target must be nonempty')
    if any(char in target for char in '\r\n'):
        raise ValueError('Target must occupy one log line')
    return case, target


def run_completed(row):
    return row['license_checkout'] and (
        (row['exit_code'] == 0 and row['stopped_reason'] is None) or
        (row.get('analysis_finished') and row['stopped_reason'] == 'post_analysis_exit_cleanup'))


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def stop_group(proc):
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)


def execute(command, stdout_path, limit, watchdog=10.0, cleanup_grace=2.0):
    """Capture a whole direct vendor invocation, including startup/cleanup."""
    start = time.monotonic()
    row = dict(command=command, started_utc=timestamp(), limit_seconds=limit)
    reason = None
    checked_out = False
    finished_at = None
    with stdout_path.open('xb') as out:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            while proc.poll() is None:
                elapsed = time.monotonic() - start
                output = stdout_path.read_bytes()
                if not checked_out:
                    checked_out = license_checked_out(output)
                if finished_at is None and analysis_finished(output):
                    finished_at = elapsed
                if elapsed >= limit:
                    reason = 'wall_budget_exhausted'
                    stop_group(proc)
                    break
                if finished_at is not None and elapsed - finished_at >= cleanup_grace:
                    reason = 'post_analysis_exit_cleanup'
                    stop_group(proc)
                    break
                if elapsed >= watchdog and not checked_out:
                    reason = 'license_startup_watchdog'
                    stop_group(proc)
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            reason = 'interrupted'
            stop_group(proc)
        except BaseException:
            stop_group(proc)
            raise
    checked_out |= license_checked_out(stdout_path.read_bytes())
    row.update(ended_utc=timestamp(), wall_seconds=time.monotonic() - start,
               exit_code=proc.returncode, license_checkout=checked_out, stopped_reason=reason,
               analysis_finished=analysis_finished(stdout_path.read_bytes()))
    return row


def records():
    return [json.loads(line) for line in LEDGER.read_text().splitlines()] if LEDGER.exists() else []


def remaining(rows):
    return max(0.0, BUDGET - sum(r['wall_seconds'] for r in rows if r['phase'] == 'run'))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='phase', required=True)
    sub.add_parser('baseline')
    sub.add_parser('status')
    run = sub.add_parser('run')
    run.add_argument('tcl', type=Path)
    run.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    with (WORK / '.jg_run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rows = records()
        if args.phase == 'status':
            print(json.dumps(dict(remaining_seconds=remaining(rows), unfinished_run=PENDING.exists(), runs=rows), indent=2))
            return
        if PENDING.exists():
            raise ValueError('An earlier JG run has no exit receipt; preserve it and stop this arm')
        validate_complete()
        case, target = load_case_config()
        if args.phase == 'baseline':
            if rows:
                raise ValueError('Baseline already attempted; preserve this run, do not overwrite')
            tcl, project, limit = case / 'baseline.tcl', WORK / 'runs/baseline', 60.0
        else:
            if not rows or rows[0]['phase'] != 'baseline' or not rows[0]['valid_baseline']:
                raise ValueError('A successful unchanged baseline is required before investigation')
            tcl, project = args.tcl.resolve(strict=True), args.project.resolve()
            if not tcl.is_relative_to(WORK) or not project.is_relative_to(WORK):
                raise ValueError('Added Tcl/project must remain under /work')
            limit = remaining(rows)
            if limit <= 0:
                raise ValueError('Post-baseline JG budget exhausted')
        if project.exists():
            raise ValueError('Project exists; choose a fresh path')
        project.parent.mkdir(parents=True, exist_ok=True)
        out = project.with_name(project.name + '.stdout.log')
        PENDING.write_text(json.dumps(dict(phase=args.phase, tcl=str(tcl), project=str(project),
                                            started_utc=timestamp())) + '\n')
        row = execute([JG, '-fpv', '-batch', '-proj', str(project), '-tcl', str(tcl)], out, limit)
        row['phase'] = args.phase
        row['valid_baseline'] = (args.phase == 'baseline' and run_completed(row)
                                 and f'PROPERTY_INFO_END {target}' in out.read_text().splitlines())
        with LEDGER.open('a') as stream:
            stream.write(json.dumps(row) + '\n')
        project.with_name(project.name + '.run.json').write_text(json.dumps(row, indent=2) + '\n')
        PENDING.unlink()
        print(json.dumps(row, indent=2))
        print(f'RAW_STDOUT {out}')
        if row['stopped_reason'] == 'post_analysis_exit_cleanup':
            print('JG_CLEANUP_NOTICE: analysis/Tcl exited normally; leftover process was terminated. '
                  'Preserve the vendor exit code and count all cleanup wall time; this is not a property verdict.')
        if not run_completed(row) or (args.phase == 'baseline' and not row['valid_baseline']):
            raise SystemExit(2)
        raise SystemExit(0)


if __name__ == '__main__':
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'JG_RUN_REFUSED: {error}', file=sys.stderr)
        raise SystemExit(2)
