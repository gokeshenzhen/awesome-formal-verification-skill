"""Treatment/checkpoint boundaries; no model calls or EDA licenses."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import experiment_policy as policy
import prepare_pilot
import recovery_checkpoint as checkpoint


class Treatment(unittest.TestCase):
    def test_only_intended_leaf_may_differ(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = [Path(directory) / name for name in ('a', 'b')]
            leaf = next(iter(policy.SKILL_DELTA))
            for root in (left, right):
                (root / leaf).parent.mkdir(parents=True)
                (root / leaf).write_text('common')
            self.assertEqual(policy.validate_snapshots(policy.PILOT, left, right), [])
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.RECOVERY, left, right)
            (right / leaf).write_text('readback refinement')
            self.assertEqual(policy.validate_snapshots(policy.RECOVERY, left, right), [leaf])
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.PILOT, left, right)
            (right / 'routing.md').write_text('changed routing')
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.RECOVERY, left, right)

    def test_kind_and_destination_are_explicit(self):
        with self.assertRaises(ValueError):
            prepare_pilot.check_destination(prepare_pilot.REPO / 'test/epoch_return_pilot_new', policy.RECOVERY)
        with self.assertRaises(ValueError):
            prepare_pilot.check_destination(prepare_pilot.REPO / 'test/epoch_return_recovery_ab_new', 'unknown')


class RawCheckpoint(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source'
        self.dest = Path(self.temp.name) / 'frozen'
        for name, relative in checkpoint.FILES.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith('.json'):
                row = dict(phase='baseline' if name.startswith('baseline') else 'run',
                           valid_baseline=True, license_checkout=True)
                path.write_text(json.dumps(row))
            else:
                path.write_text('raw artifact ' + name)
        (self.source / checkpoint.FILES['candidate.stdout.log']).write_text(
            'undetermined undetermined processed 26 infinite 0 H 1.0 {}\n')
        (self.source / checkpoint.FILES['diagnostic.stdout.log']).write_text(
            'SST_PROPERTY name=h status=undetermined trace_id=3\n'
            'SST_TRACE length 2 engine QT time 0.0 job 0.QT tag SST\n')

    def test_allowlist_preserves_bytes_and_excludes_solutions(self):
        (self.source / 'FINAL_REPORT.md').write_text('must stay hidden')
        (self.source / 'helper_sst_values.txt').write_text('must stay hidden')
        (self.source / 'final_repro.tcl').write_text('must stay hidden')
        provenance = checkpoint.copy_checkpoint(self.source, self.dest)
        self.assertEqual({p.name for p in self.dest.iterdir()}, set(checkpoint.FILES) | {'MANIFEST.json'})
        manifest = json.loads((self.dest / 'MANIFEST.json').read_text())
        for name, relative in checkpoint.FILES.items():
            self.assertEqual((self.dest / name).read_bytes(), (self.source / relative).read_bytes())
            self.assertEqual(manifest['files'][name], hashlib.sha256((self.dest / name).read_bytes()).hexdigest())
            self.assertEqual(provenance[name]['source'], str(self.source / relative))
        self.assertNotIn(str(self.source), (self.dest / 'MANIFEST.json').read_text())

    def test_sst_tag_required(self):
        (self.source / checkpoint.FILES['diagnostic.stdout.log']).write_text('SST filename only')
        with self.assertRaises(ValueError):
            checkpoint.copy_checkpoint(self.source, self.dest)
        self.assertFalse(self.dest.exists())

    def test_symlink_cannot_import_hidden_file(self):
        path = self.source / checkpoint.FILES['candidate.tcl']
        path.unlink()
        path.symlink_to(self.source / checkpoint.FILES['diagnostic.tcl'])
        with self.assertRaises(ValueError):
            checkpoint.copy_checkpoint(self.source, self.dest)


if __name__ == '__main__':
    unittest.main()
