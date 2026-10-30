"""Tests for dependency gates, honest status, views, checks and prompt rotation."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("workflow", Path(__file__).resolve().parents[1] / "scripts/workflow.py")
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)


def task(key="TASK-A", dependencies=None):
    return {"id": key, "title": "Example test task", "owner": "Fardin", "collaborators": [], "phase": "G0", "status": "planned", "depends_on": dependencies or [], "updated_at": "2026-10-28T19:29:06Z", "acceptance": [{"id": "a1", "text": "Test acceptance", "met": False, "evidence": ""}], "checks": [], "blockers": [], "issues": [], "evidence": [], "history": [], "review": {"by": None, "evidence": ""}, "merge_ref": None, "branch": None, "issue": None, "next_action": "Implement the task", "handoff": "Next owner receives tested output"}


def completed(key="TASK-A", dependencies=None):
    result = task(key, dependencies)
    result.update(status="done", merge_ref="1234567", review={"by": "Saim", "evidence": "Explicit test review"})
    result["acceptance"][0].update(met=True, evidence="Observed test output")
    result["checks"] = [{"command": "test-command", "result": "passed", "evidence": "Test passed"}]
    return result


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "README.md").write_text("# Example\n\n" + workflow.START + "\n" + workflow.END + "\n")
        (self.root / "docs").mkdir()
        (self.root / "docs/WORKFLOW.md").write_text("# Test workflow\n")
        (self.root / "docs/AI_USE.md").write_text("# Test AI disclosure\n")
        (self.root / "docs/TEAM_PLAYBOOK.md").write_text("# Test playbook\n")
        (self.root / "docs/VALIDATION.md").write_text("# Test validation\n")
        self.tasks = {"TASK-A": task()}
        self.save()

    def save(self):
        for value in self.tasks.values():
            workflow.write(self.root / "docs/tasks" / (value["id"] + ".json"), json.dumps(value) + "\n")
        workflow.render(self.root, self.tasks)

    def cli(self, *arguments):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return workflow.main(["--root", str(self.root), *arguments])

    def test_unknown_dependency_rejected(self):
        self.tasks["TASK-A"]["depends_on"] = ["MISSING"]
        with self.assertRaisesRegex(workflow.WorkflowError, "dependency"):
            workflow.validate(self.root, self.tasks)

    def test_cycle_rejected(self):
        self.tasks["TASK-A"]["depends_on"] = ["TASK-B"]
        self.tasks["TASK-B"] = task("TASK-B", ["TASK-A"])
        with self.assertRaisesRegex(workflow.WorkflowError, "cycle"):
            workflow.validate(self.root, self.tasks)

    def test_unchecked_acceptance_cannot_be_done(self):
        value = completed()
        value["acceptance"][0]["met"] = False
        with self.assertRaisesRegex(workflow.WorkflowError, "acceptance"):
            workflow.validate(self.root, {value["id"]: value})

    def test_failed_or_unrun_checks_cannot_be_done(self):
        for status in ("failed", "not_run"):
            value = completed()
            value["checks"][0]["result"] = status
            with self.subTest(status=status), self.assertRaisesRegex(workflow.WorkflowError, "passing checks"):
                workflow.validate(self.root, {value["id"]: value})

    def test_pending_or_self_review_cannot_be_done(self):
        for reviewer in (None, "Fardin"):
            value = completed()
            value["review"]["by"] = reviewer
            with self.subTest(reviewer=reviewer), self.assertRaisesRegex(workflow.WorkflowError, "independent"):
                workflow.validate(self.root, {value["id"]: value})

    def test_unmerged_commit_cannot_be_done(self):
        value = completed()
        with patch.object(workflow, "merged", return_value=False), self.assertRaisesRegex(workflow.WorkflowError, "merge_ref"):
            workflow.validate(self.root, {value["id"]: value})

    def test_completed_dependency_unlocks_parallel_work(self):
        tasks = {"TASK-A": completed(), "TASK-B": task("TASK-B", ["TASK-A"]), "TASK-C": task("TASK-C", ["TASK-A"])}
        with patch.object(workflow, "merged", return_value=True):
            workflow.validate(self.root, tasks)
        self.assertTrue(workflow.ready(tasks["TASK-B"], tasks))
        self.assertTrue(workflow.ready(tasks["TASK-C"], tasks))

    def test_start_blocked_task_does_not_modify_records(self):
        self.tasks["TASK-B"] = task("TASK-B", ["TASK-A"])
        self.save()
        before = (self.root / "docs/tasks/TASK-B.json").read_bytes()
        self.assertEqual(self.cli("update", "TASK-B", "--status", "in_progress"), 1)
        self.assertEqual(before, (self.root / "docs/tasks/TASK-B.json").read_bytes())

    def test_manual_active_status_cannot_bypass_dependencies(self):
        self.tasks["TASK-B"] = task("TASK-B", ["TASK-A"])
        self.tasks["TASK-B"]["status"] = "in_progress"
        with self.assertRaisesRegex(workflow.WorkflowError, "unfinished prerequisites"):
            workflow.validate(self.root, self.tasks)

    def test_verify_accepts_explicit_project_subdirectory(self):
        (self.root / "subdirectory").mkdir()
        result = self.cli("verify", "--cwd", "subdirectory", "TASK-A", "--", sys.executable, "-c", "from pathlib import Path; print(Path.cwd().name)")
        self.assertEqual(result, 0)
        check = workflow.load_tasks(self.root)["TASK-A"]["checks"][0]
        self.assertEqual(check["cwd"], "subdirectory")
        self.assertIn("subdirectory", check["evidence"])

    def test_verify_refuses_directory_outside_project(self):
        self.assertEqual(self.cli("verify", "--cwd", "..", "TASK-A", "--", sys.executable, "-c", "print('must not run')"), 1)
        self.assertEqual(workflow.load_tasks(self.root)["TASK-A"]["checks"], [])

    def test_add_late_task_preserves_earlier_task(self):
        before = copy.deepcopy(self.tasks["TASK-A"])
        result = self.cli("add", "LATE-TASK", "--title", "Later work", "--owner", "Saim", "--phase", "G4", "--depends", "TASK-A", "--acceptance", "Verified result", "--next", "Wait for TASK-A")
        self.assertEqual(result, 0)
        records = workflow.load_tasks(self.root)
        self.assertEqual(records["TASK-A"], before)
        self.assertFalse(workflow.ready(records["LATE-TASK"], records))
        self.assertEqual(workflow.label(records["LATE-TASK"], records), "waiting")

    def test_readonly_check_detects_stale_view(self):
        path = self.root / "docs/PROGRESS.md"
        path.write_text("stale")
        before = path.read_bytes()
        with self.assertRaisesRegex(workflow.WorkflowError, "Stale"):
            workflow.check(self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_render_is_idempotent(self):
        first = (self.root / "README.md").read_bytes()
        workflow.render(self.root, self.tasks)
        self.assertEqual((self.root / "README.md").read_bytes(), first)

    def test_check_refuses_broken_relative_link(self):
        path = self.root / "docs/WORKFLOW.md"
        path.write_text("[Missing evidence](missing.json)\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "Broken relative link"):
            workflow.check(self.root)

    def test_professional_docs_have_small_entrypoint_budgets(self):
        (self.root / "docs/PRODUCT_SPEC.md").write_text("# Product\n")
        original = (self.root / "README.md").read_text()
        for filename, words in (("AGENTS.md", 901), ("README.md", 1601)):
            with self.subTest(filename=filename):
                (self.root / "AGENTS.md").write_text("# Rules\n")
                (self.root / "README.md").write_text(original)
                if filename == "README.md":
                    (self.root / filename).write_text("word " * words + "\n" + workflow.START + "\n" + workflow.END)
                else:
                    (self.root / filename).write_text("word " * words)
                workflow.render(self.root, self.tasks)
                with self.assertRaisesRegex(workflow.WorkflowError, "Instruction budget exceeded"):
                    workflow.check(self.root)

    def test_prompt_rotation_at_fifty(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for number in range(51):
                workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", f"Record task {number}.", "Pending.", "Test fixture", kind="implementation")
        files = sorted((self.root / "docs/prompt_logs").glob("*.md"))
        self.assertEqual([len(workflow.log_rows(path)) for path in files], [50, 1])
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.check(self.root)

    def test_member_logs_are_separate_and_pipe_safe(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for member in ("fardin", "saim"):
                workflow.log_prompt(self.root, self.tasks, member, "Codex", "Update A | B <labels>.", "Updated labels.", "Test fixture", kind="implementation")
            workflow.check(self.root)
        self.assertEqual(len(list((self.root / "docs/prompt_logs").glob("*.md"))), 2)
        self.assertIn("&#124;", (self.root / "docs/prompt_logs/fardin-0001.md").read_text())

    def test_prompt_amend_updates_outcome_without_extra_entry(self):
        with contextlib.redirect_stdout(io.StringIO()):
            key = workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "Track progress.", "Started.", "Current chat", kind="implementation")
        self.assertEqual(self.cli("log-update", key, "--outcome", "Checks passed; review pending."), 0)
        path = self.root / "docs/prompt_logs/unassigned-0001.md"
        self.assertEqual(len(workflow.log_rows(path)), 1)
        self.assertIn("Checks passed; review pending.", path.read_text())
        self.assertIn("Track progress.", path.read_text())

    def test_discussion_categories_are_rejected_without_writes(self):
        before = (self.root / "docs/PROMPT_LOG.md").read_bytes()
        for kind in (None, "discussion", "question", "explanation", "brainstorm", "example"):
            with self.subTest(kind=kind), self.assertRaisesRegex(workflow.WorkflowError, "exclude discussion"):
                workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "How would this work?", "Explanation only.", "Test", kind=kind)
        self.assertEqual((self.root / "docs/PROMPT_LOG.md").read_bytes(), before)
        self.assertEqual(list((self.root / "docs/prompt_logs").glob("*.md")), [])

    def test_commit_and_push_commands_have_explicit_kinds(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for kind in ("commit", "push"):
                workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", f"{kind.title()} the intended changes.", "Pending; no delivery claimed.", "Test command", kind=kind)
            workflow.check(self.root)
        text = (self.root / "docs/prompt_logs/unassigned-0001.md").read_text()
        self.assertIn(" | commit | ", text)
        self.assertIn(" | push | ", text)

    def test_cli_rejects_unclassified_and_discussion_log_calls(self):
        for extra in ([], ["--kind", "discussion"]):
            with self.subTest(extra=extra), self.assertRaises(SystemExit) as result:
                self.cli("log", "--summary", "How does this work?", "--outcome", "Explained.", "--source", "Test", *extra)
            self.assertEqual(result.exception.code, 2)
        self.assertEqual(list((self.root / "docs/prompt_logs").glob("*.md")), [])

    def test_check_rejects_tampered_discussion_category(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "Update the workflow.", "Implemented locally.", "Test", kind="implementation")
        path = self.root / "docs/prompt_logs/unassigned-0001.md"
        path.write_text(path.read_text().replace(" | implementation | ", " | discussion | "))
        with self.assertRaisesRegex(workflow.WorkflowError, "cannot be logged"):
            workflow.check(self.root)

    def test_checklist_requires_evidence_and_preserves_task_gate(self):
        self.assertEqual(self.cli("step", "TASK-A", "a1", "--state", "done"), 1)
        self.assertEqual(self.cli("step", "TASK-A", "a1", "--state", "done", "--evidence", "Observed output and relevant check."), 0)
        record = workflow.load_tasks(self.root)["TASK-A"]
        self.assertTrue(record["acceptance"][0]["met"])
        self.assertEqual(record["status"], "in_progress")

    def test_checklist_dependency_blocks_out_of_order_completion(self):
        self.tasks["TASK-A"]["acceptance"].append({"id": "a2", "text": "Dependent step", "met": False, "evidence": "", "depends_on": ["a1"]})
        self.save()
        self.assertEqual(self.cli("step", "TASK-A", "a2", "--state", "done", "--evidence", "Claimed output"), 1)
        self.assertFalse(workflow.load_tasks(self.root)["TASK-A"]["acceptance"][1]["met"])

    def test_checklist_cycle_is_rejected(self):
        self.tasks["TASK-A"]["acceptance"][0]["depends_on"] = ["a2"]
        self.tasks["TASK-A"]["acceptance"].append({"id": "a2", "text": "Dependent step", "met": False, "evidence": "", "depends_on": ["a1"]})
        with self.assertRaisesRegex(workflow.WorkflowError, "cycle"):
            workflow.validate(self.root, self.tasks)

    def test_checklist_blocker_is_visible_without_completion(self):
        self.assertEqual(self.cli("step", "TASK-A", "a1", "--state", "blocked", "--blocker", "Source approval unavailable"), 0)
        record = workflow.load_tasks(self.root)["TASK-A"]
        self.assertFalse(record["acceptance"][0]["met"])
        self.assertIn("Source approval unavailable", (self.root / "docs/PROGRESS.md").read_text())

    def test_reopening_checklist_prerequisite_reopens_done_children(self):
        for item in self.tasks["TASK-A"]["acceptance"]:
            item.update(met=True, state="done", evidence="Observed output")
        self.tasks["TASK-A"]["acceptance"].append({"id": "a2", "text": "Dependent step", "met": True, "state": "done", "evidence": "Observed output", "depends_on": ["a1"]})
        self.save()
        self.assertEqual(self.cli("step", "TASK-A", "a1", "--state", "in_progress"), 0)
        self.assertEqual(workflow.load_tasks(self.root)["TASK-A"]["acceptance"][1]["state"], "blocked")

    def test_checklist_owner_must_be_a_real_team_member(self):
        self.tasks["TASK-A"]["acceptance"][0]["owner"] = "Invented person"
        with self.assertRaisesRegex(workflow.WorkflowError, "step owner"):
            workflow.validate(self.root, self.tasks)

    def test_focused_member_status_succeeds(self):
        self.assertEqual(self.cli("status", "--member", "Fardin"), 0)
        self.assertEqual(self.cli("status", "--task", "TASK-A"), 0)

    def test_log_refuses_long_or_multiline_summary(self):
        for summary in ("a" * 241, "line one\nline two"):
            with self.subTest(summary=summary), self.assertRaises(workflow.WorkflowError):
                workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", summary, "Pending.", "Test", kind="implementation")

    def test_verify_executes_check_and_records_real_failure(self):
        result = self.cli("verify", "TASK-A", "--", sys.executable, "-c", "import sys; print('observed failure'); sys.exit(3)")
        self.assertEqual(result, 1)
        record = workflow.load_tasks(self.root)["TASK-A"]
        self.assertEqual(record["checks"][0]["result"], "failed")
        self.assertIn("Exit 3", record["checks"][0]["evidence"])
        self.assertIn("observed failure", (self.root / "docs/PROGRESS.md").read_text())
        self.assertNotEqual(record["status"], "done")

    def test_passing_check_does_not_automatically_accept_task(self):
        self.assertEqual(self.cli("verify", "TASK-A", "--", sys.executable, "-c", "print('passed')"), 0)
        self.assertEqual(workflow.load_tasks(self.root)["TASK-A"]["status"], "planned")

    def test_dependency_regression_reopens_active_and_done_consumers(self):
        tasks = {"TASK-A": completed(), "TASK-B": completed("TASK-B", ["TASK-A"]), "TASK-C": task("TASK-C", ["TASK-B"])}
        tasks["TASK-C"]["status"] = "in_progress"
        tasks["TASK-A"]["status"] = "blocked"
        tasks["TASK-A"]["blockers"] = ["Regression"]
        workflow.reopen_dependents(tasks, "TASK-A")
        self.assertEqual(tasks["TASK-B"]["status"], "blocked")
        self.assertEqual(tasks["TASK-C"]["status"], "blocked")
        workflow.validate(self.root, tasks)

    def test_real_git_ancestry_proof(self):
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.DEVNULL).decode().strip()
        git("init", "-b", "main")
        git("config", "user.email", "workflow-test@example.invalid")
        git("config", "user.name", "Workflow Test")
        git("add", "README.md")
        git("commit", "-m", "test baseline")
        revision = git("rev-parse", "HEAD")
        self.assertTrue(workflow.merged(self.root, revision))
        self.assertFalse(workflow.merged(self.root, "deadbee"))
        self.assertFalse(workflow.merged(self.root, "--all"))


if __name__ == "__main__":
    unittest.main()
