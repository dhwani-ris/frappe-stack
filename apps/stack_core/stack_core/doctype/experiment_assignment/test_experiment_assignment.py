from frappe.tests.utils import FrappeTestCase

from stack_core.doctype.experiment_assignment.experiment_assignment import ExperimentAssignment


class TestExperimentAssignment(FrappeTestCase):
    def test_assignment_is_deterministic(self):
        for _ in range(10):
            arm = ExperimentAssignment.assign_arm("exp_001", "DOC-0001", {"arm_a": 50, "arm_b": 50})
            self.assertEqual(arm, "arm_a")

    def test_different_docs_get_different_arms_at_50_50(self):
        seen_a, seen_b = 0, 0
        for i in range(200):
            arm = ExperimentAssignment.assign_arm("exp_001", f"DOC-{i:04d}", {"arm_a": 50, "arm_b": 50})
            if arm == "arm_a":
                seen_a += 1
            else:
                seen_b += 1
        self.assertGreater(seen_a, 60)
        self.assertGreater(seen_b, 60)
        self.assertEqual(seen_a + seen_b, 200)

    def test_split_must_sum_to_100(self):
        with self.assertRaises(ValueError):
            ExperimentAssignment.assign_arm("exp", "DOC", {"arm_a": 30, "arm_b": 30})
        with self.assertRaises(ValueError):
            ExperimentAssignment.assign_arm("exp", "DOC", {"arm_a": 60, "arm_b": 60})

    def test_100_0_always_arm_a(self):
        for i in range(50):
            arm = ExperimentAssignment.assign_arm("exp_x", f"DOC-{i}", {"arm_a": 100, "arm_b": 0})
            self.assertEqual(arm, "arm_a")

    def test_different_experiments_can_yield_different_arms_for_same_doc(self):
        results = set()
        for i in range(20):
            results.add(
                ExperimentAssignment.assign_arm(f"exp_{i}", "DOC-SAME", {"arm_a": 50, "arm_b": 50})
            )
        self.assertEqual(results, {"arm_a", "arm_b"})
