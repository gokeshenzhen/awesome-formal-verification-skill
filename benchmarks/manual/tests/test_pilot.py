"""Pilot packaging integrity; no model calls or EDA licenses."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import prepare_pilot


class PilotInputs(unittest.TestCase):
    def test_public_manifest_matches_files(self):
        lines = (prepare_pilot.CASE / 'CHECKSUMS.sha256').read_text().splitlines()
        covered = set()
        for line in lines:
            expected, name = line.split(None, 1)
            covered.add(name)
            self.assertEqual(hashlib.sha256((prepare_pilot.CASE / name).read_bytes()).hexdigest(), expected)
        self.assertEqual(covered | {'CHECKSUMS.sha256'}, set(prepare_pilot.PUBLIC_FILES))

    def test_destination_refuses_existing_or_broad_paths(self):
        for path in (prepare_pilot.REPO, prepare_pilot.REPO / 'test', prepare_pilot.CASE,
                     prepare_pilot.REPO / 'test/../epoch_return_pilot_outside'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                prepare_pilot.check_destination(path)
        with tempfile.TemporaryDirectory(prefix='epoch_return_pilot_test_', dir=prepare_pilot.REPO / 'test') as path:
            with self.assertRaises(ValueError):
                prepare_pilot.check_destination(Path(path))

    def test_skill_export_contains_only_permitted_trees(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'snapshot'
            prepare_pilot.export_skill('82a7408', dest)
            self.assertEqual({p.name for p in dest.iterdir()}, {'adapters', 'knowledge', 'tool-specific'})
            entry = dest / 'adapters/claude-code'
            self.assertEqual((entry / 'knowledge').resolve(), dest / 'knowledge')
            self.assertEqual((entry / 'tool-specific').resolve(), dest / 'tool-specific')
            self.assertFalse((dest / '.git').exists())


if __name__ == '__main__':
    unittest.main()
