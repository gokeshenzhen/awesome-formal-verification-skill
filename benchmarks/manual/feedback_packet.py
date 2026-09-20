"""Feedback presence treatment: unchanged checkpoint, optional raw SST + all values."""
import json
from experiment_policy import manifest
from readback_packet import render_packet

DIAGNOSTIC_NAMES = {'diagnostic.tcl', 'diagnostic.stdout.log', 'diagnostic.run.json', 'diagnostic.vcd'}


def feedback_materials(index, packet):
    return (index + '\n## Additional diagnostic artifacts\n\n' +
            '\n'.join(f'- /opt/experiment/input/{name}' for name in sorted(DIAGNOSTIC_NAMES)) +
            '\n\nThe raw log identifies this as an SST diagnostic, not a reset-reachable CEX.\n\n' +
            render_packet(packet).replace('/opt/experiment/checkpoint/diagnostic.vcd',
                                          '/opt/experiment/input/diagnostic.vcd'))


def validate_presentations(frozen, index, spec):
    if (set(spec['conditions']) != {'a', 'b'} or
            set(spec['conditions'].values()) != {'checkpoint_only', 'checkpoint_plus_sst'} or
            spec['launch_order'] not in (['a', 'b'], ['b', 'a']) or
            spec['new_proof_processes_allowed'] is not False):
        raise ValueError('Feedback comparison needs two declared opposite conditions and no new proof')
    packet = json.loads((frozen / 'readback_packet.json').read_text())
    if any(name.startswith('diagnostic') for name in manifest(frozen / 'checkpoint')):
        raise ValueError('Do not leak diagnostics through the shared checkpoint')
    for arm, condition in spec['conditions'].items():
        path = frozen / f'input_{arm}'
        expected = {'MATERIALS.md'}
        text = index
        if condition == 'checkpoint_plus_sst':
            expected |= DIAGNOSTIC_NAMES
            text = feedback_materials(index, packet)
            if manifest(path)['diagnostic.vcd'] != packet['wave_sha256']:
                raise ValueError('Readback table belongs to a different diagnostic VCD')
            if {name: manifest(path)[name] for name in DIAGNOSTIC_NAMES} != spec['diagnostic_files']:
                raise ValueError('Raw diagnostic differs from declared source hashes')
        if set(manifest(path)) != expected or (path / 'MATERIALS.md').read_text() != text:
            raise ValueError('Unexpected or modified feedback attachment')
