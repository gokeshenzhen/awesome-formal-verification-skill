"""Freeze an unmodified proposed script and its inconclusive raw Jasper replay."""
import hashlib
import json
from pathlib import Path
import re
import shutil


def inspect_sources(script, log):
    paths = {'candidate.tcl': Path(script).absolute(), 'candidate.log': Path(log).absolute()}
    for path in paths.values():
        if path.is_symlink() or not path.is_file() or path.resolve() != path:
            raise ValueError('Replay inputs must be exact regular file paths, not symlinks')
    output = paths['candidate.log'].read_text()
    if 'successfully checked out licenses' not in output:
        raise ValueError('Replay log lacks successful license checkout')
    if not re.search(r'^ERROR: problem encountered at line \d+ in file ' +
                     re.escape(str(paths['candidate.tcl'])) + r'$', output, re.M):
        raise ValueError('Raw replay log must identify the supplied original script')
    # Check raw result fields, not filenames or an evaluator interpretation.
    records = re.findall(r'^HELPER_INFO_BEGIN (\S+)\n([^\n]+)\nHELPER_INFO_END \1$', output, re.M)
    statuses = [row.split()[:3] for _, row in records]
    if ['proven', 'proven', 'processed'] not in statuses or [
            'undetermined', 'undetermined', 'processed'] not in statuses:
        raise ValueError('Replay must contain both proven support and an inconclusive obligation')
    if re.search(r'^TARGET_(?:PROVE|INFO)_BEGIN\b|^REPLAY_CLOSED_PROVEN\b', output, re.M):
        raise ValueError('Checkpoint must stop before a later original-target attempt')
    return paths


def copy_checkpoint(script, log, destination):
    paths = inspect_sources(script, log)
    destination.mkdir()
    for name, path in paths.items():
        shutil.copy2(path, destination / name)
    hashes = {name: hashlib.sha256((destination / name).read_bytes()).hexdigest() for name in paths}
    (destination / 'MANIFEST.json').write_text(json.dumps(dict(
        kind='historical_raw_replay', files=hashes,
        note='Historical evidence only; paths are not live handles and prior results are not imported. '
             'No original wrapper receipt or process wall-time measurement is available; none is synthesized.'
    ), indent=2) + '\n')
    return {name: dict(source=str(path), sha256=hashes[name]) for name, path in paths.items()}
