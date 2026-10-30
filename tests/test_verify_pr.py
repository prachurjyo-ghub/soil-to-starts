import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("verify_pr", Path(__file__).resolve().parents[1] / "scripts/verify_pr.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContributionTests(unittest.TestCase):
    def setUp(self):
        self.team = {"repository": "owner/repo", "members": [{"name": "Maruf", "github_login": None, "identity_status": "unconfirmed"}]}
        self.event = {"repository": {"full_name": "owner/repo"}, "sender": {"login": "actual-account"}, "pull_request": {"number": 4, "user": {"login": "pr-opener"}, "head": {"sha": "a" * 40}, "body": "Task: G1B\nWork: Added sourced calendars.\nMethod/tools: human_written; none"}}

    def test_manual_contribution_needs_no_fake_prompt(self):
        report = module.event_evidence(self.event, {"G1B"}, self.team)
        self.assertEqual(report["ai_method"], "human_written")
        self.assertEqual(report["identity_status"], "unconfirmed")
        self.assertEqual(report["task_completion"], "not inferred")

    def test_account_and_pr_author_are_separate(self):
        report = module.event_evidence(self.event, {"G1B"}, self.team)
        self.assertEqual(report["observed_actor"], "actual-account")
        self.assertEqual(report["pr_author"], "pr-opener")

    def test_missing_or_duplicate_fields_fail(self):
        for body in ("Work: Something", self.event["pull_request"]["body"] + "\nTask: G1B"):
            self.event["pull_request"]["body"] = body
            with self.assertRaises(ValueError):
                module.event_evidence(self.event, {"G1B"}, self.team)

    def test_unknown_task_fails(self):
        with self.assertRaises(ValueError):
            module.event_evidence(self.event, {"OTHER"}, self.team)

    def test_real_checklist_id_can_identify_a_small_contribution(self):
        self.event["pull_request"]["body"] = "Task: G1B/s01\nWork: Added source registry.\nMethod/tools: human_written; none"
        self.assertEqual(module.event_evidence(self.event, {"G1B": {"s01"}}, self.team)["tasks"], ["G1B/s01"])
        with self.assertRaises(ValueError):
            module.event_evidence(self.event, {"G1B": {"s02"}}, self.team)

    def test_ci_rejects_unaccepted_work_package_dependencies(self):
        records = {"G1B": {"status": "in_progress", "depends_on": ["G0"], "acceptance": []}, "G0": {"status": "planned"}}
        with self.assertRaisesRegex(ValueError, "Unaccepted"):
            module.event_evidence(self.event, {"G1B"}, self.team, records)

    def test_ci_requires_task_state_to_reflect_work(self):
        records = {"G1B": {"status": "planned", "depends_on": [], "acceptance": []}}
        with self.assertRaisesRegex(ValueError, "actual task"):
            module.event_evidence(self.event, {"G1B"}, self.team, records)
        records["G1B"]["status"] = "in_review"
        self.assertEqual(module.event_evidence(self.event, {"G1B"}, self.team, records)["tasks"], ["G1B"])

    def test_ai_tools_must_be_declared(self):
        self.event["pull_request"]["body"] = "Task: G1B\nWork: Added parser.\nMethod/tools: ai_assisted; none"
        with self.assertRaises(ValueError):
            module.event_evidence(self.event, {"G1B"}, self.team)
        self.event["pull_request"]["body"] = "Task: G1B\nWork: Added parser.\nMethod/tools: mixed; ChatGPT draft, human edits"
        self.assertEqual(module.event_evidence(self.event, {"G1B"}, self.team)["ai_method"], "mixed")

    def test_push_without_declaration_is_observed_only(self):
        event = {"repository": {"full_name": "owner/repo"}, "sender": {"login": "actual-account"}, "commits": [{"id": "b" * 40}]}
        report = module.event_evidence(event, {"G1B"}, self.team)
        self.assertEqual(report["ai_method"], "unknown")
        self.assertEqual(report["verification"], "pending handoff/review")

    def test_only_confirmed_registry_mapping_names_a_member(self):
        self.team["members"][0].update(github_login="actual-account", identity_status="confirmed")
        self.assertEqual(module.event_evidence(self.event, {"G1B"}, self.team)["confirmed_member"], "Maruf")

    def test_wrong_repository_is_rejected(self):
        self.event["repository"]["full_name"] = "different/repo"
        with self.assertRaises(ValueError):
            module.event_evidence(self.event, {"G1B"}, self.team)


if __name__ == "__main__":
    unittest.main()
