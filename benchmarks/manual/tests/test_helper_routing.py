"""Exact treatment boundary for candidate-failure routing; no model calls."""
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import experiment_policy as policy
from prepare_pilot import export_skill


class RoutingTreatment(unittest.TestCase):
    def test_exact_delta_keeps_older_experiments_narrow(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = [Path(directory) / name for name in ('a', 'b')]
            for root in (left, right):
                for name in policy.ROUTING_DELTA:
                    (root / name).parent.mkdir(parents=True, exist_ok=True)
                    (root / name).write_text('same')
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.HELPER_ROUTING, left, right)
            for name in policy.ROUTING_DELTA:
                (right / name).write_text('scoped candidate CEX route')
            self.assertEqual(policy.validate_snapshots(policy.HELPER_ROUTING, left, right),
                             sorted(policy.ROUTING_DELTA))
            for kind in policy.PREFIXES:
                if kind != policy.HELPER_ROUTING:
                    with self.assertRaises(ValueError):
                        policy.validate_snapshots(kind, left, right)
            (right / 'answer.md').write_text('not a permitted change')
            with self.assertRaises(ValueError):
                policy.validate_snapshots(policy.HELPER_ROUTING, left, right)

    def test_selected_versions_change_only_routing(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = [Path(directory) / name for name in ('a', 'b')]
            export_skill('5ca5acb', left)
            export_skill('39fb63f', right)
            self.assertEqual(policy.validate_snapshots(policy.HELPER_ROUTING, left, right),
                             sorted(policy.ROUTING_DELTA))


if __name__ == '__main__':
    unittest.main()
