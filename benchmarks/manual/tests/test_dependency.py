"""Dependency-reuse comparison boundaries; no model calls or EDA licenses."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import dependency_checkpoint as checkpoint
import experiment_policy as policy
import prepare_pilot


class Treatment(unittest.TestCase):
    def test_exact_three_file_delta_without_relaxing_older_comparisons(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = [Path(directory) / name for name in ('a', 'b')]
            for root in (left, right):
                for name in policy.DEPENDENCY_DELTA:
                    (root / name).parent.mkdir(parents=True, exist_ok=True)
                    (root / name).write_text('common')
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.DEPENDENCY_REUSE, left, right)
            for name in policy.DEPENDENCY_DELTA:
                (right / name).write_text('new selection semantics')
            self.assertEqual(policy.validate_snapshots(policy.DEPENDENCY_REUSE, left, right),
                             sorted(policy.DEPENDENCY_DELTA))
            for old_kind in (policy.RECOVERY, policy.END_TO_END, policy.PILOT, policy.READBACK):
                with self.assertRaises(ValueError):
                    policy.validate_snapshots(old_kind, left, right)
            (right / 'answer.md').write_text('must not enter snapshot')
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.DEPENDENCY_REUSE, left, right)

    def test_selected_commits_match_declared_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = [Path(directory) / name for name in ('a', 'b')]
            prepare_pilot.export_skill('72cbbe0', left)
            prepare_pilot.export_skill('757e0ba', right)
            self.assertEqual(policy.validate_snapshots(policy.DEPENDENCY_REUSE, left, right),
                             sorted(policy.DEPENDENCY_DELTA))


class RawReplay(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = self.root / 'proposed.tcl'
        self.log = self.root / 'session.log'
        self.dest = self.root / 'frozen'
        self.script.write_text('unchanged proposed script\n')
        self.log.write_text(
            'INFO: successfully checked out licenses "jasper_interactive" and "jasper_fpv".\n'
            'HELPER_INFO_BEGIN h_a\nproven proven processed infinite infinite 0 H 0.01 {}\n'
            'HELPER_INFO_END h_a\n'
            'HELPER_INFO_BEGIN h_b\nundetermined undetermined processed 7 infinite 0 H 5.0 {}\n'
            'HELPER_INFO_END h_b\n'
            f'ERROR: problem encountered at line 42 in file {self.script}\n')

    def test_exact_raw_files_only_and_no_fabricated_receipt(self):
        (self.root / 'FINAL_REPORT.md').write_text('hidden interpretation')
        (self.root / 'fixed.tcl').write_text('hidden solution')
        provenance = checkpoint.copy_checkpoint(self.script, self.log, self.dest)
        self.assertEqual({p.name for p in self.dest.iterdir()},
                         {'candidate.tcl', 'candidate.log', 'MANIFEST.json'})
        manifest = json.loads((self.dest / 'MANIFEST.json').read_text())
        for name, original in [('candidate.tcl', self.script), ('candidate.log', self.log)]:
            self.assertEqual((self.dest / name).read_bytes(), original.read_bytes())
            self.assertEqual(provenance[name]['source'], str(original))
            self.assertEqual(manifest['files'][name], hashlib.sha256(original.read_bytes()).hexdigest())
        self.assertNotIn(str(self.root), (self.dest / 'MANIFEST.json').read_text())
        self.assertIn('none is synthesized', manifest['note'])

    def test_wrong_script_reference_is_refused_before_copy(self):
        self.log.write_text(self.log.read_text().replace(str(self.script), '/different.tcl'))
        with self.assertRaisesRegex(ValueError, 'original script'):
            checkpoint.copy_checkpoint(self.script, self.log, self.dest)
        self.assertFalse(self.dest.exists())

    def test_later_target_attempt_is_not_imported(self):
        self.log.write_text(self.log.read_text() + 'TARGET_PROVE_BEGIN top.P0\n')
        with self.assertRaisesRegex(ValueError, 'later original-target'):
            checkpoint.copy_checkpoint(self.script, self.log, self.dest)
        self.assertFalse(self.dest.exists())

    def test_missing_raw_status_is_refused(self):
        self.log.write_text(self.log.read_text().replace('undetermined undetermined', 'proven proven'))
        with self.assertRaisesRegex(ValueError, 'inconclusive'):
            checkpoint.inspect_sources(self.script, self.log)

    def test_symlink_is_refused(self):
        linked = self.root / 'linked.tcl'
        linked.symlink_to(self.script)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            checkpoint.inspect_sources(linked, self.log)


class IsolationCommand(unittest.TestCase):
    def test_checkpoint_and_one_snapshot_mounted_with_proof_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / 'control'
            control.mkdir()
            (control / 'source.json').write_text(json.dumps(
                dict(kind=policy.DEPENDENCY_REUSE, case='/opt/case')))
            script = control / 'isolate.py'
            script.write_bytes((BASE / 'isolate.py').read_bytes())
            spec = importlib.util.spec_from_file_location('dependency_isolation_test', script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            pins = dict(codex_binary='/vendor/codex/bin/codex', node='/vendor/node/bin/node')
            for arm, other in [('a', 'b'), ('b', 'a')]:
                command = module.command(arm, root / 'user', root / 'work', pins, ['true'])
                self.assertIn(str(control / f'frozen/snapshot_{arm}'), command)
                self.assertNotIn(str(control / f'frozen/snapshot_{other}'), command)
                self.assertIn('/opt/experiment/checkpoint', command)
                self.assertIn(str(module.JG_ROOT), command)
                self.assertIn('/opt/experiment/runtime/jg_run.py', command)
                self.assertNotIn('/opt/experiment/runtime/proof_disabled.py', command)
                self.assertNotIn(str(control / 'SCORING.md'), command)


if __name__ == '__main__':
    unittest.main()
