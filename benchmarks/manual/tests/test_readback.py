"""Input-presentation treatment boundaries; no models, EDA or live MCP."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / 'runtime'))
import experiment_policy as policy
import input_read
import readback_packet as packet
import recovery_checkpoint as checkpoint


class Parser:
    """Public API stub; the real parser is cross-checked by stdio preflight."""
    def __init__(self):
        self.rows = [dict(path='dut.z', width=2, var_type='reg'),
                     dict(path='dut.a', width=1, var_type='wire')]
        self.truncated = False

    def get_summary(self):
        return dict(scale_unit='1 ns', scale_fs_per_tick=1000000, simulation_duration_ps=10000)

    def search_signals(self, keyword, max_results):
        assert keyword == '' and max_results >= len(self.rows)
        return dict(results=self.rows, total_matched=len(self.rows), truncated=self.truncated)

    def get_value_at_time(self, path, at):
        values = {'dut.z': {0: 'bxz', 5000: 'b01', 10000: 'b01'},
                  'dut.a': {0: '1', 5000: '0', 10000: '0'}}
        return dict(value=dict(bin=values[path][at]))


class Readback(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wave = self.root / 'diagnostic.vcd'
        self.wave.write_text('$timescale 1 ns $end\n$scope module dut $end\n'
            '$var reg 2 z z $end\n$var wire 1 a a $end\n$upscope $end\n'
            '$enddefinitions $end\n#0\nbxz z\n1a\n#5\nb01 z\n0a\n#10\n')

    def test_all_timestamps_and_lexicographic_rows(self):
        data = packet.build_packet(self.wave, Parser())
        self.assertEqual(data['times_ps'], [0, 5000, 10000])
        self.assertEqual([row['path'] for row in data['signals']], ['dut.a', 'dut.z'])
        self.assertEqual(data['signals'][1]['values_bin'], ['xz', '01', '01'])
        rendered = packet.render_packet(data)
        self.assertIn('| dut.z | 2 | bxz | b01 | b01 |', rendered)
        self.assertIn('10000 ps', rendered)
        self.assertNotIn(str(self.root), rendered)

    def test_partial_search_and_ambiguous_declarations_refused(self):
        parser = Parser()
        parser.truncated = True
        with self.assertRaisesRegex(ValueError, 'complete'):
            packet.build_packet(self.wave, parser)
        self.wave.write_text(self.wave.read_text().replace('$var wire 1 a', '$var wire 1 z'))
        with self.assertRaisesRegex(ValueError, 'declaration'):
            packet.build_packet(self.wave, Parser())

    def test_initial_state_and_monotone_times_required(self):
        original = self.wave.read_text()
        for text in [original.replace('#0', '#1'), original + '#5\n']:
            self.wave.write_text(text)
            with self.assertRaisesRegex(ValueError, 'initial timestamp'):
                packet.build_packet(self.wave, Parser())

    def test_signal_selection_cannot_hide_an_exported_value(self):
        parser = Parser()
        parser.rows.pop()
        with self.assertRaisesRegex(ValueError, 'declaration'):
            packet.build_packet(self.wave, parser)

    def test_identical_skills_required(self):
        left, right = self.root / 'a', self.root / 'b'
        for path in (left, right):
            path.mkdir()
            (path / 'SKILL.md').write_text('same')
        self.assertEqual(policy.validate_snapshots(policy.READBACK, left, right), [])
        (right / 'SKILL.md').write_text('extra instruction')
        with self.assertRaises(ValueError):
            policy.validate_snapshots(policy.READBACK, left, right)

    def test_attachment_delta_is_exactly_mechanical_table(self):
        data = packet.build_packet(self.wave, Parser())
        (self.root / 'readback_packet.json').write_text(json.dumps(data))
        spec = dict(pair_count=1, launch_order=['a', 'b'], conditions=dict(a='raw', b='raw_plus_readback'),
                    new_proof_processes_allowed=False, times_ps=data['times_ps'],
                    signal_count=2, wave_sha256=data['wave_sha256'])
        index = '# Common raw materials\n'
        for arm in 'ab':
            directory = self.root / f'input_{arm}'
            directory.mkdir()
            (directory / 'MATERIALS.md').write_text(index + ('\n' + packet.render_packet(data) if arm == 'b' else ''))
        packet.validate_presentations(self.root, index, spec)
        (self.root / 'input_a/answer.md').write_text('hidden hint')
        with self.assertRaises(ValueError):
            packet.validate_presentations(self.root, index, spec)

    def test_frozen_runtime_origin_does_not_read_dirty_live_tree(self):
        runtime = self.root / 'control/frozen/traceweave'
        runtime.mkdir(parents=True)
        (runtime / 'server.py').write_text('frozen')
        hashes = {'traceweave/server.py': hashlib.sha256(b'frozen').hexdigest()}
        (self.root / 'control/pins.json').write_text(json.dumps(dict(frozen=hashes, traceweave_commit='original')))
        source, provenance = packet.inspect_runtime_origin(self.root)
        self.assertEqual(source, runtime)
        self.assertEqual(provenance['traceweave_commit'], 'original')
        (runtime / 'server.py').write_text('changed')
        with self.assertRaises(ValueError):
            packet.inspect_runtime_origin(self.root)

    def test_read_pages_deliver_exact_text_with_receipt(self):
        file = self.root / 'MATERIALS.md'
        file.write_text('one\ntwo\nthree\n')
        row, output = input_read.page(file, 1, 2)
        self.assertEqual((row['start'], row['end'], row['total_lines']), (1, 2, 3))
        self.assertIn('NEXT: input-read --start 3 --count 2', output)
        self.assertNotIn('0003:', output)
        row, output = input_read.page(file, 3, 2)
        self.assertTrue(output.endswith('EOF'))


class ReadbackCheckpoint(unittest.TestCase):
    def test_natural_trial_allowlist_excludes_later_work(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            dest = Path(directory) / 'copy'
            for name, relative in packet.CHECKPOINT_FILES.items():
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if name.endswith('.json'):
                    path.write_text(json.dumps(dict(phase='baseline' if name.startswith('baseline') else 'run',
                        valid_baseline=True, license_checkout=True)))
                elif name == 'candidate.stdout.log':
                    path.write_text('undetermined undetermined processed 35 infinite 0 H 1.0 {}\n')
                elif name == 'diagnostic.stdout.log':
                    path.write_text('SST_PROPERTY status=undetermined trace_id=2\n'
                                   'SST_TRACE length 2 engine QT time 0.1 job 0.QT tag SST\n')
                else:
                    path.write_text('raw ' + name)
            (source / 'FINAL_REPORT.md').write_text('do not copy')
            (source / 'final_repro.tcl').write_text('do not copy')
            checkpoint.copy_checkpoint(source, dest, packet.CHECKPOINT_FILES)
            self.assertEqual({p.name for p in dest.iterdir()}, set(packet.CHECKPOINT_FILES) | {'MANIFEST.json'})
            for name, relative in packet.CHECKPOINT_FILES.items():
                self.assertEqual((dest / name).read_bytes(), (source / relative).read_bytes())


class IsolationCommand(unittest.TestCase):
    def test_readback_mounts_only_selected_attachment_and_no_vendor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / 'control'
            control.mkdir()
            (control / 'source.json').write_text(json.dumps(dict(kind=policy.READBACK, case='/opt/case')))
            script = control / 'isolate.py'
            script.write_bytes((BASE / 'isolate.py').read_bytes())
            spec = importlib.util.spec_from_file_location('readback_isolation_test', script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            pins = dict(codex_binary='/vendor/codex/bin/codex', node='/vendor/node/bin/node')
            command = module.command('a', root / 'user', root / 'work', pins, ['true'])
            self.assertIn(str(control / 'frozen/input_a'), command)
            self.assertNotIn(str(control / 'frozen/input_b'), command)
            self.assertNotIn('/opt/readback-check.json', command)
            self.assertNotIn(str(module.JG_ROOT), command)
            self.assertNotIn(str(module.VERDI), command)
            self.assertIn('/opt/experiment/runtime/proof_disabled.py', command)
            self.assertIn('/opt/experiment/checkpoint', command)
            preflight = module.command('b', root / 'user', root / 'work', pins, ['true'], probes=True)
            self.assertIn('/opt/readback-check.json', preflight)
            with mock.patch.dict('os.environ', {'HOME': '/home/robin'}, clear=True):
                self.assertNotIn('CDS_LIC_FILE', module.environment())
            module.SOURCE['kind'] = policy.PILOT
            legacy = module.command('a', root / 'user', root / 'work', pins, ['true'])
            self.assertIn(str(module.JG_ROOT), legacy)
            self.assertNotIn('/opt/experiment/input', legacy)


if __name__ == '__main__':
    unittest.main()
