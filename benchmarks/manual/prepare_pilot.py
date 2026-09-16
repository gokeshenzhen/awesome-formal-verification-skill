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

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
CASE = REPO / 'test/epoch_return_orig'
TW = Path('/home/robin/Projects/mcp/TraceWeave')
PUBLIC_FILES = ('README.md', 'request_slots.sv', 'completion_queue.sv',
                'credit_return.sv', 'epoch_return_orig.sv', 'baseline.tcl',
                'CHECKSUMS.sha256')
TW_PATHS = ('server.py', 'config.py', 'custom_patterns.yaml', 'src', 'traceweave_mcp')


def check_destination(root):
    root = root.absolute()
    if root.parent.resolve() != (REPO / 'test').resolve() or not root.name.startswith('epoch_return_pilot_'):
        raise ValueError('Use a new test/epoch_return_pilot_* directory')
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


def prepare(root, revision):
    root = check_destination(root)
    commit = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', '--verify',
                                     f'{revision}^{{commit}}'], text=True).strip()
    subprocess.run(['sha256sum', '--status', '-c', 'CHECKSUMS.sha256'], cwd=CASE, check=True)
    subprocess.run(['git', '-C', str(TW), 'diff', '--quiet', 'HEAD', '--', *TW_PATHS], check=True)
    names = subprocess.check_output(['git', '-C', str(TW), 'ls-files', '-z', *TW_PATHS],
                                    text=True).split('\0')
    root.mkdir()
    control = root / 'control'
    frozen = control / 'frozen'
    frozen.mkdir(parents=True)
    export_skill(commit, frozen / 'snapshot_a')
    shutil.copytree(frozen / 'snapshot_a', frozen / 'snapshot_b', symlinks=True)
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
    shutil.copy2(BASE / 'launch.sh', root / 'launch.sh')
    (root / 'launch.sh').chmod(0o755)
    for script in (root / 'runtime').glob('*.py'):
        script.chmod(0o755)
    shutil.copy2(BASE / 'epoch_return/PLAN.md', control / 'SCORING.md')
    source = dict(kind='development_pilot_same_snapshot',
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  skill_commit_a=commit, skill_commit_b=commit,
                  case=str(CASE), target='epoch_return_orig.P0',
                  public_files={name: checksum(CASE / name) for name in PUBLIC_FILES},
                  generator_sha256=checksum(Path(__file__)),
                  repository_commit=subprocess.check_output(
                      ['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip())
    (control / 'source.json').write_text(json.dumps(source, indent=2) + '\n')
    common = root / 'common'
    common.mkdir()
    for name in ('TASK.md', 'AGENTS.md', 'config.toml'):
        (common / name).write_text((BASE / 'templates' / name).read_text().replace('@CASE_PATH@', str(CASE)))
    (common / 'case.json').write_text(json.dumps(dict(case_path=str(CASE), target=source['target']), indent=2) + '\n')
    for arm in 'ab':
        (root / f'blind/arm_{arm}').mkdir(parents=True)
    (root / 'README_RUN.md').write_text((BASE / 'epoch_return/RUN.md').read_text()
                                      .replace('@EXPERIMENT@', str(root))
                                      .replace('@SKILL_COMMIT@', commit))
    print(f'Prepared {root}. Both sessions use skill {commit}; this is not an efficacy A/B.')
    print(f'Next: {root}/launch.sh seal; then check and preflight all. No model was launched.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--skill-revision', default='82a7408', help='same immutable commit for both sessions')
    args = parser.parse_args()
    prepare(args.dest, args.skill_revision)


if __name__ == '__main__':
    main()
