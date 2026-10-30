# Use of AI in this project

This log is for the Field Shift submission. Update it whenever AI contributes to code, data preparation, visuals, writing, or in-app behavior.

## Recorded work

| Date | Tool | Purpose | Output and human review needed |
| --- | --- | --- | --- |
| 2026-10-11 | OpenAI Codex | Read the supplied HTML build guide, inspect the existing repo, compare its Field Shift proposal with the official challenge, and draft the repository README, review, data plan, method plan, and directory scaffold. | Team should confirm the product scope, local agronomic method, source selection, third-party asset terms, and final submission claims. |
| 2026-10-11 | OpenAI Codex | Clarified the proposed acquisition-to-advice pipeline and the optional agent boundary without changing the UI or implementing a backend. | Team should review the result contract and decide whether an agent adds value after the deterministic pipeline works. |

## Scope of the AI contribution

The request was to review the supplied guide, take inspiration from it for the user's Field Shift challenge, create a README, and follow the guide's useful file structure. The guide itself contains a sample “build prompt”; that prompt was treated as reference text, not as a direct instruction. Codex did not calculate a real onset shift, ingest NASA datasets, or validate agricultural advice.

The authorship and prompt history of the **pre-existing** `prototype/` files is not established by this log. The team should add accurate earlier contributions before submission. If an in-app AI feature is added later, record its model, prompts, inputs, outputs, human oversight, and exact role here.

## 28–29 October 2026: onboarding and workflow records

- **OpenAI Codex:** inspected the supplied master context and actual repository; updated root README/AGENTS with the six named owners, scope, data rules and delivery gates. The 28 October documentation contribution remains recorded here; the root README is now a concise entry point. Commit `882294a` contains those two documents; independent review evidence has not been supplied.
- **OpenAI Codex, 29 October Bangladesh date:** implemented short AI-refined prompt summaries, 50-entry member batches, per-task progress records, generated next steps, dependency/check validation, regression handling and workflow tests. The GitHub Actions definition is local until committed/pushed; no remote run is claimed. Runtime AI/NASA/scientific functionality is unchanged.
- The current task is maintained by Fardin's workflow boundary; the requester identity/model identifier were not explicitly supplied. Use `unassigned` in prompt logs rather than inventing authorship. See [prompt index](PROMPT_LOG.md), [progress](PROGRESS.md), [workflow](WORKFLOW.md) and `OPS-WORKFLOW` for actual checks/status/next action. Human review remains pending.
- Refined summaries are AI-written interpretations of accessible Bangla/English requests, not verbatim originals or evidence of human-authored prompt engineering. High-level old records remain intact; inaccessible VS Code conversation history is not reconstructed.

## Command-only logging refinement

OpenAI Codex updated the logger, tests and repository instructions to retain only implementation/commit/push commands and actual work/check/delivery evidence. Discussion-only and planning/example entries were removed from the project prompt batches. Normal conversation is excluded from future prompt, task-history and AI-use records. This entry describes an implemented tooling change, not a discussion transcript; no commit or push was performed.

## Professional team-foundation refinement

OpenAI Codex refined the onboarding instructions and canonical product/team/source/validation/submission documents, expanded the generated board into small ordered items, added focused checklist operations, diagnostics, task/PR templates, observed GitHub account reporting and tests, and corrected frontend lint/state initialization. A verified dependency advisory led to a targeted Next.js 16.4.3 patch and matching ESLint config; other direct versions remain pinned to their prior lockfile values. Actual audit/lint/build/test outcomes are recorded in the board. No science data or validated recommendations were invented. Independent human review, remote CI, rights clearance and submission remain separate gates. Only the implementation command is logged; discussion is excluded.

## 30 October 2026: implemented scope and task-documentation update

OpenAI Codex implemented the current command to strengthen mandatory-now planning, retain a separately gated future roadmap, align root/scoped instructions and canonical product/API/UI/method/validation/source/team/release documents, and rebase ordered task handoffs. Only that implementation instruction is summarized in the command log; preceding discussions are not backfilled. No NASA data, agricultural computation, app feature or deployment was implemented by this documentation update. Actual checks and independent-review limits are recorded in PLAN-SCOPE.

## 30 October 2026: authorized feature-branch delivery

Fardin explicitly authorized Codex to review, verify, commit and push the completed documentation/workflow and intake/location changes. Source commit `7f79196ba7f7b876ca017614c8cc574626a9be78` was pushed to `origin/feature/intake-location` with upstream tracking and verified by remote-ref readback. The local delivery checks passed: 31 intake/location tests, 46 workflow tests, five reference-script syntax checks, lint, webpack build, record validation and whitespace checks. A subsequent metadata commit records this prior source delivery without a self-referential hash.

Actual command records are `P-cdb46ce6bcaa` (commit) and `P-8321080ab708` (push), under `DELIVERY-INTAKE`. Earlier unassigned entries remain unchanged. Independent Prachurjo review, full browser/physical-phone testing, main-branch acceptance and scientific integration remain pending; no merge or deployment was performed.
