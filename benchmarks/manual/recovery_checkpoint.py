"""Copy only raw pre-revision artifacts; never copy solutions or interpretations."""
import hashlib
import json
import re
import shutil

FILES = {
    'baseline.stdout.log': 'runs/baseline.stdout.log',
    'baseline.run.json': 'runs/baseline.run.json',
    'candidate.tcl': 'credit_conservation_helper.tcl',
    'candidate.stdout.log': 'runs/credit_conservation_helper_v2.stdout.log',
    'candidate.run.json': 'runs/credit_conservation_helper_v2.run.json',
    'diagnostic.tcl': 'helper_sst.tcl',
    'diagnostic.stdout.log': 'runs/helper_sst.stdout.log',
    'diagnostic.run.json': 'runs/helper_sst.run.json',
    'diagnostic.vcd': 'helper_sst.vcd',
}


def inspect_source(source, files=FILES):
    source = source.resolve(strict=True)
    paths = {}
    for name, relative in files.items():
        path = source / relative
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(source) or not path.is_file():
            raise ValueError(f'Checkpoint file must be a regular in-scope file: {relative}')
        paths[name] = path
    baseline = json.loads(paths['baseline.run.json'].read_text())
    if baseline.get('phase') != 'baseline' or baseline.get('valid_baseline') is not True:
        raise ValueError('Checkpoint needs a valid historical baseline receipt')
    for name in ('candidate', 'diagnostic'):
        receipt = json.loads(paths[f'{name}.run.json'].read_text())
        if receipt.get('license_checkout') is not True or receipt.get('phase') != 'run':
            raise ValueError('Checkpoint trial/diagnostic did not check out a license')
    candidate = paths['candidate.stdout.log'].read_text()
    if not re.search(r'^undetermined undetermined processed ', candidate, re.M):
        raise ValueError('Checkpoint must contain the inconclusive candidate result')
    diagnostic = paths['diagnostic.stdout.log'].read_text()
    if not re.search(r'^SST_PROPERTY .*status=undetermined ', diagnostic, re.M) or not re.search(
            r'^SST_TRACE .*\btag SST$', diagnostic, re.M):
        raise ValueError('Checkpoint needs explicit Jasper SST classification, not a filename inference')
    return paths


def copy_checkpoint(source, destination, files=FILES):
    paths = inspect_source(source, files)
    destination.mkdir()
    for name, path in paths.items():
        shutil.copy2(path, destination / name)
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    (destination / 'MANIFEST.json').write_text(json.dumps(dict(
        kind='historical_raw_checkpoint', files=hashes,
        note='Historical paths/trace IDs are not current-session handles. No inherited proof result is activated.'
    ), indent=2) + '\n')
    # Absolute provenance is evaluator-only, outside the mounted checkpoint.
    return {name: dict(source=str(path), sha256=hashes[name]) for name, path in paths.items()}
