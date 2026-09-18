#!/usr/local/bin/python3.11
"""Prepare/check/launch ONE manual arm. Never invokes an LLM non-interactively."""
import argparse
from datetime import datetime, timezone
import hashlib
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from experiment_policy import RECOVERY, END_TO_END, READBACK, validate_snapshots, series_spec

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'control'
REPO = ROOT.parents[1]
SOURCE_FILE = CONTROL / 'source.json'
SOURCE = json.loads(SOURCE_FILE.read_text())
CASE = Path(SOURCE['case'])
TW = Path('/home/robin/Projects/mcp/TraceWeave')
USER_DIR = Path('/home/robin')
JG_ROOT = Path('/tools/cadence/jasper_2025.12p002')
VERDI = Path('/tools/synopsys/verdi/V-2023.12-SP2')
FROZEN = CONTROL / 'frozen'
PIN = CONTROL / 'pins.json'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def tree_manifest(path):
    result = {}
    for file in sorted(path.rglob('*')):
        if '__pycache__' in file.parts or file.suffix == '.pyc':
            continue
        if file.is_symlink():
            result[str(file.relative_to(path))] = {'link': os.readlink(file)}
        elif file.is_file():
            result[str(file.relative_to(path))] = digest(file)
    return result


def now():
    return datetime.now(timezone.utc).isoformat()


def seal():
    if any((CONTROL / 'receipts').glob('launch_*.json')):
        raise ValueError('Cannot reseal after an arm was launched')
    binary = Path(shutil.which('codex')).resolve()
    node = Path(shutil.which('node')).resolve()
    runtime_origin = SOURCE.get('traceweave_provenance')
    if runtime_origin:
        if SOURCE['kind'] != READBACK or tree_manifest(FROZEN / 'traceweave') != runtime_origin['files']:
            raise ValueError('Historical runtime does not match its recorded frozen provenance')
        tw_commit = runtime_origin['traceweave_commit']
    else:
        for name, value in tree_manifest(FROZEN / 'traceweave').items():
            if isinstance(value, str) and digest(TW / name) != value:
                raise ValueError('Live TraceWeave no longer matches the prepared runtime; preserve the copy and review provenance')
        tw_commit = subprocess.check_output(['git', '-C', str(TW), 'rev-parse', 'HEAD'], text=True).strip()
    pins = dict(created_utc=now(), codex_binary=str(binary), codex_sha256=digest(binary),
                codex_host_sha256=digest(binary.with_name('codex-code-mode-host')),
                codex_path=tree_manifest(binary.parent.parent / 'codex-path'),
                codex_version=subprocess.check_output([str(binary), '--version'], text=True).strip(),
                node=str(node), node_sha256=digest(node),
                traceweave_commit=tw_commit,
                frozen=tree_manifest(FROZEN), common=tree_manifest(ROOT / 'common'),
                runtime=tree_manifest(ROOT / 'runtime'), probes=tree_manifest(CONTROL / 'probes'),
                launcher=digest(__file__), launch_sh=digest(ROOT / 'launch.sh'),
                policy_sha256=digest(CONTROL / 'experiment_policy.py'),
                source=SOURCE, source_sha256=digest(SOURCE_FILE),
                scoring_sha256=digest(CONTROL / 'SCORING.md'),
                model='gpt-5.5', reasoning_effort='medium', case=str(CASE),
                venv=tree_manifest(TW / '.venv'),
                python_sha256=digest('/usr/local/bin/python3.11'), bwrap_sha256=digest('/usr/bin/bwrap'),
                jasper_launcher_sha256=None if SOURCE['kind'] == READBACK else digest(JG_ROOT / 'bin/jg'))
    if SOURCE['kind'] == READBACK:
        pins['readback_policy_sha256'] = digest(CONTROL / 'readback_packet.py')
        pins['materials_index_sha256'] = digest(CONTROL / 'materials_index.md')
    PIN.write_text(json.dumps(pins, indent=2) + '\n')
    print(f'Sealed {PIN}; launch will refuse drift')


def verify():
    pins = json.loads(PIN.read_text())
    for key, path in [('frozen', FROZEN), ('common', ROOT / 'common'),
                      ('runtime', ROOT / 'runtime'), ('probes', CONTROL / 'probes'), ('venv', TW / '.venv'),
                      ('codex_path', Path(pins['codex_binary']).parent.parent / 'codex-path')]:
        if pins[key] != tree_manifest(path):
            raise ValueError(f'Pinned {key} content changed')
    for key, path in [('launcher', Path(__file__)), ('launch_sh', ROOT / 'launch.sh'),
                      ('policy_sha256', CONTROL / 'experiment_policy.py'),
                      ('source_sha256', SOURCE_FILE), ('scoring_sha256', CONTROL / 'SCORING.md'),
                      ('codex_sha256', Path(pins['codex_binary'])), ('node_sha256', Path(pins['node'])),
                      ('codex_host_sha256', Path(pins['codex_binary']).with_name('codex-code-mode-host')),
                      ('bwrap_sha256', Path('/usr/bin/bwrap')),
                      ('python_sha256', Path('/usr/local/bin/python3.11'))]:
        if pins[key] != digest(path):
            raise ValueError(f'Pinned executable changed: {key}')
    if SOURCE['kind'] != READBACK and pins['jasper_launcher_sha256'] != digest(JG_ROOT / 'bin/jg'):
        raise ValueError('Pinned Jasper launcher changed')
    if SOURCE['kind'] == READBACK:
        for field, name in [('readback_policy_sha256', 'readback_packet.py'),
                            ('materials_index_sha256', 'materials_index.md')]:
            if pins[field] != digest(CONTROL / name):
                raise ValueError('Pinned readback preparation policy changed')
        from readback_packet import validate_presentations
        validate_presentations(FROZEN, (CONTROL / 'materials_index.md').read_text(), SOURCE['readback'])
    changed = validate_snapshots(SOURCE['kind'], FROZEN / 'snapshot_a', FROZEN / 'snapshot_b')
    if changed != SOURCE['skill_changed_files']:
        raise ValueError('Skill treatment differs from its declared delta')
    if SOURCE['kind'] == END_TO_END:
        series = SOURCE['series']
        if series != series_spec(series['id'], series['pair_index'], series['pair_count']):
            raise ValueError('Invalid preregistered series/order')
    checkpoint = FROZEN / 'checkpoint'
    if (SOURCE['kind'] in (RECOVERY, READBACK)) != checkpoint.is_dir():
        raise ValueError('Checkpoint presence must match the experiment kind')
    if checkpoint.exists():
        expected = json.loads((checkpoint / 'MANIFEST.json').read_text())['files']
        actual = tree_manifest(checkpoint)
        actual.pop('MANIFEST.json')
        if actual != expected:
            raise ValueError('Checkpoint differs from its raw manifest')
    for arm in 'ab':
        snapshot = FROZEN / f'snapshot_{arm}'
        for part in ['knowledge', 'tool-specific']:
            if (snapshot / 'adapters/claude-code' / part).resolve() != snapshot / part:
                raise ValueError('Snapshot resource link escapes the selected tree')
    subprocess.run(['sha256sum', '--status', '-c', 'CHECKSUMS.sha256'], cwd=FROZEN / 'case', check=True)
    return pins


def environment():
    if os.environ.get('HOME') != str(USER_DIR):
        raise ValueError('This local launcher requires the existing /home/robin login; HOME is not reassigned')
    # Do not inherit hooks, memory locations, agent sockets, remote endpoints,
    # provider overrides, SSH sockets, Python paths, or arbitrary credential vars.
    names = ['HOME', 'USER', 'LOGNAME', 'TERM', 'LANG', 'LC_ALL', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
             'NO_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy']
    env = {name: os.environ[name] for name in names if name in os.environ}
    env.update(PATH='/opt/experiment/bin:/opt/codex/bin:/opt/codex/codex-path:/opt/node/bin:/usr/local/bin:/usr/bin:/bin',
               SHELL='/bin/bash', PYTHONDONTWRITEBYTECODE='1',
               XDG_CACHE_HOME='/home/robin/.cache', XDG_RUNTIME_DIR='/run/user/1000',
               CDS_LIC_FILE='5280@workstation', CDS_LICENSE_FILE='5280@workstation',
               LM_LICENSE_FILE='5280@workstation', SNPSLMD_LICENSE_FILE='2700@workstation',
               Jasper_ROOT=str(JG_ROOT), VERDI_HOME=str(VERDI), NOVAS_HOME=str(VERDI),
               TRACEWEAVE_CACHE_DIR='/home/robin/.cache/traceweave',
               TRACEWEAVE_SOURCE_GRAPH_DISK_CACHE='1', TRACEWEAVE_SOURCE_GRAPH_DISK_CACHE_MAX_ENTRIES='8',
               TRACEWEAVE_SOURCE_GRAPH_DISK_CACHE_MAX_BYTES='536870912',
               TRACEWEAVE_SOURCE_GRAPH_SEMANTIC_SESSION='1', TRACEWEAVE_TELEMETRY='1',
               TZ='America/Los_Angeles')
    if SOURCE['kind'] == READBACK:
        for name in ['CDS_LIC_FILE', 'CDS_LICENSE_FILE', 'LM_LICENSE_FILE', 'SNPSLMD_LICENSE_FILE',
                     'Jasper_ROOT', 'VERDI_HOME', 'NOVAS_HOME']:
            env.pop(name, None)
    return env


def make_private_state(base, auth=False):
    base.mkdir(parents=True, exist_ok=False)
    base.chmod(0o700)
    sandbox_user_dir = base / 'user'
    for rel in ['.codex/skills', '.agents/skills', '.cache', '.local/share', 'Projects']:
        (sandbox_user_dir / rel).mkdir(parents=True, exist_ok=True)
    for client in ['.codex', '.agents']:
        (sandbox_user_dir / client / 'skills/formal-verification').symlink_to(
            '/opt/formal-snapshot/adapters/claude-code')
    if auth:
        # Private per-arm credential copy, never printed or included in a manifest.
        target = sandbox_user_dir / '.codex/auth.json'
        shutil.copyfile(USER_DIR / '.codex/auth.json', target)
        target.chmod(0o600)
    return sandbox_user_dir


def command(arm, sandbox_user_dir, work, pins, argv, probes=False):
    args = ['/usr/bin/bwrap', '--die-with-parent', '--new-session',
            '--unshare-pid', '--unshare-ipc', '--unshare-uts', '--hostname', 'workstation',
            '--cap-drop', 'ALL', '--ro-bind', '/usr', '/usr',
            '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/sbin', '/sbin',
            '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
            '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--tmpfs', '/run',
            '--dir', '/run/user/1000', '--dir', '/var/tmp', '--dir', '/etc']
    for name in ['hosts', 'hostname', 'resolv.conf', 'nsswitch.conf', 'passwd', 'group',
                 'ld.so.cache', 'localtime', 'ssl', 'pki', 'crypto-policies', 'services',
                 'protocols', 'os-release', 'redhat-release']:
        path = Path('/etc') / name
        if path.exists():
            args += ['--ro-bind', str(path), str(path)]
    args += ['--ro-bind', '/sys/devices/system/cpu', '/sys/devices/system/cpu',
             '--bind', str(sandbox_user_dir), str(USER_DIR),
             '--ro-bind', str(ROOT / 'common/config.toml'), str(USER_DIR / '.codex/config.toml'),
             '--ro-bind', str(FROZEN / f'snapshot_{arm}'), '/opt/formal-snapshot',
             '--ro-bind', str(FROZEN / 'case'), str(CASE),
             '--ro-bind', str(FROZEN / 'traceweave'), str(TW),
             '--ro-bind', str(TW / '.venv'), str(TW / '.venv'),
             '--ro-bind', str(Path(pins['codex_binary']).parent), '/opt/codex/bin',
             '--ro-bind', str(Path(pins['codex_binary']).parent.parent / 'codex-path'), '/opt/codex/codex-path',
             '--ro-bind', str(Path(pins['node']).parent.parent), '/opt/node',
             '--ro-bind', str(ROOT / 'runtime'), '/opt/experiment/runtime',
             '--ro-bind', str(ROOT / 'common'), '/opt/experiment/common',
             '--dir', '/opt/experiment/bin',
             '--symlink', '/opt/experiment/runtime/skill_read.py', '/opt/experiment/bin/skill-read',
             '--bind', str(work), '/work',
             '--ro-bind', str(ROOT / 'common/AGENTS.md'), '/work/AGENTS.md']
    if SOURCE['kind'] == READBACK:
        args += ['--ro-bind', str(FROZEN / f'input_{arm}'), '/opt/experiment/input',
                 '--symlink', '/opt/experiment/runtime/input_read.py', '/opt/experiment/bin/input-read',
                 '--symlink', '/opt/experiment/runtime/proof_disabled.py', '/opt/experiment/bin/jg-run',
                 '--symlink', '/opt/experiment/runtime/proof_disabled.py', '/opt/experiment/bin/jg']
        if probes:
            # Ground-truth mechanical values are available to model-free checks
            # only; the raw-input arm never receives this JSON in a model run.
            args += ['--ro-bind', str(FROZEN / 'readback_packet.json'), '/opt/readback-check.json']
    else:
        args += ['--ro-bind', str(JG_ROOT), str(JG_ROOT), '--ro-bind', str(VERDI), str(VERDI),
                 '--symlink', '/opt/experiment/runtime/jg_run.py', '/opt/experiment/bin/jg-run']
    if SOURCE['kind'] in (RECOVERY, READBACK):
        args += ['--ro-bind', str(FROZEN / 'checkpoint'), '/opt/experiment/checkpoint']
    if probes:
        args += ['--ro-bind', str(CONTROL / 'probes'), '/opt/preflight']
    return args + ['--chdir', '/work', '--'] + argv


def preflight(arm, pins):
    starting_pin = digest(PIN)
    parent = CONTROL / 'preflight'
    parent.mkdir(exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix=f'{arm}.', dir=parent))
    work = base / 'work'
    work.mkdir()
    user = make_private_state(base / 'state')
    probe = 'readback_smoke.py' if SOURCE['kind'] == READBACK else 'smoke.py'
    args = command(arm, user, work, pins,
                   [str(TW / '.venv/bin/python'), f'/opt/preflight/{probe}'], probes=True)
    with (base / 'stdout.log').open('xb') as log:
        proc = subprocess.Popen(args, env=environment(), stdout=log, stderr=subprocess.STDOUT)
        try:
            exit_code = proc.wait(timeout=120 if SOURCE['kind'] == READBACK else 90)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            exit_code = 124
    if digest(PIN) != starting_pin or verify() != pins:
        raise ValueError('Inputs changed during preflight; results cannot certify this configuration')
    receipt = dict(arm=arm, checked_utc=now(), pins_sha256=starting_pin,
                   exit_code=exit_code, evidence_dir=str(base))
    (CONTROL / 'receipts').mkdir(exist_ok=True)
    (CONTROL / f'receipts/preflight_{arm}.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    if exit_code:
        print((base / 'stdout.log').read_text()[-10000:])
        raise ValueError('Isolation/tool preflight failed; do not launch an arm')


def launch(arm, pins):
    receipt_dir = CONTROL / 'receipts'
    prior = json.loads((receipt_dir / f'preflight_{arm}.json').read_text())
    if prior['exit_code'] != 0 or prior['pins_sha256'] != digest(PIN):
        raise ValueError('A passing preflight for the sealed configuration is required')
    work = ROOT / f'blind/arm_{arm}'
    if list(work.iterdir()):
        raise ValueError('Arm output is not empty; preserve it and prepare a fresh pair')
    receipt = receipt_dir / f'launch_{arm}.json'
    if receipt.exists():
        raise ValueError('Arm was already launched; do not reuse the run')
    if SOURCE['kind'] == END_TO_END:
        first = SOURCE['series']['launch_order'][0]
        if arm != first and not (receipt_dir / f'launch_{first}.json').exists():
            raise ValueError(f'Preregistered order requires arm {first} first')
    if SOURCE['kind'] == READBACK:
        first = SOURCE['readback']['launch_order'][0]
        if arm != first and not (receipt_dir / f'launch_{first}.json').exists():
            raise ValueError(f'Preregistered order requires arm {first} first')
    if not sys.stdin.isatty():
        raise ValueError('Launch the manual arm from a real terminal')
    user = CONTROL / f'private/arm_{arm}/user'
    env = environment()
    row = dict(arm=arm, started_utc=now(), pins_sha256=digest(PIN),
               model='gpt-5.5', effort='medium', internal_cwd='/work', host_output=str(work),
               environment_sha256=hashlib.sha256(json.dumps(env, sort_keys=True).encode()).hexdigest(),
               private_session_dir=str(user / '.codex'),
               scope=('mount/PID isolation; no proof-tool mounts; network retained for model API'
                      if SOURCE['kind'] == READBACK else
                      'mount/PID isolation; network retained for model API and EDA licenses'))
    other = receipt_dir / f'launch_{"b" if arm == "a" else "a"}.json'
    if other.exists():
        before = json.loads(other.read_text())
        if not before.get('ended_utc'):
            raise ValueError('Run the arms sequentially; other launch has not ended')
        if before['environment_sha256'] != row['environment_sha256'] or before['pins_sha256'] != row['pins_sha256']:
            raise ValueError('Launch conditions differ from the other arm')
    make_private_state(user.parent, auth=True)
    shutil.copyfile(ROOT / 'common/AGENTS.md', work / 'AGENTS.md')
    receipt.write_text(json.dumps(row, indent=2) + '\n')
    prompt = '请完整读取 /opt/experiment/common/TASK.md，按其中要求完成 /work 中分配的任务。'
    args = command(arm, user, work, pins,
                   ['/opt/codex/bin/codex', '--strict-config', '-C', '/work',
                    '-m', 'gpt-5.5', '-c', 'model_reasoning_effort="medium"', prompt])
    print(f'Launching manual arm {arm}; host outputs: {work}', flush=True)
    try:
        row['exit_code'] = subprocess.call(args, env=env)
    finally:
        row['ended_utc'] = now()
        try:
            row['inputs_unchanged_at_exit'] = digest(PIN) == row['pins_sha256'] and verify() == pins
        except (ValueError, OSError, subprocess.SubprocessError):
            row['inputs_unchanged_at_exit'] = False
        receipt.write_text(json.dumps(row, indent=2) + '\n')
        # Remove only the throwaway credential copy made by this launcher.
        (user / '.codex/auth.json').unlink(missing_ok=True)
    print(f'Session data preserved: {user / ".codex"}; global skill links were not changed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['seal', 'check', 'preflight', 'a', 'b'])
    parser.add_argument('arm', nargs='?', choices=['a', 'b', 'all'], default='all')
    args = parser.parse_args()
    if args.action == 'seal':
        seal()
    else:
        pins = verify()
        if args.action == 'check':
            print(f'CHECK PASS: {pins["codex_version"]}; frozen snapshots and runtime pins match')
        elif args.action == 'preflight':
            for arm in ('ab' if args.arm == 'all' else args.arm):
                preflight(arm, pins)
        else:
            with (CONTROL / '.launch.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                launch(args.action, pins)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f'ISOLATION_REFUSED: {error}', file=sys.stderr)
        raise SystemExit(2)
