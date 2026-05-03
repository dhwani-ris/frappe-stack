import hashlib

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ExperimentAssignment(Document):
    @staticmethod
    def assign_arm(experiment_id: str, doc_name: str, traffic_split: dict[str, int]) -> str:
        """Deterministic A/B assignment.

        Hashes (experiment_id || doc_name) so the same document always maps to the
        same arm even if the assignment is recomputed on workflow re-evaluation.
        Refuses any traffic_split that doesn't sum to exactly 100.
        """
        arm_a = int(traffic_split.get("arm_a", 0))
        arm_b = int(traffic_split.get("arm_b", 0))
        if arm_a + arm_b != 100:
            raise ValueError(f"traffic_split must sum to 100, got {arm_a + arm_b}")

        seed = f"{experiment_id}::{doc_name}".encode()
        bucket = int(hashlib.sha256(seed).hexdigest(), 16) % 100
        return "arm_a" if bucket < arm_a else "arm_b"

    def before_insert(self):
        if not self.assigned_at:
            self.assigned_at = now_datetime()
        if not self.outcome:
            self.outcome = "pending"

    def record_outcome(self, outcome: str) -> None:
        valid = {"approved", "rejected", "cancelled", "expired"}
        if outcome not in valid:
            frappe.throw(frappe._("Invalid outcome {0}; must be one of {1}").format(outcome, valid))
        if self.outcome and self.outcome != "pending":
            frappe.throw(frappe._("Outcome already recorded as {0}; cannot overwrite").format(self.outcome))
        self.outcome = outcome
        self.outcome_at = now_datetime()
        if self.assigned_at:
            delta = (self.outcome_at - self.assigned_at).total_seconds()
            self.cycle_time_seconds = int(delta)
        self.save(ignore_permissions=False)
