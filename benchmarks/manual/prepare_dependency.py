#!/usr/local/bin/python3.11
"""Prepare one manually launched old/new skill pair from a raw stalled replay."""
import argparse
from pathlib import Path

from experiment_policy import DEPENDENCY_REUSE
from prepare_pilot import prepare_pair


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--old-revision', required=True)
    parser.add_argument('--new-revision', required=True)
    parser.add_argument('--candidate-script', required=True, type=Path)
    parser.add_argument('--replay-log', required=True, type=Path)
    args = parser.parse_args()
    prepare_pair(args.dest, args.old_revision, args.new_revision, kind=DEPENDENCY_REUSE,
                 checkpoint=args.candidate_script, checkpoint_log=args.replay_log)


if __name__ == '__main__':
    main()
