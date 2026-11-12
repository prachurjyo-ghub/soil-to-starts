# Team workflow: prompts, progress and handoffs

This development helper uses Python **3.9 or newer** and its standard library. No runtime AI, API key, package install, database or frontend change is involved. Run commands from the repository root.

Codex uses repository `AGENTS.md` as persistent guidance; see [official instruction-discovery documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md). After updating these rules, start a fresh Codex session in this project or explicitly have the active assistant read the updated files. A log is only claimed saved when the file actually exists and checks pass.

## What is automatic, and what needs evidence

- **The assistant** reads `AGENTS.md`, refines the action request into a professional English sentence, identifies the task and supplies actual work/checks in readable sentences. It keeps purpose, AI work, evidenced human work, changed files, results and review together in the same contribution entry. It does this only for explicit implementation, commit or push instructions and actual work performed or attempted. Normal conversations, questions, explanations, ideas, brainstorming, examples and discussion-only clarifications are never recorded.
- **The helper** saves the supplied wording as Markdown entries, validates task/dependency structure, records explicitly executed checks, maintains the single combined AI-use/contribution file, and regenerates the README snapshot and progress page. It does not translate, infer missing facts or call an AI service. English sentence quality remains the assistant/contributor's responsibility.
- **The team** supplies real source review and human PR approval. A script cannot establish scientific correctness or prove an undocumented review. It never commits, pushes, merges, publishes, watches other chats, or silently runs commands from task JSON.
- **CI**, after this workflow is committed/pushed and Actions is available, checks record integrity, generated views and helper tests. The local check is usable immediately. No remote CI run or branch protection is claimed by adding a YAML file.

## Files to read

1. Humans: [README](../README.md) for onboarding and [PROGRESS](PROGRESS.md) as the daily task board. Agents: load the assigned task and relevant sections only.
2. [PROGRESS.md](PROGRESS.md): generated task checklist, checks, issues, dependencies and next actions.
3. The relevant JSON record under `docs/tasks/`: editable source of truth, one work package per file with small ordered checklist items. Each item includes owner, how, files, verification, prerequisites, errors and evidence.
4. [AI_USE.md](AI_USE.md): the combined contribution history. Read one entry with `log-show ID` or the latest records for a member with `log-show --member NAME --limit 5`.

`AGENTS.md` holds durable rules, not a second mutable progress table. No backend or NASA work is marked done by this workflow installation. Existing root-document changes are recorded with their observed commit, while independent review remains pending.

## Task states and completion

| State | Meaning |
| --- | --- |
| `planned` | Not started. Displayed as **ready** if dependencies are accepted and there are no blockers; otherwise **waiting**. |
| `in_progress` | Active development; prerequisites accepted. Partial implementation and failed checks remain visible. |
| `blocked` | A concrete external blocker, reopened dependency or regression prevents progress. Preserve implemented substeps and failed evidence. |
| `in_review` | Technical acceptance/checks are satisfied; independent review and/or main-branch integration still pending. |
| `done` | Acceptance met with evidence, checks passing, no unresolved issues/blockers, dependencies done, independent human review recorded, and a recorded commit is an ancestor of local `main` or `origin/main`. |

`[x]` in a work-package table means reviewed/merged `done`. Individual checklist items can be ticked when implemented/observed with evidence, while the package remains under review. The count is not a scientific-readiness percentage.

An `issues` item records a known bug to fix in the task. A `blockers` item means something prevents work (for example, missing external source approval). A planned bug-fix task can be ready even though its recorded reproduction check fails. `done`/`in_review` permit neither open issues nor blockers.

## Daily commands

```bash
python3 scripts/workflow.py status
python3 scripts/workflow.py check
```

Start an existing task only after checking current records and authorization:

```bash
python3 scripts/workflow.py update G0-CONTRACT --status in_progress --next "Agree source, crop and API contracts with the four technical owners."
```

This example changes status; run it only when actually starting that work. The installation leaves planned tasks unstarted. Use the real task ID for your work.

Run an actual check and record its outcome:

```bash
python3 scripts/workflow.py verify --cwd prototype OPS-LINT -- npm run lint -- --no-cache
```

Place `--cwd`/`--timeout` **before the task ID**; everything after the ID and `--` is the command. This command currently reproduces the known ESLint configuration failure. It returns nonzero, records the error and refreshes progress. It does not fix lint. Only explicit commands passed to `verify` are run; stored commands are evidence, not executable instructions. Default timeout is 60 seconds.

A passed check never automatically marks a task done. A failed new check on a done task reopens it and blocks active/accepted dependent tasks for re-verification. A failed check on work under review returns it to development. Resolve the bug and record a passing rerun; preserve the history. Clear an issue only with real evidence.

Record an external blocker:

```bash
python3 scripts/workflow.py update G0-CONTRACT --status blocked --blocker "Required source decision has not been supplied." --next "Fardin to resolve the source decision."
```

These are command examples, not assertions of actual current blockers. To clear actual blockers, use `--clear-blockers --note "Evidence explaining the resolution"` and the appropriate state. Do not hide errors by clearing fields without a reason.

## Edit the relevant task record

The JSON fields are intentionally readable: `id`, `title`, `owner`, `collaborators`, `phase`, `status`, `depends_on`, `acceptance`, `checks`, `issues`, `blockers`, `review`, `merge_ref`, `branch`, `issue`, `evidence`, `history`, `updated_at`, `next_action`, and `handoff`.

- Tick an acceptance item with `"met": true` only when its `evidence` describes a real inspected artifact or result.
- Record actual test outputs with `verify`; manual checks must identify the person/action and actual result. Never convert an unrun check into passed.
- Set `review.by` and `review.evidence` only from explicit human approval or an inspected review record. The reviewer must be one of the other five owners; an assistant cannot approve on someone's behalf.
- Set `merge_ref` to the actual implementation commit on local `main`/`origin/main`, after merge. The helper verifies ancestry without network calls; a cached remote ref is not proof of a fresh GitHub state. Record real issue/PR references where available.
- Preserve history and evidence when revising a status. Update the timestamp and next action. If a task is too broad, split it into bounded records.

Then refresh and validate:

```bash
python3 scripts/workflow.py render
python3 scripts/workflow.py check
```

To accept a task after all evidence exists:

```bash
python3 scripts/workflow.py update TASK-ID --status done --note "Acceptance, checks, independent approval and main-branch commit verified."
```

Replace `TASK-ID`; this will refuse missing evidence. A completion record may be a subsequent documentation change referencing an earlier accepted implementation commit. Do not invent a commit hash or create a self-referential commit hash inside its own commit.

## Parallel or out-of-order tasks

Create the task record when work is proposed, including late-stage tasks:

```bash
python3 scripts/workflow.py add SCENARIO-DETAIL --owner Saim --phase G4 --depends G3 --title "Detailed scenario comparison" --acceptance "A reproducible comparison uses documented climate inputs." --next "Wait for G3; define the comparison scope with Fardin."
```

That task displays **waiting** until G3 is done. It does not move earlier gates forward. To perform genuinely independent research/preparation now, create a separate bounded preparation task with its true prerequisites and link the later task to it. Do not rename blocked implementation as complete preparation.

One JSON file per task reduces conflicts between members. Each member works in their own checkout/branch, synchronizes reviewed prerequisites from `main`, edits their own records and logs, then renders views. During merge, combine task/log sources first and regenerate views; do not choose one person's entire generated README over another's. A local writer lock protects concurrent helper calls in the same checkout; it is not a multi-computer synchronization service.

## Implementation command records

Keep AI-use explanations and implementation history together in **[AI_USE.md](AI_USE.md)**. Each action has one entry: its refined prompt, purpose/AI work, evidenced human contribution, affected files, outcome and handoff. Shared context for related commands is recorded once and linked by entry ID. Do not recreate a separate prompt index or member batches, or copy the same narrative into another disclosure.

Classify intent before logging. Only explicit implementation, commit or push instructions qualify. “Can you implement X?” is an action; “How does X work?” and examples are discussion. Extract only the action from mixed messages. Ordinary conversations, understanding questions, brainstorming and examples never trigger log/task/view writes.

Refine Bangla or informal English into one natural, professional English instruction without adding requirements. Use **Refined implementation prompt (AI-written)** rather than “Original command”; raw prompts and transcripts are not required here. Write the actual outcome in one or two complete factual sentences rather than slash-separated shorthand. The assistant supplies this wording; the helper formats records without calling an AI service.

The readable date uses **Asia/Dhaka** and shows the recording date only. The original UTC timestamp remains in an HTML comment so migration does not lose historical precision. Backfills still identify an unknown original command time. Preserve existing IDs, tools, sources, recorded facts and unassigned requesters. Current task records hold progress; an older result describes the evidence recorded then.

Each member has an independent sequence: `FARDIN-001`, `FARDIN-002`, `SAIM-001`, and so on. Headings display the name and number, such as `Fardin — Prompt 001`. The helper allocates the next number without changing older numbers; use the returned key with `log-show` or `log-update`. Hidden internal IDs and their anchor aliases preserve earlier references and timestamps.

### Combined contribution format

Optional fields appear when relevant and supported by evidence. Do not invent a human edit, review, model, original prompt or scientific result to fill a field.

```markdown
## Fardin — Prompt 001

**Date:** [Recording date in Bangladesh]

**Member:** [Confirmed member or unassigned]

**Tool:** [Actual tool; model only if recorded]

**Type:** implementation

**Refined implementation prompt (AI-written):** Allow farmers to select their location using a map pin or district-name search.

**Purpose / AI contribution:** [Why assistance was used and what it actually produced]

**Human contribution:** [Evidenced decisions, authored work, edits or review]

**Changed files:** [Paths or links to the verified full change list]

**Before → After:** [One sentence describing the actual behavior change]

**Actual outcome:** [Actual work, important checks and remaining limitations]

**Review / limitations:** [Relevant unresolved issue or review limit]

**Next action / owner:** [The actual handoff, when known]

**Task / source:** [Real task ID and source of the action instruction]
```

Use the actual tool, including tools used outside an IDE. Assigned roles and GitHub accounts do not establish authorship. Manual code needs no invented AI prompt; record its true method in the task/PR declaration. Commit and push records describe delivery rather than inventing additional creative work. Cite earlier context by its entry link instead of repeating its explanation.

For authorized work, run from the project root (this example is not itself an action to execute):

```bash
python3 scripts/workflow.py log --kind implementation --member fardin --tool Codex --summary "Define the shared data contracts for the Bangladesh rotation planner." --purpose "Assist with documenting the agreed request and response formats." --human "Fardin requested a shared contract before integration." --files "docs/API_CONTRACT.md" --outcome "The contract work has started. The shared decisions still require agreement." --source "Current implementation instruction" --task G0-CONTRACT
```

The prompt allows 240 characters; the outcome allows 480. Optional details allow up to 1800 characters per field but should stay concise. CLI values use one line; the helper writes the Markdown paragraphs. Other optional flags are `--before-after`, `--review`, `--context` and `--next-action`. Member slugs are `fardin`, `saim`, `maruf`, `prachurjo`, `nadim`, `hla` and `unassigned`; use a name only when confirmed by evidence.

Amend the same result after checks finish:

```bash
python3 scripts/workflow.py log-update FARDIN-001 --outcome "The configured checks passed. Independent teammate review remains pending."
```

Read just the relevant history without changing files:

```bash
python3 scripts/workflow.py log-show FARDIN-001
python3 scripts/workflow.py log-show --member fardin --limit 5
```

One entry is required per qualifying instruction, not per discussion, model message or tool call. The helper accepts only implementation/commit/push kinds and checks record structure; honest intent classification, sentence quality and contribution attribution remain the contributor's responsibility. Backfill only instructions supported by an actual source, never from a commit alone. No commit, push, merge, deployment or human approval is inferred from a log entry. Keep credentials and private data out.

## End-of-task checkpoint

1. For implementation/commit/push work, record the refined command once and remember its ID. Discussion-only messages have no entry or end-of-task file updates.
2. Record partial/completed acceptance, changed paths, actual checks, bugs/blockers and next owner in the task record.
3. Use `in_review` for technically finished local work; do not bypass human review or delivery gates.
4. Update that prompt's outcome, run `render`, `check`, and relevant tests.
5. Report the task ID, prompt ID, status, check results, blockers and **next action** to the user. Follow current authorization for commits/pushes; neither the helper nor logging grants it.

Workflow tests:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

These test the development workflow, not scientific recommendations or frontend correctness. A passing `workflow.py check` validates records/views; known failing product checks remain visible rather than being relabeled as passed.

## Focused task and checklist commands

```bash
python3 scripts/workflow.py status --member Saim
python3 scripts/workflow.py status --task G1A
python3 scripts/workflow.py step G1A s01 --state in_progress
python3 scripts/workflow.py step G1A s01 --state done --evidence "Actual output, source/revision and verification result."
python3 scripts/workflow.py step G1A s02 --state blocked --blocker "Actual missing dependency or error."
```

Examples are not commands to execute before their prerequisites are accepted. Starting or completing the first item moves a planned parent to `in_progress`; it never approves that package. A completed item requires evidence and completed item prerequisites. Reopening a prerequisite reopens its completed dependent items. A checkbox does not approve the whole package; all required review/merge conditions still apply. Keep fields `how`, `files`, `verification`, `owner` and `depends_on` accurate so a teammate can work without another briefing.

## Tool-neutral contribution declarations and identity

The PR template requires only `Task:`, `Work:`, and `Method/tools:`. Method is `human_written; none`, or `ai_assisted/mixed; actual tools and their role`. Manual work needs no fake prompt. The CI event verifier reads the GitHub payload, records observed actor and PR author separately, and checks the declaration against real task IDs. Declared work needs an actual task state rather than a stale `planned` record, accepted parent prerequisites and completed prerequisites for any exact checklist ID. A draft can show incomplete/blocked work honestly; separate independent preparation from work whose prerequisites are unfinished. The verifier never executes PR text, infers AI usage, marks a task complete, commits or modifies GitHub settings.

Observed accounts appear in the Actions job summary after publication. `docs/team.json` maps only explicitly confirmed member/account relationships; an unknown account remains unconfirmed. A bare push produces observed commit metadata and pending handoff/review, not a guessed method or done task. A reviewer can use the observed PR/check/source links in the task record. Domain validation and independent approval remain genuine human responsibilities.

## Mandatory-now versus future work

Read [MVP_SCOPE](MVP_SCOPE.md) for current release requirements and [FUTURE_ROADMAP](FUTURE_ROADMAP.md) for deferred options. Future task files use phase Z-FUTURE, depend on G5 and retain an explicit activation blocker. They remain planned/waiting. Accepted G5 alone does not authorize starting them or clearing every blocker. Select and authorize a bounded extension before changing its blocker/dependencies.

G3-STORY and G3-REPORT follow the integrated G3 slice; G4 validates the full MVP. Early media packages cover preparation, while G5 owns final accepted scientific recording/editing and authorized release. PLAN-SCOPE is the documentation change, not completion of these product features. Local documentation ticks must never tick planned science tasks.
