#!/usr/bin/env python3
"""Local team workflow records; Python standard library only. Never commits or pushes."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import time
import uuid

OWNERS = ("Fardin", "Saim", "Maruf", "Prachurjo", "Nadim", "Hla")
STATES = ("planned", "in_progress", "blocked", "in_review", "done")
START = "<!-- workflow:progress:start -->"
END = "<!-- workflow:progress:end -->"
LOG_LIMIT = 50
COMMAND_KINDS = ("implementation", "commit", "push")
LOG_HEADER = "| ID | Recorded UTC | Tool | Command kind | Refined task summary (AI-written) | Actual outcome | Task / source |"


class WorkflowError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise WorkflowError(message)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == content:
        return
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        os.chmod(temporary, path.stat().st_mode & 0o777 if path.exists() else 0o644)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def locked(root):
    lock = root / ".workflow-lock"
    for _ in range(100):
        try:
            lock.mkdir()
            break
        except FileExistsError:
            time.sleep(0.05)
    else:
        raise WorkflowError("Another workflow writer is active, or .workflow-lock is stale. Check the process before removing the lock.")
    try:
        yield
    finally:
        lock.rmdir()


def load_tasks(root):
    tasks = {}
    for path in sorted((root / "docs/tasks").glob("*.json")):
        try:
            task = json.loads(path.read_text())
        except (ValueError, OSError) as error:
            raise WorkflowError(f"Cannot read {path}: {error}") from error
        require(isinstance(task, dict), f"{path}: expected an object")
        key = task.get("id")
        require(key == path.stem and key not in tasks, f"{path}: ID/filename mismatch or duplicate")
        tasks[key] = task
    return tasks


def merged(root, revision):
    """Verify local Git ancestry; does not contact GitHub or prove human review."""
    if not re.fullmatch(r"[0-9a-f]{7,40}", revision or ""):
        return False
    for base in ("refs/heads/main", "refs/remotes/origin/main"):
        result = subprocess.run(["git", "merge-base", "--is-ancestor", revision, base], cwd=root, capture_output=True)
        if result.returncode == 0:
            return True
    return False


def waiting(task, tasks):
    return [key for key in task["depends_on"] if tasks[key]["status"] != "done"]


def validate(root, tasks):
    for key, task in tasks.items():
        require(re.fullmatch(r"[A-Z][A-Z0-9-]*", key), f"Invalid task ID: {key}")
        for field in ("title", "phase", "next_action", "updated_at"):
            require(isinstance(task.get(field), str) and task[field].strip(), f"{key}: missing {field}")
        require(task.get("owner") in OWNERS, f"{key}: unknown owner")
        require(task.get("status") in STATES, f"{key}: invalid status")
        for field in ("depends_on", "collaborators", "acceptance", "checks", "blockers", "issues", "evidence", "history"):
            require(isinstance(task.get(field), list), f"{key}: {field} must be a list")
        deps = task["depends_on"]
        require(len(deps) == len(set(deps)), f"{key}: duplicate dependencies")
        require(all(dep in tasks and dep != key for dep in deps), f"{key}: missing/self dependency")
        require(all(person in OWNERS for person in task["collaborators"]), f"{key}: invalid collaborator")
        require(all(isinstance(value, str) and value.strip() for value in task["blockers"] + task["issues"] + task["evidence"]), f"{key}: empty issue/evidence")
        require(task["acceptance"], f"{key}: acceptance criteria required")
        acceptance_ids = set()
        for item in task["acceptance"]:
            require(isinstance(item, dict), f"{key}: invalid acceptance criterion")
            require(item.get("id") and item["id"] not in acceptance_ids and item.get("text"), f"{key}: invalid/duplicate acceptance ID")
            acceptance_ids.add(item["id"])
            require(type(item.get("met")) is bool, f"{key}: acceptance met must be boolean")
            require(not item["met"] or bool(item.get("evidence", "").strip()), f"{key}: checked acceptance needs evidence")
            require(item.get("owner", task["owner"]) in OWNERS, f"{key}: unknown step owner")
            require(isinstance(item.get("depends_on", []), list), f"{key}: step dependencies must be a list")
            require(isinstance(item.get("blockers", []), list), f"{key}: step blockers must be a list")
            require(not item["met"] or not item.get("blockers"), f"{key}: completed step has unresolved blockers")
            require(item.get("state", "done" if item["met"] else "planned") in ("planned", "in_progress", "blocked", "done"), f"{key}: invalid step state")
            require((item.get("state", "done" if item["met"] else "planned") == "done") == item["met"], f"{key}: step state and checkbox disagree")
        items = {item["id"]: item for item in task["acceptance"]}
        active_steps, visited_steps = set(), set()
        def visit_step(step_id):
            require(step_id not in active_steps, f"{key}: step dependency cycle")
            if step_id in visited_steps:
                return
            active_steps.add(step_id)
            item = items[step_id]
            for dependency in item.get("depends_on", []):
                require(dependency in items and dependency != step_id, f"{key}: missing/self step dependency")
                require(not item["met"] or items[dependency]["met"], f"{key}: completed step has unfinished prerequisite")
                visit_step(dependency)
            active_steps.remove(step_id)
            visited_steps.add(step_id)
        for step_id in items:
            visit_step(step_id)
        for check in task["checks"]:
            require(isinstance(check, dict) and check.get("command"), f"{key}: check command required")
            require(check.get("result") in ("passed", "failed", "not_run"), f"{key}: invalid check result")
            require(check["result"] == "not_run" or bool(check.get("evidence", "").strip()), f"{key}: executed check needs evidence")
        require(isinstance(task.get("review"), dict), f"{key}: review record required")
        if task["status"] in ("in_progress", "in_review"):
            require(not waiting(task, tasks) and not task["blockers"], f"{key}: active work has unfinished prerequisites/blockers; register independent preparation separately")
        if task["status"] in ("in_review", "done"):
            require(all(item["met"] for item in task["acceptance"]), f"{key}: unmet acceptance criteria")
            require(task["checks"] and all(check["result"] == "passed" for check in task["checks"]), f"{key}: passing checks required")
            require(not task["blockers"] and not task["issues"], f"{key}: unresolved blockers/issues")
        if task["status"] == "blocked":
            require(task["blockers"] or waiting(task, tasks), f"{key}: blocked needs a reason")
        if task["status"] == "done":
            require(not waiting(task, tasks), f"{key}: unfinished dependencies")
            reviewer = task["review"].get("by")
            require(reviewer in OWNERS and reviewer != task["owner"], f"{key}: independent human reviewer required")
            require(bool(task["review"].get("evidence", "").strip()), f"{key}: review evidence required")
            require(merged(root, task.get("merge_ref")), f"{key}: merge_ref must be a commit already on local main/origin/main")
    visited, active = set(), set()

    def visit(key):
        require(key not in active, f"Dependency cycle involving {key}")
        if key in visited:
            return
        active.add(key)
        for dep in tasks[key]["depends_on"]:
            visit(dep)
        active.remove(key)
        visited.add(key)

    for key in tasks:
        visit(key)


def ready(task, tasks):
    return task["status"] == "planned" and not task["blockers"] and not waiting(task, tasks)


def cell(value):
    return html.escape(" ".join(str(value).split()), quote=False).replace("|", "&#124;")


def label(task, tasks):
    if task["status"] == "planned" and waiting(task, tasks):
        return "waiting"
    return "ready" if ready(task, tasks) else task["status"]


def snapshot(tasks, detailed=False):
    ordered = sorted(tasks.values(), key=lambda task: (task["phase"], task["id"]))
    done = sum(task["status"] == "done" for task in ordered)
    failed = sum(any(check["result"] == "failed" for check in task["checks"]) for task in ordered)
    lines = [f"**Accepted tasks: {done}/{len(ordered)}. Tasks with recorded failing checks: {failed}.** Counts are task records, not product-completion percentages.", ""]
    lines += ["| Done | Task | Owner | State | Depends on | Next action |", "| --- | --- | --- | --- | --- | --- |"]
    for task in ordered:
        name = f"[{task['id']}](tasks/{task['id']}.json)" if detailed else task["id"]
        dependencies = ", ".join(waiting(task, tasks)) or ("accepted" if task["depends_on"] else "none")
        next_action = "Accepted; hand off documented outputs." if task["status"] == "done" else task["next_action"]
        lines.append(f"| {'[x]' if task['status'] == 'done' else '[ ]'} | {name}: {cell(task['title'])} | {task['owner']} | {label(task, tasks)} | {dependencies} | {cell(next_action)} |")
    lines += ["", "### Next action by member", "", "| Member | Available now / next dependency |", "| --- | --- |"]
    for owner in OWNERS:
        available = [task for task in ordered if task["owner"] == owner and (ready(task, tasks) or task["status"] in ("in_progress", "in_review"))]
        support = [task["id"] for task in ordered if owner in task["collaborators"] and (ready(task, tasks) or task["status"] == "in_progress")]
        text = "; ".join(f"{task['id']}: {task['next_action']}" for task in available)
        if support:
            text += ("; " if text else "") + "Collaborate on " + ", ".join(support)
        if not text:
            owned = [task for task in ordered if task["owner"] == owner and task["status"] != "done"]
            text = "; ".join(f"{task['id']}: waiting for {', '.join(waiting(task, tasks)) or 'documented blocker'}" for task in owned[:2]) or "No open owned task; review the team's handoff queue."
        lines.append(f"| {owner} | {cell(text)} |")
    if detailed:
        lines += ["", "## Acceptance, checks, bugs and handoffs", ""]
        for task in ordered:
            lines += [f"### {task['id']} — {task['title']}", "", f"Owner: **{task['owner']}** · State: `{label(task, tasks)}` · Updated UTC: `{task['updated_at']}`", ""]
            if task.get("purpose"):
                lines += ["**Why:** " + cell(task["purpose"]), ""]
            for item in task["acceptance"]:
                state = item.get("state", "done" if item["met"] else "planned")
                lines += [f"- [{'x' if item['met'] else ' '}] **{item['id']} · {item.get('owner', task['owner'])} · {state}:** {item['text']}"]
                for heading, value in (("How", item.get("how")), ("Files", ", ".join(item.get("files", []))), ("Verify", item.get("verification")), ("Before", ", ".join(item.get("depends_on", []))), ("Error/blocker", "; ".join(item.get("blockers", []))), ("Evidence", item.get("evidence"))):
                    if value:
                        lines.append(f"  - {heading}: {cell(value)}")
            for kind in ("blockers", "issues"):
                lines += [f"- **{kind[:-1].title()}:** {cell(value)}" for value in task[kind]]
            lines += [f"- **Resolved issue:** {cell(value)}" for value in task.get("resolved_issues", [])]
            lines += [f"- Check **{check['result']}**: `{cell(check['command'])}` — {cell(check.get('evidence', 'Not run'))}" for check in task["checks"]]
            if not task["checks"]:
                lines += ["- Checks: not run; no pass claimed."]
            lines += [f"- Review: {cell(task['review'].get('by') or 'pending')} — {cell(task['review'].get('evidence') or 'no approval recorded')}", f"- Delivery: {cell(task.get('merge_ref') or 'no accepted merge recorded')}; branch: {cell(task.get('branch') or 'not recorded')}; issue/PR: {cell(task.get('issue') or 'not created/recorded')}", f"- Handoff: {cell(task.get('handoff', 'Owner to document next consumer.'))}", ""]
    return "\n".join(lines).rstrip() + "\n"


def log_rows(path):
    return [line for line in path.read_text().splitlines() if line.startswith("| P-")]


def compact_snapshot(tasks):
    completed = sum(task["status"] == "done" for task in tasks.values())
    steps = [step for task in tasks.values() for step in task["acceptance"]]
    accepted_steps = sum(step["met"] for step in steps)
    lines = [f"**Accepted work packages: {completed}/{len(tasks)} · Implemented checklist items: {accepted_steps}/{len(steps)}.** Checked items can still await independent review and merge.", "", "| Member | First available action |", "| --- | --- |"]
    for owner in OWNERS:
        candidates = sorted((task for task in tasks.values() if task["owner"] == owner and task["status"] == "in_progress"), key=lambda task: task["id"])
        candidates += sorted((task for task in tasks.values() if task["owner"] == owner and ready(task, tasks)), key=lambda task: (task["phase"], task["id"]))
        if candidates:
            task = candidates[0]
            pending = [step for step in task["acceptance"] if not step["met"] and not step.get("blockers") and all(next(x for x in task["acceptance"] if x["id"] == dep)["met"] for dep in step.get("depends_on", []))]
            action = f"{task['id']} / {pending[0]['id']}: {pending[0]['text']}" if pending else task["next_action"]
        else:
            supports = [task["id"] for task in tasks.values() if owner in task["collaborators"] and (ready(task, tasks) or task["status"] == "in_progress")]
            action = "Review/collaborate on " + ", ".join(supports) if supports else "Read the task board for waiting dependencies and review requests."
        lines.append(f"| {owner} | {cell(action)} |")
    return "\n".join(lines) + "\n"


def views(root, tasks):
    readme = (root / "README.md").read_text()
    require(readme.count(START) == 1 and readme.count(END) == 1, "README workflow markers missing/duplicated")
    prefix, remaining = readme.split(START)
    _, suffix = remaining.split(END)
    block = "\n## Team progress and next steps\n\nGenerated from task records; the detailed board is the team's daily starting point.\n\n" + compact_snapshot(tasks)
    block += "\n[Detailed progress, acceptance and blockers](docs/PROGRESS.md) · [Workflow commands](docs/WORKFLOW.md) · [Short prompt logs](docs/PROMPT_LOG.md)\n\n"
    progress = "# Team task board\n\nGenerated from `docs/tasks/*.json`; update a record or use the helper, then render. This is the single human-readable list of owners, small steps, errors, evidence and handoffs.\n\n**Read this way:** choose your next available work package, follow its small checklist items in order, record errors and real evidence, then hand it off. A checked checklist item means that output is implemented/observed locally. A checked work-package row means passing checks, independent review and an accepted main-branch commit. Neither means national scientific validation.\n\n[Team playbook](TEAM_PLAYBOOK.md) · [Command reference](WORKFLOW.md) · [Validation requirements](VALIDATION.md)\n\n" + snapshot(tasks, detailed=True)
    index = "# Prompt log index\n\nEach entry is a concise **AI-written interpretation**, not a verbatim user prompt or proof of human prompt authorship. Preserve intent; never invent requirements, checks or outcomes. English summaries may come from Bangla or English requests. Original prompts remain in their source conversations when available; this index is not a full transcript.\n\nLog only explicit implementation, commit or push commands and the actual work/checks/delivery evidence associated with them. Never record questions, explanations, brainstorming, examples, normal conversation or discussion-only clarifications, even as summaries. Discussion must not trigger log/task/view writes. Classify intent, not punctuation: “Can you implement X?” is an action; “How would X work?” is discussion. Mixed messages contribute only their action instruction. Use --kind implementation, commit or push; do not infer commands from discussion. Local work remains not pushed until actual delivery evidence is available. Members use separate batches, at most 50 entries each. Read the index/current relevant batch, not every historical log. `unassigned` means the requesting member was not confirmed. Recorded UTC is the logging time; a backfill does not invent the original timestamp.\n\nSee [workflow instructions](WORKFLOW.md) and [AI-use disclosure](AI_USE.md). Add entries with `python3 scripts/workflow.py log`; never include credentials/private data.\n\n| Batch | Entries |\n| --- | --- |\n"
    for path in sorted((root / "docs/prompt_logs").glob("*.md")):
        count = len(log_rows(path))
        require(0 < count <= LOG_LIMIT, f"{path.name}: must contain 1–50 prompt entries")
        index += f"| [{path.stem}](prompt_logs/{path.name}) | {count} |\n"
    if not list((root / "docs/prompt_logs").glob("*.md")):
        index += "| No prompt entries yet | 0 |\n"
    return {root / "README.md": prefix + START + block + END + suffix, root / "docs/PROGRESS.md": progress, root / "docs/PROMPT_LOG.md": index}


def render(root, tasks):
    validate(root, tasks)
    for path, content in views(root, tasks).items():
        write(path, content)


def check(root):
    tasks = load_tasks(root)
    validate(root, tasks)
    if (root / "docs/PRODUCT_SPEC.md").exists():
        for filename, budget in (("AGENTS.md", 900), ("README.md", 1600)):
            require(len((root / filename).read_text().split()) <= budget, f"Instruction budget exceeded: {filename}; move details to the relevant canonical document")
    registry = root / "docs/team.json"
    if registry.exists():
        team = json.loads(registry.read_text())
        require({m["name"] for m in team["members"]} == set(OWNERS) and len(team["members"]) == len(OWNERS), "Team registry must contain exactly the six named owners")
        logins = []
        for member in team["members"]:
            login = member.get("github_login")
            require(login is None or isinstance(login, str) and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", login), "Invalid GitHub login")
            require(member.get("identity_status") in ("unconfirmed", "confirmed"), "Invalid identity status")
            require(member["identity_status"] != "confirmed" or login and member.get("mapping_evidence"), "Confirmed identity needs an explicit mapping source")
            if login:
                logins.append(login.lower())
        require(len(logins) == len(set(logins)), "One GitHub account cannot be mapped to multiple team members")
    prompt_ids = set()
    for path in (root / "docs/prompt_logs").glob("*.md"):
        for row in log_rows(path):
            parts = row.split(" | ")
            require(len(parts) == 7, f"{path}: malformed command row; expected an explicit command kind")
            require(parts[3] in COMMAND_KINDS, f"{path}: discussions/questions/examples cannot be logged as command entries")
            key = parts[0].removeprefix("| ")
            require(key not in prompt_ids, f"Duplicate prompt ID: {key}")
            prompt_ids.add(key)
    for path, expected in views(root, tasks).items():
        require(path.exists() and path.read_text() == expected, f"Stale/missing generated view: {path.relative_to(root)}; run render")
    pages = [root / "README.md", root / "AGENTS.md"] + list((root / "docs").rglob("*.md"))
    for page in pages:
        if not page.exists():
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", page.read_text()):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            require((page.parent / target.split("#", 1)[0]).exists(), f"Broken relative link in {page.relative_to(root)}: {target}")
    print(f"Workflow records valid: {len(tasks)} tasks, {len(prompt_ids)} prompts. Recorded failed product checks remain visible; this is not a product test pass.")


def save_task(root, tasks, task):
    candidate = dict(tasks)
    candidate[task["id"]] = task
    validate(root, candidate)
    write(root / "docs/tasks" / (task["id"] + ".json"), json.dumps(task, ensure_ascii=False, indent=2) + "\n")
    render(root, candidate)


def reopen_dependents(tasks, key):
    for dependent in tasks.values():
        if key in dependent["depends_on"] and dependent["status"] in ("done", "in_progress", "in_review"):
            dependent["status"] = "blocked"
            dependent["blockers"].append(f"Dependency {key} reopened; recheck this task before acceptance.")
            dependent["review"] = {"by": None, "evidence": ""}
            dependent["updated_at"] = now()
            reopen_dependents(tasks, dependent["id"])


def log_prompt(root, tasks, member, tool, summary, outcome, source, task_id=None, *, kind=None):
    require(kind in COMMAND_KINDS, "Log only explicit implementation, commit or push commands; exclude discussion, explanations, ideas and examples")
    require(member in [person.lower() for person in OWNERS] + ["unassigned"], "Use a known member slug or unassigned")
    for name, value, limit in (("summary", summary, 240), ("outcome", outcome, 240), ("tool", tool, 60), ("source", source, 180)):
        require(value and len(value) <= limit and "\n" not in value and "\r" not in value, f"{name}: provide one short line, at most {limit} characters")
    require(task_id is None or task_id in tasks, "Unknown prompt task ID")
    directory = root / "docs/prompt_logs"
    batches = sorted(directory.glob(f"{member}-*.md"))
    path = batches[-1] if batches else directory / f"{member}-0001.md"
    if path.exists() and len(log_rows(path)) >= LOG_LIMIT:
        number = int(path.stem.rsplit("-", 1)[1]) + 1
        path = directory / f"{member}-{number:04d}.md"
    if not path.exists():
        write(path, f"# Command summaries — {member}, batch {path.stem.rsplit('-', 1)[1]}\n\nAI-written interpretations of implementation, commit or push commands only. Discussion, explanations, examples and brainstorming are excluded. UTC is the recording time; original timestamps/model identifiers are not invented.\n\n{LOG_HEADER}\n| --- | --- | --- | --- | --- | --- | --- |\n")
    prompt_id = f"P-{uuid.uuid4().hex[:12]}"
    reference = (task_id + "; " if task_id else "") + source
    row = "| " + " | ".join(cell(value) for value in (prompt_id, now(), tool, kind, summary, outcome, reference)) + " |\n"
    write(path, path.read_text() + row)
    render(root, tasks)
    print(f"Recorded {prompt_id} in {path.relative_to(root)}")
    return prompt_id


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = cli.add_subparsers(dest="action", required=True)
    for action in ("check", "render"):
        commands.add_parser(action)
    status = commands.add_parser("status")
    status.add_argument("--task")
    status.add_argument("--member", choices=OWNERS)
    step = commands.add_parser("step")
    step.add_argument("id")
    step.add_argument("step_id")
    step.add_argument("--state", choices=("planned", "in_progress", "blocked", "done"), required=True)
    step.add_argument("--evidence", default="")
    step.add_argument("--blocker", default="")
    add = commands.add_parser("add")
    add.add_argument("id")
    add.add_argument("--title", required=True)
    add.add_argument("--owner", choices=OWNERS, required=True)
    add.add_argument("--phase", required=True)
    add.add_argument("--depends", nargs="*", default=[])
    add.add_argument("--acceptance", action="append", required=True)
    add.add_argument("--next", required=True)
    update = commands.add_parser("update")
    update.add_argument("id")
    update.add_argument("--status", choices=STATES)
    update.add_argument("--next")
    update.add_argument("--blocker", action="append", default=[])
    update.add_argument("--clear-blockers", action="store_true")
    update.add_argument("--note", default="")
    verify = commands.add_parser("verify")
    verify.add_argument("id")
    verify.add_argument("--cwd", default=".")
    verify.add_argument("--timeout", type=int, default=60)
    verify.add_argument("command", nargs=argparse.REMAINDER)
    log = commands.add_parser("log")
    log.add_argument("--kind", choices=COMMAND_KINDS, required=True, help="Only implementation, commit or push instructions; never ordinary conversation")
    log.add_argument("--member", default="unassigned")
    log.add_argument("--tool", default="Codex")
    log.add_argument("--summary", required=True)
    log.add_argument("--outcome", required=True)
    log.add_argument("--source", required=True)
    log.add_argument("--task")
    amend = commands.add_parser("log-update")
    amend.add_argument("id")
    amend.add_argument("--outcome", required=True)
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    root = args.root.resolve()
    try:
        tasks = load_tasks(root)
        validate(root, tasks)
        if args.action == "check":
            check(root)
            return 0
        if args.action == "status":
            if args.task:
                require(args.task in tasks, "Unknown task")
                print(snapshot({args.task: tasks[args.task]}, detailed=True) if not tasks[args.task]["depends_on"] else json.dumps(tasks[args.task], indent=2, ensure_ascii=False))
            elif args.member:
                for task in tasks.values():
                    if task["owner"] == args.member or args.member in task["collaborators"]:
                        print(f"{task['id']} [{label(task, tasks)}]: {task['next_action']}")
            else:
                print(snapshot(tasks))
            return 0
        with locked(root):
            tasks = load_tasks(root)
            validate(root, tasks)
            if args.action == "render":
                render(root, tasks)
            elif args.action == "step":
                require(args.id in tasks, "Unknown task")
                task = tasks[args.id]
                matches = [item for item in task["acceptance"] if item["id"] == args.step_id]
                require(len(matches) == 1, "Unknown checklist item")
                item = matches[0]
                if item["met"] and args.state != "done":
                    def reopen_step(step_id):
                        for child in task["acceptance"]:
                            if step_id in child.get("depends_on", []) and child["met"]:
                                child.update(met=False, state="blocked", blockers=[f"Checklist prerequisite {step_id} reopened; re-verify this item."])
                                reopen_step(child["id"])
                    reopen_step(item["id"])
                if args.state in ("in_progress", "done"):
                    require(not waiting(task, tasks), "Parent work package has unfinished dependencies")
                    require(all(next(x for x in task["acceptance"] if x["id"] == dep)["met"] for dep in item.get("depends_on", [])), "Checklist prerequisites are unfinished")
                require(args.state != "done" or args.evidence.strip(), "A completed checklist item requires actual evidence")
                require(args.state != "blocked" or args.blocker.strip(), "A blocked checklist item requires a reason")
                item.update(state=args.state, met=args.state == "done", evidence=args.evidence, blockers=[args.blocker] if args.state == "blocked" else [])
                if task["status"] == "planned" and args.state in ("in_progress", "done"):
                    task["status"] = "in_progress"
                if task["status"] in ("done", "in_review") and args.state != "done":
                    previous = task["status"]
                    task["status"] = "in_progress"
                    task["review"] = {"by": None, "evidence": ""}
                    if previous == "done":
                        reopen_dependents(tasks, task["id"])
                task["updated_at"] = now()
                task["history"].append({"at": now(), "note": f"Checklist {args.step_id}: {args.state}", "evidence": args.evidence or args.blocker})
                validate(root, tasks)
                for changed in tasks.values():
                    write(root / "docs/tasks" / (changed["id"] + ".json"), json.dumps(changed, ensure_ascii=False, indent=2) + "\n")
                render(root, tasks)
            elif args.action == "add":
                require(args.id not in tasks, "Task already exists; do not overwrite it")
                task = {"id": args.id, "title": args.title, "owner": args.owner, "collaborators": [], "phase": args.phase, "status": "planned", "depends_on": args.depends, "updated_at": now(), "acceptance": [{"id": f"a{index}", "text": value, "met": False, "evidence": ""} for index, value in enumerate(args.acceptance, 1)], "checks": [], "blockers": [], "issues": [], "evidence": [], "history": [], "review": {"by": None, "evidence": ""}, "merge_ref": None, "branch": None, "issue": None, "next_action": args.next, "handoff": "Record the next consumer and reproduction steps before review."}
                save_task(root, tasks, task)
            elif args.action == "update":
                require(args.id in tasks, "Unknown task")
                task = tasks[args.id]
                previous = task["status"]
                if args.clear_blockers:
                    require(args.note.strip(), "Explain the evidence that resolved blockers in --note")
                    task["blockers"] = []
                task["blockers"].extend(args.blocker)
                if args.next:
                    task["next_action"] = args.next
                if args.status:
                    task["status"] = args.status
                if task["status"] == "in_progress":
                    require(not waiting(task, tasks) and not task["blockers"], "Unfinished prerequisites/blockers: " + ", ".join(waiting(task, tasks) + task["blockers"]))
                task["updated_at"] = now()
                task["history"].append({"at": now(), "from": previous, "to": task["status"], "note": args.note or args.next or "Status update"})
                if previous == "done" and task["status"] != "done":
                    reopen_dependents(tasks, args.id)
                validate(root, tasks)
                for item in tasks.values():
                    write(root / "docs/tasks" / (item["id"] + ".json"), json.dumps(item, ensure_ascii=False, indent=2) + "\n")
                render(root, tasks)
            elif args.action == "verify":
                require(args.id in tasks, "Unknown task")
                command = args.command[1:] if args.command[:1] == ["--"] else args.command
                require(command, "Provide an explicit command after --; recorded commands are never executed automatically")
                cwd = (root / args.cwd).resolve()
                require(cwd.is_relative_to(root) and cwd.is_dir(), "Check cwd must be inside this project")
                require(0 < args.timeout <= 300, "Timeout must be 1–300 seconds")
                try:
                    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=args.timeout)
                    code = result.returncode
                    output = (result.stdout + result.stderr).strip()
                except subprocess.TimeoutExpired:
                    code, output = 124, f"Timed out after {args.timeout} seconds"
                except OSError as error:
                    code, output = 127, str(error)
                task = tasks[args.id]
                check_record = {"command": shlex.join(command), "cwd": args.cwd, "result": "passed" if code == 0 else "failed", "evidence": f"Exit {code}. " + output[-1800:], "run_at_utc": now()}
                old = [item for item in task["checks"] if item["command"] == check_record["command"] and item.get("cwd", ".") == args.cwd]
                task["checks"] = [item for item in task["checks"] if item not in old] + [check_record]
                task["updated_at"] = now()
                if code and task["status"] in ("done", "in_review"):
                    previous = task["status"]
                    task["status"] = "blocked" if previous == "done" else "in_progress"
                    task["review"] = {"by": None, "evidence": ""}
                    if previous == "done":
                        task["blockers"].append("Regression: " + check_record["command"])
                        reopen_dependents(tasks, args.id)
                task["history"].append({"at": now(), "note": f"Check {check_record['result']}: {check_record['command']}"})
                validate(root, tasks)
                for item in tasks.values():
                    write(root / "docs/tasks" / (item["id"] + ".json"), json.dumps(item, ensure_ascii=False, indent=2) + "\n")
                render(root, tasks)
                print(output[-3000:])
                return 0 if code == 0 else 1
            elif args.action == "log":
                log_prompt(root, tasks, args.member.lower(), args.tool, args.summary, args.outcome, args.source, args.task, kind=args.kind)
            elif args.action == "log-update":
                require(args.outcome and len(args.outcome) <= 240 and "\n" not in args.outcome and "\r" not in args.outcome, "Outcome must be one short line, at most 240 characters")
                matches = []
                for path in (root / "docs/prompt_logs").glob("*.md"):
                    for row in log_rows(path):
                        if row.startswith(f"| {args.id} | "):
                            matches.append((path, row))
                require(len(matches) == 1, "Prompt ID missing or duplicated")
                path, row = matches[0]
                parts = row.split(" | ")
                require(len(parts) == 7 and parts[3] in COMMAND_KINDS, "Only classified implementation/commit/push entries can be updated")
                parts[5] = cell(args.outcome)
                write(path, path.read_text().replace(row, " | ".join(parts), 1))
                render(root, tasks)
        return 0
    except (WorkflowError, OSError, KeyError, TypeError) as error:
        print(f"Workflow error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
