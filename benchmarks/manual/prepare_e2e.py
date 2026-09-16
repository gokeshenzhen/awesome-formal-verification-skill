#!/usr/local/bin/python3.11
"""Freeze a fixed series of manual neutral-start pairs; never run a model."""
import argparse
from pathlib import Path

from experiment_policy import END_TO_END, series_spec
from prepare_pilot import check_destination, prepare_pair


def destinations(prefix, count):
    if count < 1:
        raise ValueError('Declare a positive pair count before running any arm')
    # Check every destination before creating the first; never reuse prior runs.
    return [check_destination(Path(f'{prefix}_{index:02d}'), END_TO_END)
            for index in range(1, count + 1)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest-prefix', required=True, type=Path)
    parser.add_argument('--pairs', type=int, default=2)
    parser.add_argument('--old-revision', required=True)
    parser.add_argument('--new-revision', required=True)
    args = parser.parse_args()
    for index, root in enumerate(destinations(args.dest_prefix, args.pairs), 1):
        prepare_pair(root, args.old_revision, args.new_revision, kind=END_TO_END,
                     series=series_spec(args.dest_prefix, index, args.pairs))


if __name__ == '__main__':
    main()
