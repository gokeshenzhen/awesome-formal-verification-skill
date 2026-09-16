#!/usr/local/bin/python3.11
"""Paginated delivery receipts; no technique selection or model orchestration."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path('/opt/formal-snapshot').resolve()
ENTRY = ROOT / 'adapters/claude-code/SKILL.md'
LEDGER = Path('/work/skill_reads.jsonl')


def validate_complete(ledger=LEDGER, root=ROOT, entry=ENTRY):
    if not ledger.is_file():
        raise ValueError('No skill delivery receipt. Read the installed entry first.')
    coverage = {}
    for line in ledger.read_text().splitlines():
        row = json.loads(line)
        path = Path(row['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Receipt outside frozen skill')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Skill changed since reading')
        count = len(raw.decode().splitlines())
        if row['total_lines'] != count or not 1 <= row['start'] <= row['end'] <= count:
            raise ValueError('Malformed skill receipt')
        coverage.setdefault(path, set()).update(range(row['start'], row['end'] + 1))
    if entry not in coverage:
        raise ValueError('Installed SKILL.md has not been read')
    for path, seen in coverage.items():
        if seen != set(range(1, len(path.read_text().splitlines()) + 1)):
            raise ValueError(f'Incomplete selected file: {path}; continue reading through EOF')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--count', type=int, default=100)
    args = parser.parse_args()
    path = args.path.resolve(strict=True)
    if not path.is_relative_to(ROOT) or path.suffix != '.md':
        parser.error('Read only Markdown in the installed frozen skill')
    raw = path.read_bytes()
    lines = raw.decode().splitlines()
    if not 1 <= args.start <= len(lines) or not 1 <= args.count <= 100:
        parser.error('start must be in the file; count must be 1..100')
    end = min(len(lines), args.start + args.count - 1)
    row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
               total_lines=len(lines), start=args.start, end=end)
    print('SKILL_PAGE ' + json.dumps(row), flush=True)
    for i in range(args.start - 1, end):
        print(f'{i + 1:04d}: {lines[i]}')
    print('EOF' if end == len(lines) else
          f'NEXT: skill-read {args.path} --start {end + 1} --count {args.count}', flush=True)
    with LEDGER.open('a') as stream:
        stream.write(json.dumps(row) + '\n')


if __name__ == '__main__':
    main()
