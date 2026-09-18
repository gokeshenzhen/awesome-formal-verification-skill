"""Mechanical, all-signal short-VCD presentation; no diagnosis or model call."""
import hashlib
import json
from pathlib import Path
import re
import sys

from experiment_policy import manifest

# This allowlist identifies the preregistered, naturally inconclusive trial.
# Later revisions, reports, decoded interpretations and sessions are excluded.
CHECKPOINT_FILES = {
    'baseline.stdout.log': 'runs/baseline.stdout.log',
    'baseline.run.json': 'runs/baseline.run.json',
    'candidate.tcl': 'helper_conservation.tcl',
    'candidate.stdout.log': 'runs/helper_conservation.stdout.log',
    'candidate.run.json': 'runs/helper_conservation.run.json',
    'diagnostic.tcl': 'sst_helper_conservation.tcl',
    'diagnostic.stdout.log': 'runs/sst_helper_conservation.stdout.log',
    'diagnostic.run.json': 'runs/sst_helper_conservation.run.json',
    'diagnostic.vcd': 'helper_conservation_sst.vcd',
}
MAX_SIGNALS = 1024
MAX_TIMESTAMPS = 32
MAX_VCD_BYTES = 1024 * 1024


def inspect_runtime_origin(experiment):
    """Reuse a sealed runtime, not a concurrently edited live TraceWeave tree."""
    experiment = Path(experiment).resolve(strict=True)
    pin_file = experiment / 'control/pins.json'
    pins = json.loads(pin_file.read_text())
    source = experiment / 'control/frozen/traceweave'
    expected = {name.removeprefix('traceweave/'): value
                for name, value in pins['frozen'].items() if name.startswith('traceweave/')}
    if not expected or manifest(source) != expected:
        raise ValueError('Historical TraceWeave snapshot differs from its seal')
    if any(not isinstance(value, str) for value in expected.values()):
        raise ValueError('Runtime source must contain regular files, not symlinks')
    return source, dict(experiment=str(experiment), pins_sha256=hashlib.sha256(pin_file.read_bytes()).hexdigest(),
                        traceweave_commit=pins['traceweave_commit'], files=expected)


def build_packet(wave, parser):
    """Use frozen TraceWeave's public parser API; never select relevant signals."""
    wave = Path(wave)
    raw = wave.read_bytes()
    if len(raw) > MAX_VCD_BYTES:
        raise ValueError('Readback probe accepts only a short VCD; do not silently truncate')
    text = raw.decode('utf-8', errors='strict')
    summary = parser.get_summary()
    # Preserve every recorded timestamp, including the initial dump and a
    # final timestamp without changes. Do not pick clock edges or helper edges.
    header, body = text.split('$enddefinitions $end', 1)
    if '$timescale' not in header or '(assumed)' in summary['scale_unit']:
        raise ValueError('An explicit VCD timescale is required')
    scale = summary['scale_fs_per_tick']
    if not isinstance(scale, int) or scale < 1000 or scale % 1000:
        raise ValueError('This exact-ps presentation does not support sub-ps timescales')
    ticks = [int(value) for value in re.findall(r'^\s*#(\d+)\s*$', body, re.M)]
    if not ticks or ticks[0] != 0 or ticks != sorted(set(ticks)) or len(ticks) > MAX_TIMESTAMPS:
        raise ValueError('Require an explicit initial timestamp and a short monotone trace')
    times = [value * (scale // 1000) for value in ticks]
    found = parser.search_signals('', max_results=MAX_SIGNALS)
    signals = sorted(found['results'], key=lambda item: item['path'])
    if not signals or found.get('truncated') or found['total_matched'] != len(signals):
        raise ValueError('Signal enumeration must be complete')
    # Reject aliased/multipart declarations for this small probe rather than
    # claiming complete coverage if a parser's search hides an alias.
    declarations = re.findall(r'\$var\s+\S+\s+\d+\s+(\S+)\s+.*?\$end', header)
    if len(declarations) != len(set(declarations)) or len(declarations) != len(signals):
        raise ValueError('Probe requires one complete search row per VCD declaration')
    if summary['simulation_duration_ps'] != times[-1]:
        raise ValueError('Parser duration differs from recorded timestamps')
    rows = []
    for signal in signals:
        if signal.get('var_type') not in ('wire', 'reg', 'integer', 'parameter'):
            raise ValueError('Only four-state bit-vector signals are supported')
        values = []
        for at in times:
            value = parser.get_value_at_time(signal['path'], at)['value']
            bits = None if value is None else value['bin'].removeprefix('b').removeprefix('B').lower()
            if bits is not None and (not re.fullmatch('[01xz]+', bits) or len(bits) > signal['width']):
                raise ValueError('Unsupported bit-vector value')
            values.append(bits)
        rows.append(dict(path=signal['path'], width=signal['width'], values_bin=values))
    return dict(schema_version=1, wave_sha256=hashlib.sha256(raw).hexdigest(),
                timescale=summary['scale_unit'], times_ps=times, signals=rows,
                sampling='last recorded value at each timestamp; no clock-edge inference',
                coverage='all declarations and all recorded timestamps; not all RTL signals')


def render_packet(packet):
    lines = ['## Mechanical VCD readback', '',
             'Source: /opt/experiment/checkpoint/diagnostic.vcd',
             f"SHA256: {packet['wave_sha256']}",
             f"VCD timescale: {packet['timescale']}", '',
             'Rows are sorted by signal path. All declarations and recorded timestamps are included.',
             'Values are binary as recorded (b prefix); ? means no recorded value, x/z remain unknown.',
             'Each column is the last value at that timestamp, not an inferred SVA sampling event.',
             'No derived sums, selected signals, reachability verdicts or candidate relations are supplied.', '',
             '| Signal | Width | ' + ' | '.join(f'{at} ps' for at in packet['times_ps']) + ' |',
             '|---|---:|' + '---|' * len(packet['times_ps'])]
    for row in packet['signals']:
        values = ['?' if value is None else 'b' + value for value in row['values_bin']]
        lines.append('| ' + row['path'] + f" | {row['width']} | " + ' | '.join(values) + ' |')
    return '\n'.join(lines) + '\n'


def prepare_presentations(frozen, index_text):
    # Import exactly the frozen code that both model sessions will use.
    sys.path.insert(0, str(frozen / 'traceweave'))
    from src.vcd_parser import VCDParser
    wave = frozen / 'checkpoint/diagnostic.vcd'
    packet = build_packet(wave, VCDParser(str(wave)))
    for arm in 'ab':
        directory = frozen / f'input_{arm}'
        directory.mkdir()
        contents = index_text + ('\n' + render_packet(packet) if arm == 'b' else '')
        (directory / 'MATERIALS.md').write_text(contents)
    # Evaluator/preflight data: not mounted into either model session.
    (frozen / 'readback_packet.json').write_text(json.dumps(packet, indent=2) + '\n')
    return dict(pair_count=1, launch_order=['a', 'b'], conditions=dict(a='raw', b='raw_plus_readback'),
                new_proof_processes_allowed=False, times_ps=packet['times_ps'],
                signal_count=len(packet['signals']), wave_sha256=packet['wave_sha256'])


def validate_presentations(frozen, index_text, spec):
    packet = json.loads((frozen / 'readback_packet.json').read_text())
    expected = dict(pair_count=1, launch_order=['a', 'b'], conditions=dict(a='raw', b='raw_plus_readback'),
                    new_proof_processes_allowed=False, times_ps=packet['times_ps'],
                    signal_count=len(packet['signals']), wave_sha256=packet['wave_sha256'])
    if spec != expected:
        raise ValueError('Readback treatment differs from preregistered conditions')
    for arm in 'ab':
        directory = frozen / f'input_{arm}'
        contents = index_text + ('\n' + render_packet(packet) if arm == 'b' else '')
        if set(manifest(directory)) != {'MATERIALS.md'} or (directory / 'MATERIALS.md').read_text() != contents:
            raise ValueError('Unexpected or modified arm presentation')
