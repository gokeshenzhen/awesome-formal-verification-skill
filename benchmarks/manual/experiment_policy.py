"""Content boundaries shared by preparation and the frozen manual launcher."""
import hashlib
import os
from pathlib import Path

PILOT = 'development_pilot_same_snapshot'
RECOVERY = 'helper_recovery_ab'
END_TO_END = 'helper_end_to_end_ab'
PREFIXES = {PILOT: 'epoch_return_pilot_', RECOVERY: 'epoch_return_recovery_ab_',
            END_TO_END: 'epoch_return_e2e_ab_'}
SKILL_DELTA = {'knowledge/fpv/complexity-management/decomposition.md'}


def series_spec(prefix, index, count):
    if count < 1 or not 1 <= index <= count:
        raise ValueError('Series index/count must be a fixed positive range')
    return dict(id=str(Path(prefix).absolute()), pair_index=index, pair_count=count,
                launch_order=['a', 'b'] if index % 2 else ['b', 'a'])


def manifest(root):
    result = {}
    for path in sorted(Path(root).rglob('*')):
        if '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        name = str(path.relative_to(root))
        if path.is_symlink():
            result[name] = {'link': os.readlink(path)}
        elif path.is_file():
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def validate_snapshots(kind, first, second):
    if kind not in PREFIXES:
        raise ValueError('Unknown experiment kind')
    left, right = manifest(first), manifest(second)
    changed = {name for name in left.keys() | right.keys() if left.get(name) != right.get(name)}
    if kind == PILOT:
        if changed:
            raise ValueError('Pilot requires identical skill snapshots')
    elif changed != SKILL_DELTA or left.keys() != right.keys():
        raise ValueError('Comparison must change only the existing decomposition leaf')
    return sorted(changed)
