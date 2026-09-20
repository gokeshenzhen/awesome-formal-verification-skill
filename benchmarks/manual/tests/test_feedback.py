"""Feedback cannot leak through shared mounts or an extra attachment."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import feedback_packet as packet
import experiment_policy as policy


class Feedback(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'checkpoint').mkdir()
        self.data = dict(wave_sha256=hashlib.sha256(b'wave').hexdigest(),
                         timescale='1 ns', times_ps=[0],
                         signals=[dict(path='dut.q', width=1, values_bin=['0'])])
        (self.root / 'readback_packet.json').write_text(json.dumps(self.data))
        self.index = '# Shared checkpoint\n'
        for arm in 'ab':
            path = self.root / f'input_{arm}'
            path.mkdir()
            (path / 'MATERIALS.md').write_text(self.index if arm == 'a' else
                                              packet.feedback_materials(self.index, self.data))
        for name in packet.DIAGNOSTIC_NAMES:
            (self.root / 'input_b' / name).write_text('wave' if name.endswith('.vcd') else 'raw')
        self.spec = dict(conditions=dict(a='checkpoint_only', b='checkpoint_plus_sst'),
                         launch_order=['b', 'a'], new_proof_processes_allowed=False,
                         diagnostic_files={name: policy.manifest(self.root / 'input_b')[name]
                                           for name in packet.DIAGNOSTIC_NAMES})

    def test_exact_optional_feedback(self):
        packet.validate_presentations(self.root, self.index, self.spec)
        self.assertNotIn('dut.q', (self.root / 'input_a/MATERIALS.md').read_text())

    def test_shared_diagnostic_rejected(self):
        (self.root / 'checkpoint/diagnostic.vcd').write_text('wave')
        with self.assertRaisesRegex(ValueError, 'leak'):
            packet.validate_presentations(self.root, self.index, self.spec)

    def test_control_extra_files_rejected(self):
        (self.root / 'input_a/answer.md').write_text('hint')
        with self.assertRaises(ValueError):
            packet.validate_presentations(self.root, self.index, self.spec)

    def test_raw_feedback_drift_rejected(self):
        (self.root / 'input_b/diagnostic.tcl').write_text('changed')
        with self.assertRaises(ValueError):
            packet.validate_presentations(self.root, self.index, self.spec)

    def test_skills_must_be_identical(self):
        left, right = self.root / 'skill_a', self.root / 'skill_b'
        left.mkdir()
        right.mkdir()
        self.assertEqual(policy.validate_snapshots(policy.FEEDBACK, left, right), [])
        (right / 'extra.md').write_text('guidance')
        with self.assertRaises(ValueError):
            policy.validate_snapshots(policy.FEEDBACK, left, right)


if __name__ == '__main__':
    unittest.main()
