"""Non-interactive opt-in and process supervision, without a model/API call."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))


class Headless(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        control = self.root / 'control'
        control.mkdir()
        (control / 'source.json').write_text(json.dumps(dict(case='/opt/case')))
        script = control / 'isolate.py'
        script.write_bytes((BASE / 'isolate.py').read_bytes())
        spec = importlib.util.spec_from_file_location('headless_test', script)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_default_stays_interactive(self):
        policy = self.module.execution_policy()
        self.assertEqual(policy, {'mode': 'manual'})
        self.assertNotIn('exec', self.module.model_command(policy))

    def test_explicit_bounded_authorization_required(self):
        for value in [{}, {'mode': 'headless'},
                      dict(mode='headless', authorization='user request', wall_seconds=True),
                      dict(mode='headless', authorization='', wall_seconds=900),
                      dict(mode='headless', authorization='request', wall_seconds=3601)]:
            self.module.SOURCE['execution'] = value
            with self.assertRaises(ValueError):
                self.module.execution_policy()
        self.module.SOURCE['execution'] = dict(mode='headless', authorization='user request', wall_seconds=900)
        args = self.module.model_command(self.module.execution_policy())
        self.assertIn('exec', args)
        self.assertIn('--skip-git-repo-check', args)
        self.assertIn('--json', args)
        self.assertIn('gpt-5.5', args)
        self.assertNotIn('--ephemeral', args)
        self.assertNotIn('resume', args)

    def run_stub(self, code, limit=5):
        return self.module.run_headless([sys.executable, '-c', code], dict(os.environ), self.root, limit)

    def test_success_keeps_events_usage_and_session(self):
        events = [dict(type='thread.started', thread_id='new-independent-session'),
                  dict(type='turn.completed', usage={'input_tokens': 12, 'output_tokens': 3})]
        row = self.run_stub(f'import json; [print(json.dumps(e)) for e in {events!r}]')
        self.assertTrue(row['model_run_completed'])
        self.assertEqual(row['session_ids'], ['new-independent-session'])
        self.assertEqual(row['usage'][0]['output_tokens'], 3)
        self.assertTrue((self.root / 'stderr.log').exists())
        with self.assertRaises(FileExistsError):
            self.run_stub('pass')

    def test_zero_exit_without_completed_turn_is_not_success(self):
        row = self.run_stub('print("not a JSON event")')
        self.assertFalse(row['model_run_completed'])
        self.assertTrue(row['malformed_events'])

    def test_model_failure_not_success(self):
        row = self.run_stub('print(\'{"type":"turn.failed","error":"quota"}\')')
        self.assertFalse(row['model_run_completed'])
        self.assertEqual(row['completed_turns'], 0)

    def test_timeout_kills_only_launched_group_and_preserves_partial_output(self):
        row = self.run_stub('import time; print(\'{"type":"turn.started"}\', flush=True); time.sleep(10)', .1)
        self.assertTrue(row['timed_out'])
        self.assertFalse(row['model_run_completed'])
        self.assertLess(row['wall_seconds'], 3)
        self.assertIn('turn.started', (self.root / 'events.jsonl').read_text())


if __name__ == '__main__':
    unittest.main()
