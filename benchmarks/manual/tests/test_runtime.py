"""Fast execution-policy tests, independent of models and Jasper licenses."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

RUNTIME = Path(__file__).resolve().parents[1] / 'runtime'
sys.path.insert(0, str(RUNTIME))
import skill_read
import jg_run


class ReadGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.entry = self.root / 'SKILL.md'
        self.entry.write_text('first\nsecond\nthird\n')
        self.ledger = self.root / 'read.jsonl'

    def tearDown(self):
        self.temp.cleanup()

    def receipt(self, start, end, path=None):
        path = path or self.entry
        row = dict(path=str(path), sha256=skill_read.hashlib.sha256(path.read_bytes()).hexdigest(),
                   total_lines=len(path.read_text().splitlines()), start=start, end=end)
        with self.ledger.open('a') as out:
            out.write(json.dumps(row) + '\n')

    def validate(self):
        skill_read.validate_complete(self.ledger, self.root, self.entry)

    def test_missing(self):
        with self.assertRaises(ValueError):
            self.validate()

    def test_partial_then_complete(self):
        self.receipt(1, 2)
        with self.assertRaises(ValueError):
            self.validate()
        self.receipt(3, 3)
        self.validate()

    def test_other_selected_leaf_also_requires_eof(self):
        self.receipt(1, 3)
        leaf = self.root / 'leaf.md'
        leaf.write_text('one\ntwo\n')
        self.receipt(1, 1, leaf)
        with self.assertRaises(ValueError):
            self.validate()

    def test_hash_drift(self):
        self.receipt(1, 3)
        self.entry.write_text('changed\n')
        with self.assertRaises(ValueError):
            self.validate()


class Budget(unittest.TestCase):
    def test_explicit_environment_is_not_in_receipt_or_parent(self):
        marker = 'JG_REPLAY_ENV_TEST'
        parent_marker = 'JG_REPLAY_PARENT_TEST'
        child_value = 'synthetic-child-only-value'
        child_code = ('import os, sys; '
                      'print("successfully checked out licenses", flush=True); '
                      f'sys.exit(0 if os.environ.get({marker!r}) and '
                      f'{parent_marker!r} not in os.environ else 1)')
        with patch.dict(os.environ, {parent_marker: 'parent-only'}):
            before = dict(os.environ)
            with tempfile.TemporaryDirectory() as directory:
                row = jg_run.execute([sys.executable, '-c', child_code],
                    Path(directory) / 'out', 2.0, env={marker: child_value})
            self.assertEqual(os.environ, before)
            self.assertTrue(jg_run.run_completed(row))
            self.assertEqual(row['exit_code'], 0)
            self.assertNotIn(child_value, json.dumps(row))

    def test_post_analysis_cleanup_preserves_vendor_exit(self):
        lines = ['successfully checked out license "jasper_fpv".',
                 '[<embedded>] % INFO (IPL005): Received request to exit from the console.',
                 'INFO (IPL015): The Tcl-thread exited with status 0.',
                 'INFO (IPL016): Exiting the analysis session with status 0.']
        with tempfile.TemporaryDirectory() as directory:
            row = jg_run.execute([sys.executable, '-c',
                f'import time; print({chr(10).join(lines)!r}, flush=True); time.sleep(5)'],
                Path(directory) / 'out', 2.0, cleanup_grace=0.1)
            self.assertTrue(jg_run.run_completed(row))
            self.assertEqual(row['stopped_reason'], 'post_analysis_exit_cleanup')
            self.assertNotEqual(row['exit_code'], 0)

    def test_proven_text_is_not_a_cleanup_trigger(self):
        self.assertFalse(jg_run.analysis_finished(b'PROPERTY_STATUS proven\n'))

    def test_license_message_forms(self):
        self.assertTrue(jg_run.license_checked_out(b'successfully checked out license "jasper_fpv".'))
        self.assertTrue(jg_run.license_checked_out(b'successfully checked out licenses "jasper_interactive" and "jasper_fpv".'))
        self.assertFalse(jg_run.license_checked_out(b'Waiting for license'))

    def test_baseline_excluded(self):
        self.assertEqual(jg_run.remaining([dict(phase='baseline', wall_seconds=20),
                                           dict(phase='run', wall_seconds=40)]), 140)

    def test_budget_exhausted(self):
        self.assertEqual(jg_run.remaining([dict(phase='run', wall_seconds=181)]), 0)

    def test_watchdog(self):
        with tempfile.TemporaryDirectory() as directory:
            row = jg_run.execute([sys.executable, '-c', 'import time; time.sleep(5)'],
                                 Path(directory) / 'out', 2.0, watchdog=0.1)
            self.assertEqual(row['stopped_reason'], 'license_startup_watchdog')
            self.assertFalse(row['license_checkout'])

    def test_wall_limit_after_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            row = jg_run.execute([sys.executable, '-c',
                'import time; print("successfully checked out licenses", flush=True); time.sleep(5)'],
                Path(directory) / 'out', 0.2)
            self.assertTrue(row['license_checkout'])
            self.assertEqual(row['stopped_reason'], 'wall_budget_exhausted')


class AnalysisExit(unittest.TestCase):
    REQUEST = b'INFO (IPL005): Received request to exit from the console.'
    TCL_OK = b'INFO (IPL015): The Tcl-thread exited with status 0.'
    ANALYSIS_OK = b'INFO (IPL016): Exiting the analysis session with status 0.'

    def log(self, prefix=b'', tcl=None, analysis=None):
        return b'\n'.join([prefix + self.REQUEST,
                           self.TCL_OK if tcl is None else tcl,
                           self.ANALYSIS_OK if analysis is None else analysis])

    def test_real_console_prefixes(self):
        for prefix in (b'', b'% ', b'[<embedded>] % ', b'[task_one] % '):
            with self.subTest(prefix=prefix):
                self.assertTrue(jg_run.analysis_finished(self.log(prefix)))

    def test_nonzero_tcl_or_analysis_exit(self):
        for output in (self.log(tcl=self.TCL_OK.replace(b'0.', b'1.')),
                       self.log(analysis=self.ANALYSIS_OK.replace(b'0.', b'1.'))):
            self.assertFalse(jg_run.analysis_finished(output))
            self.assertIsNone(jg_run.analysis_exit_code(output))

    def test_complete_error_exit_is_not_success(self):
        for code in (1, 2, 255):
            output = self.log().replace(b'status 0.', f'status {code}.'.encode())
            self.assertEqual(jg_run.analysis_exit_code(output), code)
            self.assertFalse(jg_run.analysis_finished(output))

    def test_exit_markers_must_be_in_order(self):
        request, tcl, analysis = self.log().splitlines()
        for lines in ((tcl, request, analysis), (request, analysis, tcl),
                      (analysis, request, tcl), (analysis, tcl, request),
                      (tcl, analysis, request)):
            self.assertIsNone(jg_run.analysis_exit_code(b'\n'.join(lines)))

    def test_all_three_markers_required(self):
        lines = self.log().splitlines()
        for index in range(3):
            output = b'\n'.join(lines[:index] + lines[index + 1:])
            self.assertFalse(jg_run.analysis_finished(output))
            self.assertIsNone(jg_run.analysis_exit_code(output))

    def test_echoed_text_does_not_match(self):
        for prefix in (b'puts "', b'# ', b'example: ', b'% puts '):
            for index in range(3):
                lines = self.log().splitlines()
                lines[index] = prefix + lines[index]
                self.assertIsNone(jg_run.analysis_exit_code(b'\n'.join(lines)))

    def test_top_level_help_process_is_cleaned_up(self):
        output = b'successfully checked out license "jasper_fpv".\n' + self.log(b'% ')
        with tempfile.TemporaryDirectory() as directory:
            row = jg_run.execute([sys.executable, '-c',
                f'import time; print({output.decode()!r}, flush=True); time.sleep(5)'],
                Path(directory) / 'out', 2.0, cleanup_grace=0.1)
            self.assertTrue(row['analysis_finished'])
            self.assertEqual(row['analysis_exit_code'], 0)
            self.assertEqual(row['stopped_reason'], 'post_analysis_exit_cleanup')
            self.assertTrue(jg_run.run_completed(row))
            self.assertNotEqual(row['exit_code'], 0)
            self.assertGreater(row['wall_seconds'], 0)

    def test_error_exit_is_cleaned_up_but_stays_failed(self):
        output = b'successfully checked out license "jasper_fpv".\n' + self.log(b'% ').replace(
            b'status 0.', b'status 1.')
        with tempfile.TemporaryDirectory() as directory:
            row = jg_run.execute([sys.executable, '-c',
                f'import time; print({output.decode()!r}, flush=True); time.sleep(5)'],
                Path(directory) / 'out', 2.0, cleanup_grace=0.1)
            self.assertEqual(row['analysis_exit_code'], 1)
            self.assertFalse(row['analysis_finished'])
            self.assertEqual(row['stopped_reason'], 'post_analysis_exit_cleanup')
            self.assertFalse(jg_run.run_completed(row))
            self.assertNotEqual(row['exit_code'], 0)
            self.assertLess(row['wall_seconds'], row['limit_seconds'])
            row['phase'] = 'run'
            self.assertAlmostEqual(jg_run.remaining([row]), jg_run.BUDGET - row['wall_seconds'])

    def test_natural_process_exit_cannot_hide_analysis_error(self):
        output = b'successfully checked out license "jasper_fpv".\n' + self.log().replace(
            b'status 0.', b'status 1.')
        for outer_code in (0, 1):
            with self.subTest(outer_code=outer_code), tempfile.TemporaryDirectory() as directory:
                row = jg_run.execute([sys.executable, '-c',
                    f'import sys; print({output.decode()!r}, flush=True); sys.exit({outer_code})'],
                    Path(directory) / 'out', 2.0)
                self.assertEqual(row['analysis_exit_code'], 1)
                self.assertEqual(row['exit_code'], outer_code)
                self.assertIsNone(row['stopped_reason'])
                self.assertFalse(jg_run.run_completed(row))

    def test_partial_exit_does_not_trigger_cleanup(self):
        output = b'successfully checked out license "jasper_fpv".\n' + self.REQUEST
        with tempfile.TemporaryDirectory() as directory:
            row = jg_run.execute([sys.executable, '-c',
                f'import time; print({output.decode()!r}, flush=True); time.sleep(5)'],
                Path(directory) / 'out', 0.3, cleanup_grace=0.05)
            self.assertFalse(row['analysis_finished'])
            self.assertIsNone(row['analysis_exit_code'])
            self.assertEqual(row['stopped_reason'], 'wall_budget_exhausted')
            self.assertFalse(jg_run.run_completed(row))

    def test_cleanup_cannot_override_missing_license(self):
        self.assertFalse(jg_run.run_completed(dict(license_checkout=False,
            exit_code=-15, analysis_exit_code=0, analysis_finished=True,
            stopped_reason='post_analysis_exit_cleanup')))


class CaseConfig(unittest.TestCase):
    def check(self, config):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'case.json'
            path.write_text(json.dumps(config))
            return jg_run.load_case_config(path)

    def test_case_identity_is_configured(self):
        self.assertEqual(self.check(dict(case_path='/opt/case', target='dut.P0')),
                         (Path('/opt/case'), 'dut.P0'))

    def test_bad_identity(self):
        for path, target in [('relative', 'dut.P0'), ('/opt/case', ''),
                             ('/opt/case', 7), ('/opt/case', 'P0\nP1')]:
            with self.subTest(path=path, target=target), self.assertRaises(ValueError):
                self.check(dict(case_path=path, target=target))


if __name__ == '__main__':
    unittest.main()
