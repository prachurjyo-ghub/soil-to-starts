#!/usr/bin/env python3
"""Validate a tool-neutral handoff and report observed GitHub identity; never run PR text."""
import argparse
import html
import json
import os
from pathlib import Path
import re


def event_evidence(payload, tasks, team, records=None):
    repo = payload.get("repository", {}).get("full_name")
    if repo != team["repository"]:
        raise ValueError("Event repository does not match the team registry")
    actor = payload.get("sender", {}).get("login")
    mapping = next((m["name"] for m in team["members"] if m.get("github_login") == actor and m.get("identity_status") == "confirmed"), None)
    common = {"repository": repo, "observed_actor": actor, "confirmed_member": mapping, "identity_status": "confirmed" if mapping else "unconfirmed", "task_completion": "not inferred"}
    pr = payload.get("pull_request")
    if not pr:
        return dict(common, event="push", verification="pending handoff/review", commits=[c["id"] for c in payload.get("commits", []) if c.get("id")], ai_method="unknown", ai_tools="not declared")
    fields = {}
    for line in (pr.get("body") or "").splitlines():
        match = re.fullmatch(r"\s*(Task|Work|Method/tools):\s*(.+?)\s*", line, re.I)
        if match:
            key = match[1].lower()
            if key in fields:
                raise ValueError("Duplicate declaration field: " + key)
            fields[key] = match[2]
    if not all(key in fields for key in ("task", "work", "method/tools")):
        raise ValueError("Fill Task, Work, and Method/tools in the PR template")
    ids = [key for key in re.split(r"[,\s]+", fields["task"]) if key]
    def known_task(key):
        parent, separator, step = key.partition("/")
        return parent in tasks and (not separator or isinstance(tasks, dict) and step in tasks[parent])
    if not ids or any(not known_task(key) for key in ids):
        raise ValueError("Task must identify real local task IDs")
    if records is not None:
        for key in ids:
            parent, separator, step_id = key.partition("/")
            record = records[parent]
            if record["status"] == "planned":
                raise ValueError("Update the actual task/checklist state and evidence before handing off work: " + parent)
            if any(records[dep]["status"] != "done" for dep in record["depends_on"]):
                raise ValueError("Unaccepted work-package prerequisites: " + parent)
            if separator:
                items = {item["id"]: item for item in record["acceptance"]}
                if any(not items[dep]["met"] for dep in items[step_id].get("depends_on", [])):
                    raise ValueError("Unfinished checklist prerequisites: " + key)
    if len(fields["work"]) > 500 or fields["work"].startswith("<"):
        raise ValueError("Work must briefly describe the actual change")
    method, separator, tools = fields["method/tools"].partition(";")
    method, tools = method.strip().lower(), tools.strip()
    if method not in ("human_written", "ai_assisted", "mixed") or not separator or not tools:
        raise ValueError("Method/tools must be human_written; none OR ai_assisted/mixed; actual tool names and role")
    if method == "human_written" and tools.lower() not in ("none", "no ai"):
        raise ValueError("Human-written declaration must state none/no AI")
    if method != "human_written" and tools.lower() in ("none", "unknown", "n/a"):
        raise ValueError("AI-assisted work must name the actual tools")
    return dict(common, event="pull_request", pr=pr.get("number"), pr_url=pr.get("html_url"), pr_author=pr.get("user", {}).get("login"), head_revision=pr.get("head", {}).get("sha"), tasks=ids, work=fields["work"], ai_method=method, ai_tools=tools, declaration="contributor self-report; not AI detection", verification="declaration valid; checks/review/merge still required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=Path, default=os.getenv("GITHUB_EVENT_PATH"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        if not args.event:
            raise ValueError("Supply an event file; this script does not guess GitHub activity")
        records = {p.stem: json.loads(p.read_text()) for p in (args.root / "docs/tasks").glob("*.json")}
        tasks = {key: {item["id"] for item in record["acceptance"]} for key, record in records.items()}
        report = event_evidence(json.loads(args.event.read_text()), tasks, json.loads((args.root / "docs/team.json").read_text()), records)
        output = json.dumps(report, ensure_ascii=False, indent=2)
        print(output)
        summary = os.getenv("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as stream:
                stream.write("## Contribution handoff evidence\n\n<pre>" + html.escape(output) + "</pre>\n")
        return 0
    except (ValueError, OSError) as error:
        print("Contribution declaration error:", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
