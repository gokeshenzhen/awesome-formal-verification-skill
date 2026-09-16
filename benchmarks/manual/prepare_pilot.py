#!/usr/local/bin/python3.11
"""Freeze two independent manual pilot sessions. Never invoke model inference."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

from experiment_policy import PILOT, RECOVERY, PREFIXES, validate_snapshots

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
CASE = REPO / 'test/epoch_return_orig'
TW = Path('/home/robin/Projects/mcp/TraceWeave')
PUBLIC_FILES = ('README.md', 'request_slots.sv', 'completion_queue.sv',
                'credit_return.sv', 'epoch_return_orig.sv', 'baseline.tcl',
                'CHECKSUMS.sha256')
TW_PATHS = ('server.py', 'config.py', 'custom_patterns.yaml', 'src', 'traceweave_mcp')


def check_destination(root, kind=PILOT):
    root = root.absolute()
    if kind not in PREFIXES or root.parent.resolve() != (REPO / 'test').resolve() or not root.name.startswith(PREFIXES[kind]):
        raise ValueError('Use a new test directory with the prefix for this experiment kind')
    if root.exists() or root.is_symlink():
        raise ValueError('Destination exists; preserve it and choose a fresh name')
    return root


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_skill(commit, destination):
    archive = subprocess.check_output(['git', '-C', str(REPO), 'archive', '--format=tar',
                                      commit, 'knowledge', 'tool-specific', 'adapters'])
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(destination, filter='data')


def prepare_pair(root, revision_a, revision_b, kind=PILOT, checkpoint=None):
    root = check_destination(root, kind)
    commits = [subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', '--verify',
                                      f'{revision}^{{commit}}'], text=True).strip()
               for revision in (revision_a, revision_b)]
    if kind == RECOVERY:
        from recovery_checkpoint import inspect_source
        if checkpoint is None:
            raise ValueError('Recovery requires an explicit raw checkpoint source')
        inspect_source(checkpoint)
    elif checkpoint is not None:
        raise ValueError('A neutral pilot cannot inherit a checkpoint')
    subprocess.run(['sha256sum', '--status', '-c', 'CHECKSUMS.sha256'], cwd=CASE, check=True)
    subprocess.run(['git', '-C', str(TW), 'diff', '--quiet', 'HEAD', '--', *TW_PATHS], check=True)
    names = subprocess.check_output(['git', '-C', str(TW), 'ls-files', '-z', *TW_PATHS],
                                    text=True).split('\0')
    root.mkdir()
    control = root / 'control'
    frozen = control / 'frozen'
    frozen.mkdir(parents=True)
    export_skill(commits[0], frozen / 'snapshot_a')
    export_skill(commits[1], frozen / 'snapshot_b')
    changed = validate_snapshots(kind, frozen / 'snapshot_a', frozen / 'snapshot_b')
    provenance = None
    if checkpoint is not None:
        from recovery_checkpoint import copy_checkpoint
        provenance = copy_checkpoint(checkpoint, frozen / 'checkpoint')
    (frozen / 'case').mkdir()
    for name in PUBLIC_FILES:
        shutil.copy2(CASE / name, frozen / 'case' / name)
    for name in filter(None, names):
        target = frozen / 'traceweave' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TW / name, target)
    (frozen / 'traceweave/.venv').mkdir()
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
    shutil.copytree(BASE / 'runtime', root / 'runtime', ignore=ignore)
    shutil.copytree(BASE / 'probes', control / 'probes', ignore=ignore)
    shutil.copy2(BASE / 'isolate.py', control / 'isolate.py')
    shutil.copy2(BASE / 'experiment_policy.py', control / 'experiment_policy.py')
    shutil.copy2(BASE / 'launch.sh', root / 'launch.sh')
    (root / 'launch.sh').chmod(0o755)
    for script in (root / 'runtime').glob('*.py'):
        script.chmod(0o755)
    plan_name = 'PLAN.md' if kind == PILOT else 'RECOVERY_PLAN.md'
    shutil.copy2(BASE / 'epoch_return' / plan_name, control / 'SCORING.md')
    source = dict(kind=kind,
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  skill_commit_a=commits[0], skill_commit_b=commits[1], skill_changed_files=changed,
                  case=str(CASE), target='epoch_return_orig.P0',
                  public_files={name: checksum(CASE / name) for name in PUBLIC_FILES},
                  generator_sha256=checksum(Path(__file__)),
                  repository_commit=subprocess.check_output(
                      ['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip(),
                  checkpoint_provenance=provenance)
    (control / 'source.json').write_text(json.dumps(source, indent=2) + '\n')
    common = root / 'common'
    common.mkdir()
    for name in ('TASK.md', 'AGENTS.md', 'config.toml'):
        template = BASE / 'templates' / name
        if name == 'TASK.md' and kind == RECOVERY:
            template = BASE / 'epoch_return/RECOVERY_TASK.md'
        (common / name).write_text(template.read_text().replace('@CASE_PATH@', str(CASE)))
    (common / 'case.json').write_text(json.dumps(dict(case_path=str(CASE), target=source['target']), indent=2) + '\n')
    for arm in 'ab':
        (root / f'blind/arm_{arm}').mkdir(parents=True)
    run_name = 'RUN.md' if kind == PILOT else 'RECOVERY_RUN.md'
    (root / 'README_RUN.md').write_text((BASE / 'epoch_return' / run_name).read_text()
                                      .replace('@EXPERIMENT@', str(root))
                                      .replace('@SKILL_COMMIT@', commits[0])
                                      .replace('@OLD_COMMIT@', commits[0])
                                      .replace('@NEW_COMMIT@', commits[1]))
    print(f'Prepared {root}; kind={kind}; skill a={commits[0]}, b={commits[1]}.')
    print(f'Next: {root}/launch.sh seal; then check and preflight all. No model was launched.')


def prepare(root, revision):
    prepare_pair(root, revision, revision)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--skill-revision', default='82a7408', help='same immutable commit for both sessions')
    args = parser.parse_args()
    prepare(args.dest, args.skill_revision)


if __name__ == '__main__':
    main()
