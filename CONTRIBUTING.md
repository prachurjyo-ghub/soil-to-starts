# Contributing

1. Read [mandatory scope](docs/MVP_SCOPE.md); [future tracks](docs/FUTURE_ROADMAP.md) stay blocked until separately activated. Open [the task board](docs/PROGRESS.md). Choose an available item for your role; inspect its prerequisites, files, verification and handoff. Coordinate shared files with the owner.
2. Check `git status --short --branch`. Preserve teammates' changes. From a clean tree, update `main` with `git pull --ff-only origin main`, then create a bounded branch. Do not work simultaneously in one shared checkout.
3. Implement the smallest complete item. Use existing dependencies/lockfile. Source-backed scientific constraints and runtime-AI exclusions are in [AGENTS.md](AGENTS.md).
4. Record actual checklist evidence, tests, errors and next action. Run the relevant checks and regenerate the board. Starting a checklist item starts its parent package; a tick is local implementation evidence, while reviewed/merged completion is separate.
5. Open a PR using the three-field declaration: **Task**, **Work**, **Method/tools**. Update the declared task's actual state first; CI rejects stale planned records and unfinished prerequisites. Declare human-written or actual AI assistance. Do not invent prompts for manual work. Different teammate review is required; scientific claims need the responsible domain owner's review.

## Commands

```bash
python3 scripts/doctor.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/workflow.py check
python3 scripts/workflow.py status --member Saim
```

In `prototype/`: `npm ci`, `npm run dev`, `npm run lint`, `npm run build -- --webpack`, then `npm run start` after a successful build. Root `make check` and `make build` wrap these checks. Python helpers need no package installation. Science/API test commands become real with their implementation; do not invent them.

Only implementation/commit/push commands are logged, using a short AI-refined summary and actual result. Ordinary discussion, questions, examples and brainstorming are excluded. Keep secrets, large downloads and unapproved personal information out of Git/prompts. See [workflow](docs/WORKFLOW.md) for update commands and [playbook](docs/TEAM_PLAYBOOK.md) for team ownership.

Humans authorize commits, pushes, merges and release. Stage only intended files and inspect the staged diff. No force pushes, fabricated coauthors or unrelated upgrades. After prerequisite PRs merge, downstream owners update from `main` and record the revision used.
