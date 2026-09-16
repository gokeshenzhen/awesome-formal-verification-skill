#!/usr/local/bin/python3.11
"""Prepare one manual old/new comparison from an identical raw failure checkpoint."""
import argparse
from pathlib import Path

from experiment_policy import RECOVERY
from prepare_pilot import prepare_pair


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--old-revision', required=True)
    parser.add_argument('--new-revision', required=True)
    parser.add_argument('--checkpoint-arm', required=True, type=Path)
    args = parser.parse_args()
    prepare_pair(args.dest, args.old_revision, args.new_revision,
                 kind=RECOVERY, checkpoint=args.checkpoint_arm)


if __name__ == '__main__':
    main()
