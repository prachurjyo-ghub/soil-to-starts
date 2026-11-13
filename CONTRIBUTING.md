# Development

One maintainer now completes the remaining work. Read AGENTS.md and [DEVELOPMENT](docs/DEVELOPMENT.md); no team approval/task gate is needed for routine development.

Preserve existing changes. Keep each change coherent, use the existing dependencies and record actual check results. Do not invent scientific outputs or silently mix demonstration fixtures with submitted inputs. Preserve source provenance, rights and previous contributors' records.

```bash
python3 scripts/doctor.py
python3 -B -m unittest discover -s tests -p 'test_*.py'
cd prototype
npm run test:ui
npm run lint
npm run build -- --webpack
```

Root `make check` and `make build` wrap these checks. Scientific data preparation and optional PDF re-extraction have their own documented dependencies; do not install them unnecessarily for frontend work. Add meaningful tests for changed behavior and report checks not run.

Record actual AI implementation commands, tool roles, outcomes and evidenced human input compactly in docs/AI_USE.md. Manual work needs no fake prompt. Do not record discussions. Commit/push/merge/deploy/publication still follow current authorization; solo development does not authorize those actions automatically.
