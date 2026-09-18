#!/usr/local/bin/python3.11
"""Deliver the selected immutable attachment, without selecting a method."""
import argparse
import hashlib
import json
from pathlib import Path

INPUT = Path('/opt/experiment/input/MATERIALS.md')
LEDGER = Path('/work/input_reads.jsonl')


def page(path, start, count):
    raw = path.read_bytes()
    lines = raw.decode().splitlines()
    if not 1 <= start <= len(lines) or not 1 <= count <= 100:
        raise ValueError('start must be in the file; count must be 1..100')
    end = min(len(lines), start + count - 1)
    row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
               total_lines=len(lines), start=start, end=end)
    output = ['INPUT_PAGE ' + json.dumps(row)]
    output.extend(f'{index + 1:04d}: {lines[index]}' for index in range(start - 1, end))
    output.append('EOF' if end == len(lines) else f'NEXT: input-read --start {end + 1} --count {count}')
    return row, '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--count', type=int, default=100)
    args = parser.parse_args()
    try:
        row, output = page(INPUT, args.start, args.count)
    except ValueError as error:
        parser.error(str(error))
    print(output, flush=True)
    with LEDGER.open('a') as stream:
        stream.write(json.dumps(row) + '\n')


if __name__ == '__main__':
    main()
