#!/usr/local/bin/python3.11
"""Prepare one manual raw-versus-predecoded pair, with an identical skill."""
import argparse
from pathlib import Path

from experiment_policy import READBACK
from prepare_pilot import prepare_pair


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--skill-revision', default='883d481')
    parser.add_argument('--checkpoint-arm', required=True, type=Path)
    parser.add_argument('--traceweave-from', required=True, type=Path,
                        help='prior sealed experiment supplying unchanged TraceWeave source')
    args = parser.parse_args()
    prepare_pair(args.dest, args.skill_revision, args.skill_revision, kind=READBACK,
                 checkpoint=args.checkpoint_arm, traceweave_from=args.traceweave_from)


if __name__ == '__main__':
    main()
