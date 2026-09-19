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

from experiment_policy import PILOT, RECOVERY, END_TO_END, READBACK, DEPENDENCY_REUSE, PREFIXES, validate_snapshots, series_spec

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


def prepare_pair(root, revision_a, revision_b, kind=PILOT, checkpoint=None, series=None,
                 traceweave_from=None, checkpoint_log=None):
    root = check_destination(root, kind)
    if kind == END_TO_END:
        if not series or series != series_spec(series['id'], series['pair_index'], series['pair_count']):
            raise ValueError('End-to-end comparison requires a predeclared series/order')
    elif series is not None:
        raise ValueError('Only the end-to-end comparison uses a repeated series')
    commits = [subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', '--verify',
                                      f'{revision}^{{commit}}'], text=True).strip()
               for revision in (revision_a, revision_b)]
    checkpoint_files = None
    runtime_origin = None
    if checkpoint_log is not None and kind != DEPENDENCY_REUSE:
        raise ValueError('A standalone replay log is only supported for dependency recovery')
    if kind in (RECOVERY, READBACK):
        from recovery_checkpoint import inspect_source, FILES
        checkpoint_files = FILES
        if kind == READBACK:
            from readback_packet import CHECKPOINT_FILES
            checkpoint_files = CHECKPOINT_FILES
        if checkpoint is None:
            raise ValueError('Recovery requires an explicit raw checkpoint source')
        inspect_source(checkpoint, checkpoint_files)
    elif kind == DEPENDENCY_REUSE:
        from dependency_checkpoint import inspect_sources
        if checkpoint is None or checkpoint_log is None:
            raise ValueError('Dependency recovery requires the original script and raw replay log')
        inspect_sources(checkpoint, checkpoint_log)
    elif checkpoint is not None:
        raise ValueError('A neutral task cannot inherit a checkpoint')
    if kind == READBACK:
        from readback_packet import inspect_runtime_origin
        if traceweave_from is None:
            raise ValueError('Readback comparison requires an explicit sealed tool runtime')
        runtime_source, runtime_origin = inspect_runtime_origin(traceweave_from)
    elif traceweave_from is not None:
        raise ValueError('A historical runtime is only supported for the readback probe')
    subprocess.run(['sha256sum', '--status', '-c', 'CHECKSUMS.sha256'], cwd=CASE, check=True)
    if runtime_origin is None:
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
    if kind == DEPENDENCY_REUSE:
        from dependency_checkpoint import copy_checkpoint
        provenance = copy_checkpoint(checkpoint, checkpoint_log, frozen / 'checkpoint')
    elif checkpoint is not None:
        from recovery_checkpoint import copy_checkpoint
        provenance = copy_checkpoint(checkpoint, frozen / 'checkpoint', checkpoint_files)
    (frozen / 'case').mkdir()
    for name in PUBLIC_FILES:
        shutil.copy2(CASE / name, frozen / 'case' / name)
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
    if runtime_origin is None:
        for name in filter(None, names):
            target = frozen / 'traceweave' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(TW / name, target)
        (frozen / 'traceweave/.venv').mkdir()
    else:
        shutil.copytree(runtime_source, frozen / 'traceweave', ignore=ignore)
    shutil.copytree(BASE / 'runtime', root / 'runtime', ignore=ignore)
    shutil.copytree(BASE / 'probes', control / 'probes', ignore=ignore)
    shutil.copy2(BASE / 'isolate.py', control / 'isolate.py')
    shutil.copy2(BASE / 'experiment_policy.py', control / 'experiment_policy.py')
    if kind == READBACK:
        shutil.copy2(BASE / 'readback_packet.py', control / 'readback_packet.py')
    shutil.copy2(BASE / 'launch.sh', root / 'launch.sh')
    (root / 'launch.sh').chmod(0o755)
    for script in (root / 'runtime').glob('*.py'):
        script.chmod(0o755)
    plan_name = {PILOT: 'PLAN.md', RECOVERY: 'RECOVERY_PLAN.md', END_TO_END: 'E2E_PLAN.md',
                 READBACK: 'READBACK_PLAN.md', DEPENDENCY_REUSE: 'DEPENDENCY_PLAN.md'}[kind]
    shutil.copy2(BASE / 'epoch_return' / plan_name, control / 'SCORING.md')
    source = dict(kind=kind,
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  skill_commit_a=commits[0], skill_commit_b=commits[1], skill_changed_files=changed,
                  case=str(CASE), target='epoch_return_orig.P0',
                  public_files={name: checksum(CASE / name) for name in PUBLIC_FILES},
                  generator_sha256=checksum(Path(__file__)),
                  repository_commit=subprocess.check_output(
                      ['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip(),
                  checkpoint_provenance=provenance, series=series, traceweave_provenance=runtime_origin)
    common = root / 'common'
    common.mkdir()
    for name in ('TASK.md', 'AGENTS.md', 'config.toml'):
        template = BASE / 'templates' / name
        if name == 'TASK.md' and kind == RECOVERY:
            template = BASE / 'epoch_return/RECOVERY_TASK.md'
        if name == 'TASK.md' and kind == DEPENDENCY_REUSE:
            template = BASE / 'epoch_return/DEPENDENCY_TASK.md'
        if kind == READBACK and name in ('TASK.md', 'AGENTS.md'):
            template = BASE / 'epoch_return' / ('READBACK_TASK.md' if name == 'TASK.md' else 'READBACK_RULES.md')
        (common / name).write_text(template.read_text().replace('@CASE_PATH@', str(CASE)))
    (common / 'case.json').write_text(json.dumps(dict(case_path=str(CASE), target=source['target']), indent=2) + '\n')
    if kind == READBACK:
        from readback_packet import prepare_presentations
        index_text = (BASE / 'epoch_return/READBACK_MATERIALS.md').read_text().replace('@CASE_PATH@', str(CASE))
        # This evaluator-side index is never mounted separately into a client.
        (control / 'materials_index.md').write_text(index_text)
        source['readback'] = prepare_presentations(frozen, index_text)
        (common / 'mode.json').write_text(json.dumps(dict(proof_execution=False, stage='diagnosis')) + '\n')
    (control / 'source.json').write_text(json.dumps(source, indent=2) + '\n')
    for arm in 'ab':
        (root / f'blind/arm_{arm}').mkdir(parents=True)
    run_name = {PILOT: 'RUN.md', RECOVERY: 'RECOVERY_RUN.md', END_TO_END: 'E2E_RUN.md',
                READBACK: 'READBACK_RUN.md', DEPENDENCY_REUSE: 'DEPENDENCY_RUN.md'}[kind]
    readme = ((BASE / 'epoch_return' / run_name).read_text()
              .replace('@EXPERIMENT@', str(root)).replace('@SKILL_COMMIT@', commits[0])
              .replace('@OLD_COMMIT@', commits[0]).replace('@NEW_COMMIT@', commits[1]))
    if series:
        for key, value in dict(PAIR_INDEX=series['pair_index'], PAIR_COUNT=series['pair_count'],
                               FIRST_ARM=series['launch_order'][0], SECOND_ARM=series['launch_order'][1],
                               SERIES=series['id']).items():
            readme = readme.replace(f'@{key}@', str(value))
    (root / 'README_RUN.md').write_text(readme)
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
