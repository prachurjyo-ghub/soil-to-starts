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

    def test_many_prompts_stay_in_one_file(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for number in range(51):
                workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", f"Record task {number}.", "Pending.", "Test fixture", kind="implementation")
        entries = workflow.log_entries(self.root / "docs/AI_USE.md")
        self.assertEqual(len(entries), 51)
        self.assertEqual(list((self.root / "docs/prompt_logs").glob("*.md")), [])
        self.assertFalse((self.root / "docs/PROMPT_LOG.md").exists())
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.check(self.root)

    def test_member_logs_are_separate_and_pipe_safe(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for member in ("fardin", "saim"):
                workflow.log_prompt(self.root, self.tasks, member, "Codex", "Update A | B <labels>.", "Updated labels.", "Test fixture", kind="implementation")
            workflow.check(self.root)
        self.assertEqual({entry["member"] for entry in workflow.log_entries(self.root / "docs/AI_USE.md")}, {"fardin", "saim"})
        self.assertEqual(len(workflow.log_entries(self.root / "docs/AI_USE.md")), 2)
        self.assertIn("&#124;", (self.root / "docs/AI_USE.md").read_text())

    def test_prompt_amend_updates_outcome_without_extra_entry(self):
        with contextlib.redirect_stdout(io.StringIO()):
            key = workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "Track progress.", "Started.", "Current chat", kind="implementation")
        self.assertEqual(self.cli("log-update", key, "--outcome", "Checks passed; review pending."), 0)
        path = self.root / "docs/AI_USE.md"
        self.assertEqual(len(workflow.log_rows(path)), 1)
        self.assertIn("Checks passed; review pending.", path.read_text())
        self.assertIn("Track progress.", path.read_text())

    def test_discussion_categories_are_rejected_without_writes(self):
        before = (self.root / "docs/AI_USE.md").read_bytes()
        for kind in (None, "discussion", "question", "explanation", "brainstorm", "example"):
            with self.subTest(kind=kind), self.assertRaisesRegex(workflow.WorkflowError, "exclude discussion"):
                workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "How would this work?", "Explanation only.", "Test", kind=kind)
        self.assertEqual((self.root / "docs/AI_USE.md").read_bytes(), before)
        self.assertEqual(list((self.root / "docs/prompt_logs").glob("*.md")), [])

    def test_commit_and_push_commands_have_explicit_kinds(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for kind in ("commit", "push"):
                workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", f"{kind.title()} the intended changes.", "Pending; no delivery claimed.", "Test command", kind=kind)
            workflow.check(self.root)
        text = (self.root / "docs/AI_USE.md").read_text()
        self.assertIn("**Type:** commit", text)
        self.assertIn("**Type:** push", text)

    def test_cli_rejects_unclassified_and_discussion_log_calls(self):
        for extra in ([], ["--kind", "discussion"]):
            with self.subTest(extra=extra), self.assertRaises(SystemExit) as result:
                self.cli("log", "--summary", "How does this work?", "--outcome", "Explained.", "--source", "Test", *extra)
            self.assertEqual(result.exception.code, 2)
        self.assertEqual(list((self.root / "docs/prompt_logs").glob("*.md")), [])

    def test_check_rejects_tampered_discussion_category(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "Update the workflow.", "Implemented locally.", "Test", kind="implementation")
        path = self.root / "docs/AI_USE.md"
        path.write_text(path.read_text().replace("**Type:** implementation", "**Type:** discussion"))
        with self.assertRaisesRegex(workflow.WorkflowError, "cannot be logged"):
            workflow.check(self.root)

    def test_markdown_prompt_records_preserve_meaning_and_metadata(self):
        summary = "Allow farmers to choose a location using a map pin or district-name search."
        source = "Actual instruction; labels A | B <reference> & metadata"
        with contextlib.redirect_stdout(io.StringIO()):
            key = workflow.log_prompt(self.root, self.tasks, "fardin", "OpenAI Codex", summary, "The location interface was implemented. Independent review is pending.", source, "TASK-A", kind="implementation")
            workflow.check(self.root)
        path = self.root / "docs/AI_USE.md"
        entries = workflow.log_entries(path)
        self.assertEqual(len(entries), 1)
        self.assertTrue(workflow.entry_matches(entries[0], key))
        self.assertEqual(entries[0]["summary"], summary)
        self.assertEqual(entries[0]["reference"], "TASK-A; " + source)
        self.assertEqual(entries[0]["tool"], "OpenAI Codex")
        self.assertIn("**Refined implementation prompt (AI-written):** " + summary, path.read_text())
        self.assertNotIn("| ID |", path.read_text())
        self.assertNotIn("Original command", path.read_text())

    def test_legacy_table_append_preserves_identity_time_and_escaped_content(self):
        path = self.root / "docs/AI_USE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        row = "| P-legacy | 2026-10-28T19:37:39Z | Codex | implementation | Update A &#124; B &lt;labels&gt;. | Work was recorded; review is pending. | TASK-A; Saved source &amp; evidence |\n"
        path.write_text("# Legacy log\n\n" + workflow.LOG_HEADER + "\n| --- | --- | --- | --- | --- | --- | --- |\n" + row)
        before = workflow.log_entries(path)[0]
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "unassigned", "Codex", "Update the existing instructions.", "The instructions were updated.", "Current command", kind="implementation")
            workflow.check(self.root)
        after = workflow.log_entries(path)
        self.assertEqual({k:v for k,v in after[0].items() if k != "number"}, before)
        self.assertEqual(len(after), 2)
        self.assertIn("<!-- record-id: P-legacy -->", path.read_text())
        self.assertNotIn("| P-legacy", path.read_text())
        self.assertEqual(after[0]["recorded_utc"], "2026-10-28T19:37:39Z")

    def test_legacy_outcome_update_keeps_other_fields_and_allows_readable_sentences(self):
        path = self.root / "docs/AI_USE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(workflow.LOG_HEADER + "\n| P-old | 2026-10-28T19:37:39Z | Codex | push | Push the reviewed branch. | Pending. | TASK-A; Actual user instruction |\n")
        before = workflow.log_entries(path)[0]
        outcome = ("The branch was pushed after the configured workflow and application checks completed successfully, and the remote revision was verified against the local source commit. "
                   "Independent teammate review, physical-phone testing and the scientific integration remain pending; no main-branch merge or deployment was performed.")
        self.assertGreater(len(outcome), 240)
        self.assertEqual(self.cli("log-update", "P-old", "--outcome", outcome), 0)
        after = workflow.log_entries(path)
        self.assertEqual(len(after), 1)
        self.assertEqual({k:v for k,v in after[0].items() if k != "number"}, {**before, "outcome": outcome})

    def test_malformed_or_duplicate_markdown_fields_are_not_silently_discarded(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Update the documentation.", "Review is pending.", "Current instruction", kind="implementation")
        path = self.root / "docs/AI_USE.md"
        original = path.read_text()
        variants = (
            original.replace("**Tool:** Codex\n", ""),
            original.replace("**Tool:** Codex", "**Tool:** Codex\n\n**Tool:** Another tool"),
            original.replace(workflow.AI_END, "Unexpected content inside an entry.\n" + workflow.AI_END),
        )
        for content in variants:
            with self.subTest(content=content):
                path.write_text(content)
                with self.assertRaises(workflow.WorkflowError):
                    workflow.log_entries(path)
                self.assertEqual(path.read_text(), content)

    def test_outcome_limits_and_blank_fields_are_rejected_without_log_writes(self):
        for outcome in ("a" * 481, "line one\nline two", "   "):
            with self.subTest(outcome=outcome), self.assertRaises(workflow.WorkflowError):
                workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Update the project.", outcome, "Current command", kind="implementation")
        self.assertEqual(list((self.root / "docs/prompt_logs").glob("*.md")), [])

    def test_duplicate_ids_in_combined_history_fail_validation(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Update the instructions.", "The instructions were updated.", "Current command", kind="implementation")
        original = self.root / "docs/AI_USE.md"
        entry = workflow.log_entries(original)[0]
        before = original.read_bytes()
        with self.assertRaisesRegex(workflow.WorkflowError, "Duplicate prompt ID"):
            workflow.write_ai_log(self.root, [entry, entry])
        self.assertEqual(original.read_bytes(), before)

    def test_combined_log_preserves_intro_suffix_and_contribution_details_on_update(self):
        path = self.root / "docs/AI_USE.md"
        prefix = "# AI disclosure\n\nKnown historical contribution.\n\n"
        path.write_text(prefix + workflow.AI_START + "\n" + workflow.AI_END + "\n\nFooter evidence stays intact.\n")
        with contextlib.redirect_stdout(io.StringIO()):
            key = workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Implement both location methods.", "The work has started.", "Current instruction", "TASK-A", kind="implementation", purpose="Assist with interface code and tests.", human="Fardin selected the two methods.", files="location.js", before_after="District search becomes district search or a map pin.", review="Review is pending.", next_action="Another teammate reviews the implementation.")
        before = workflow.log_entries(path)[0]
        self.assertEqual(self.cli("log-update", key, "--outcome", "The checks passed. Review remains pending."), 0)
        self.assertEqual(workflow.log_entries(path)[0], {**before, "outcome": "The checks passed. Review remains pending."})
        self.assertTrue(path.read_text().startswith(prefix))
        self.assertTrue(path.read_text().endswith("\n\nFooter evidence stays intact.\n"))

    def test_date_only_display_uses_bangladesh_date_and_retains_original_utc(self):
        path = self.root / "docs/AI_USE.md"
        with patch.object(workflow, "now", return_value="2026-10-31T19:35:45Z"), contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "prachurjo", "Cursor", "Refine the workspace interface.", "The checks passed.", "Current instruction", kind="implementation")
        self.assertIn("**Date:** 2026-11-01", path.read_text())
        self.assertIn("<!-- recorded-utc: 2026-10-31T19:35:45Z -->", path.read_text())
        self.assertEqual(workflow.log_entries(path)[0]["recorded_utc"], "2026-10-31T19:35:45Z")
        path.write_text(path.read_text().replace("**Date:** 2026-11-01", "**Date:** 2026-10-31"))
        with self.assertRaisesRegex(workflow.WorkflowError, "displayed date"):
            workflow.log_entries(path)

    def test_focused_member_history_is_readonly_and_does_not_load_other_members(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for member in ("fardin", "saim", "fardin"):
                workflow.log_prompt(self.root, self.tasks, member, "Codex", f"Update {member}'s task.", "Review is pending.", "Current instruction", kind="implementation")
        path = self.root / "docs/AI_USE.md"
        before = path.read_bytes()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = workflow.main(["--root", str(self.root), "log-show", "--member", "fardin", "--limit", "1"])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().count("## Fardin — Prompt"), 1)
        self.assertIn("**Member:** fardin", output.getvalue())
        self.assertNotIn("**Member:** saim", output.getvalue())
        self.assertEqual(path.read_bytes(), before)

    def test_combined_history_refuses_duplicate_legacy_copies_and_broken_markers(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Update the records.", "The records were updated.", "Current instruction", kind="implementation")
        old_index = self.root / "docs/PROMPT_LOG.md"
        old_index.write_text("# Duplicate old entrypoint\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "live once"):
            workflow.check(self.root)
        old_index.unlink()
        path = self.root / "docs/AI_USE.md"
        original = path.read_text()
        for text in (original.replace(workflow.AI_START, ""), original + workflow.AI_END):
            with self.subTest(text=text):
                path.write_text(text)
                with self.assertRaisesRegex(workflow.WorkflowError, "markers"):
                    workflow.log_entries(path)

    def test_prompt_numbers_are_per_member_and_do_not_change_on_update(self):
        with contextlib.redirect_stdout(io.StringIO()):
            first = workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Update the form.", "The form was updated.", "Current command", kind="implementation")
            other = workflow.log_prompt(self.root, self.tasks, "saim", "Codex", "Review the data manifest.", "Review is pending.", "Current command", kind="implementation")
            second = workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Test the updated form.", "The checks passed.", "Current command", kind="implementation")
        self.assertEqual((first, other, second), ("FARDIN-001", "SAIM-001", "FARDIN-002"))
        path = self.root / workflow.AI_LOG
        before = workflow.log_entries(path)
        self.assertEqual(self.cli("log-update", "fardin-002", "--outcome", "The checks passed. Independent review remains pending."), 0)
        after = workflow.log_entries(path)
        self.assertEqual([(e['id'],e['member'],e['number']) for e in before], [(e['id'],e['member'],e['number']) for e in after])
        text = path.read_text()
        self.assertIn("## Fardin — Prompt 001", text)
        self.assertIn("## Saim — Prompt 001", text)
        self.assertNotIn("## P-", text)

    def test_public_numbers_use_next_available_maximum_and_scale_past_three_digits(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Update the records.", "The records were updated.", "Current command", kind="implementation")
        entries = workflow.log_entries(self.root / workflow.AI_LOG)
        entries[0]['number'] = 1000
        workflow.write_ai_log(self.root, entries)
        with contextlib.redirect_stdout(io.StringIO()):
            key = workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", "Verify the records.", "Verification passed.", "Current command", kind="implementation")
        self.assertEqual(key, "FARDIN-1001")
        self.assertEqual([e['number'] for e in workflow.log_entries(self.root / workflow.AI_LOG)], [1000,1001])

    def test_legacy_ids_remain_valid_lookup_update_and_anchor_aliases(self):
        with contextlib.redirect_stdout(io.StringIO()):
            public = workflow.log_prompt(self.root, self.tasks, "prachurjo", "Cursor", "Review the interface.", "Review is pending.", "Current command", kind="implementation")
        path = self.root / workflow.AI_LOG
        entry = workflow.log_entries(path)[0]
        self.assertEqual(public, "PRACHURJO-001")
        self.assertTrue(workflow.entry_matches(entry, "Prachurjo — Prompt 001"))
        self.assertIn(f'<!-- record-id: {entry["id"]} -->', path.read_text())
        self.assertIn(f'<a id="{entry["id"].lower()}"></a>', path.read_text())
        self.assertIn('<a id="prachurjo-001"></a>', path.read_text())
        self.assertEqual(self.cli("log-show", entry['id']), 0)
        self.assertEqual(self.cli("log-update", entry['id'], "--outcome", "The UI review was recorded."), 0)
        updated = workflow.log_entries(path)[0]
        self.assertEqual((updated['id'],updated['number']), (entry['id'],1))

    def test_duplicate_numbers_and_heading_member_mismatch_are_rejected(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for action in ('Update the form.','Test the form.'):
                workflow.log_prompt(self.root, self.tasks, "fardin", "Codex", action, "Review is pending.", "Current command", kind="implementation")
        path = self.root / workflow.AI_LOG
        entries = workflow.log_entries(path)
        entries[1]['number'] = entries[0]['number']
        before = path.read_bytes()
        with self.assertRaisesRegex(workflow.WorkflowError, "Duplicate member prompt number"):
            workflow.write_ai_log(self.root, entries)
        self.assertEqual(path.read_bytes(), before)
        path.write_text(path.read_text().replace('## Fardin — Prompt 001','## Saim — Prompt 001',1))
        with self.assertRaisesRegex(workflow.WorkflowError, "heading/member mismatch"):
            workflow.log_entries(path)

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
