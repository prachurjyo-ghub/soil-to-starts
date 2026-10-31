# AI Use and Contribution Log

This is the single record of implemented AI assistance and related commit/push instructions for Soil to Stars. It combines the former disclosure and member command logs; shared contribution context is recorded once and linked by ID. Recorded tools include OpenAI Codex and Cursor. Exact model versions and earlier prototype authorship remain unconfirmed where no source establishes them.

Refined prompts are AI-written English interpretations of real action requests, not verbatim quotes. Ordinary discussion, understanding questions, brainstorming and examples are excluded. Human contribution means evidenced decisions, authored work, edits or review; an assigned role or Git account alone is not authorship evidence.

Dates show the recording date in **Asia/Dhaka**; original UTC precision is retained in HTML comments. Backfills distinguish an unknown original command time. Historical outcomes describe evidence known then; linked task records hold current progress. This file does not establish scientific correctness or competition acceptance.

Read one entry with `python3 scripts/workflow.py log-show FARDIN-001`, or a member's latest entries with `python3 scripts/workflow.py log-show --member fardin --limit 5`. The [workflow instructions](WORKFLOW.md#combined-contribution-format) explain future entries. The helper formats supplied text and does not call AI.

## Historical contribution — guide review and initial documentation

**Recorded period:** 11 October 2026, retained from the earlier AI-use record.

**Responsible member / tool:** Fardin, confirmed as the historical requester; OpenAI Codex.

**Why AI was used:** To help review the supplied build guide and prepare the project documentation and scaffold.

**Refined implementation prompt (AI-written):** Review the supplied guide against the Field Shift challenge, and prepare the project README, data plan, methodology and directory scaffold.

**AI contribution:** Drafted documentation and planning materials after inspecting the repository and supplied context. The guide's embedded sample prompt was treated as reference material.

**Team contribution:** Fardin supplied the challenge, project idea and build-guide context. Individual authorship of the pre-existing prototype and earlier human edits was not established by this record.

**Review and limitations:** Product scope, scientific methods, sources, asset rights and submission claims require human confirmation. This contribution did not ingest NASA data, compute climate trends or validate crop advice.

**Evidence:** The earlier AI-use record and [build-guide review](BUILD_GUIDE_REVIEW.md). No original prompt ID or exact model version was recorded.

**Attribution update — 2026-11-01:** Fardin explicitly confirmed that the historical unassigned requester was him. The five affected command records and earlier requester attribution now name Fardin; original dates, tools, outcomes and source evidence are retained. This confirms requester identity, not individual code authorship or a GitHub-account mapping.

**Record numbering:** Each member has a separate stable sequence, displayed as `Fardin — Prompt 001` or `Prachurjo — Prompt 001`. Use keys such as `FARDIN-001` with the helper. Numbering follows recorded order, with commits before pushes at equal recording times; backfills do not establish unknown original timing. Legacy IDs remain hidden lookup/link aliases.

<!-- workflow:ai-records:start -->

## Fardin — Prompt 001

<a id="fardin-001"></a>
<a id="p-4be1d0f3da4f"></a>
<!-- record-id: P-4be1d0f3da4f -->

**Date:** 2026-10-29

<!-- recorded-utc: 2026-10-28T19:37:39Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Add concise implementation-command records and a task board that tracks owners, dependencies, blockers, verification evidence and next steps.

**Purpose / AI contribution:** Implement workflow commands, member records, task checklists, generated views, dependency gates and regression handling.

**Human contribution:** Fardin defined command-only logging and a shared view of owners, dependencies, errors, verification and next steps.

**Changed files:** [Workflow helper](../scripts/workflow.py), [tests](../tests/test_workflow.py) and [OPS-WORKFLOW](tasks/OPS-WORKFLOW.json).

**Actual outcome:** Logging and task tracking were implemented locally, and 23 workflow tests passed along with record and link checks. An existing frontend lint failure remained recorded; application and scientific behavior did not change, and independent review, commit and push were pending.

**Review / limitations:** Fardin is the confirmed requester and workflow owner. This attribution does not establish individual code authorship or independent approval.

**Related context:** Shared workflow context for [FARDIN-003](#fardin-003) and [FARDIN-004](#fardin-004).

**Task / source:** OPS-WORKFLOW; Current request in this Codex conversation

## Fardin — Prompt 002

<a id="fardin-002"></a>
<a id="p-8199e2e2d031"></a>
<!-- record-id: P-8199e2e2d031 -->

**Date:** 2026-10-29

<!-- recorded-utc: 2026-10-28T19:37:39Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Create project onboarding documents that explain team responsibilities, development dependencies, scientific scope and the use of AI assistance.

**Purpose / AI contribution:** Draft onboarding rules from the supplied project context.

**Human contribution:** Fardin supplied the six members’ names and coordination requirements; individual human edits remain unconfirmed.

**Changed files:** [README](../README.md), [AGENTS](../AGENTS.md) and [DOC-FOUNDATION](tasks/DOC-FOUNDATION.json).

**Actual outcome:** The README and AGENTS updates were observed in commit 882294a. Independent review had not been recorded.

**Review / limitations:** The contribution was attributed to 28 October 2026; the command entry is a backfill with an unknown original UTC.

**Task / source:** DOC-FOUNDATION; Backfill: visible chat; original UTC unknown

## Fardin — Prompt 003

<a id="fardin-003"></a>
<a id="p-b73dc9b061a3"></a>
<!-- record-id: P-b73dc9b061a3 -->

**Date:** 2026-10-29

<!-- recorded-utc: 2026-10-29T16:27:42Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Record only implementation, commit and push instructions, and remove discussion entries from the command logs.

**Actual outcome:** Command-only logging rules were implemented, and ten non-implementation entries were removed. All 27 workflow tests and record and link checks passed; the changes had not been committed or pushed at that time.

**Related context:** See [FARDIN-001](#fardin-001) for the shared AI purpose, human contribution, review limits and file evidence.

**Task / source:** OPS-WORKFLOW; Implementation command in current Codex conversation

## Fardin — Prompt 004

<a id="fardin-004"></a>
<a id="p-5c764c535e1b"></a>
<!-- record-id: P-5c764c535e1b -->

**Date:** 2026-10-29

<!-- recorded-utc: 2026-10-29T17:21:59Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Improve project onboarding, the team task board, contribution handoffs and verification checks so each member can follow the development process.

**Purpose / AI contribution:** Add contribution templates, correct frontend lint/state initialization and apply the recorded targeted dependency fix.

**Actual outcome:** The project foundation was updated with 84 task checklist items, onboarding and pull-request checks, and targeted dependency fixes. All 46 tests, lint, the production build, the dependency audit and HTTP smoke checks passed locally; independent review and push remained pending.

**Review / limitations:** The recorded dependency advisory prompted a Next.js 16.4.3 patch with matching ESLint configuration; other direct versions remained pinned.

**Related context:** See [FARDIN-001](#fardin-001) for the shared AI purpose, human contribution, review limits and file evidence.

**Task / source:** OPS-WORKFLOW; Current implementation request and professional-refinement follow-up

## Fardin — Prompt 005

<a id="fardin-005"></a>
<a id="p-c4d152de7e93"></a>
<!-- record-id: P-c4d152de7e93 -->

**Date:** 2026-10-30

<!-- recorded-utc: 2026-10-30T10:00:13Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Strengthen the mandatory product plan, retain a separate future roadmap, and align the specifications, agent instructions and ordered team tasks.

**Purpose / AI contribution:** Align the product, API, UI, sources, methodology, validation, team and release documents with the mandatory/future split.

**Human contribution:** Fardin selected the mandatory-now versus future split and practical ordered handoffs.

**Changed files:** [Mandatory scope](MVP_SCOPE.md), [future roadmap](FUTURE_ROADMAP.md) and [PLAN-SCOPE](tasks/PLAN-SCOPE.json).

**Actual outcome:** Two scope documents and a 26-package plan with 125 checklist steps were updated. All 46 helper tests and record and link checks passed; product features remained planned, and independent review, commit and push were pending.

**Review / limitations:** This changed planning documentation; NASA acquisition, scientific computation and planned application features were not implemented.

**Task / source:** PLAN-SCOPE; Current explicit project-documentation update command

## Fardin — Prompt 006

<a id="fardin-006"></a>
<a id="p-40f8b1c01bd7"></a>
<!-- record-id: P-40f8b1c01bd7 -->

**Date:** 2026-10-30

<!-- recorded-utc: 2026-10-30T14:57:12Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Require farmers across all 64 Bangladesh districts to complete the six-question intake, with bilingual validation and a summary that clearly states scientific planning is unavailable.

**Purpose / AI contribution:** Build mounted intake controls, shared validation, separate drafts/submissions, input summaries and tests.

**Human contribution:** Fardin selected nationwide coverage, approved the question order and required meaningful answers.

**Changed files:** [Intake UI](../prototype/public/reference/intake-ui.js) and [complete intake change/QA record](INTAKE_QA.md).

**Actual outcome:** Required intake for all 64 districts was implemented; 18 intake tests, 46 workflow tests, script syntax, lint, build and record checks passed, with English, Bangla and 400-pixel browser checks recorded. Scientific planning remained unavailable, independent review was pending, and no commit, push or deployment had been performed.

**Review / limitations:** Supported crop identities were for intake only, and illustrative demo results remained separate.

**Task / source:** INTAKE-UI; Current user attachment: Pasted text.txt

## Fardin — Prompt 007

<a id="fardin-007"></a>
<a id="p-c57fe1ebaa44"></a>
<!-- record-id: P-c57fe1ebaa44 -->

**Date:** 2026-10-30

<!-- recorded-utc: 2026-10-30T15:34:40Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Allow farmers to select their location using either a confirmed map pin or district-name search, with local district validation and preservation of their saved answers.

**Purpose / AI contribution:** Implement MapLibre, pin confirmation, district search, local containment, saved-answer handling and version-two migration.

**Human contribution:** Fardin requested both location methods and nationwide coverage; Prachurjo was assigned independent review.

**Changed files:** [Map controller](../prototype/public/reference/intake-map.js), [containment](../prototype/public/reference/location.js) and [complete location change/QA record](LOCATION_QA.md).

**Actual outcome:** The two location methods, licensed local boundaries for 64 districts and version-two migration were implemented; 31 intake tests, 46 workflow tests, syntax, lint, build and eight HTTP asset checks passed. Browser and phone verification remained unconfirmed at this handoff, independent review was pending, and no commit, push or deployment had been performed.

**Review / limitations:** Administrative boundaries are approximate; a precise pin establishes neither a surveyed field boundary nor field-resolution NASA evidence.

**Task / source:** INTAKE-MAP; Current user attachment: Pasted text.txt

## Fardin — Prompt 008

<a id="fardin-008"></a>
<a id="p-cdb46ce6bcaa"></a>
<!-- record-id: P-cdb46ce6bcaa -->

**Date:** 2026-10-30

<!-- recorded-utc: 2026-10-30T16:43:10Z -->

**Member:** fardin

**Tool:** Codex

**Type:** commit

**Refined implementation prompt (AI-written):** Review, verify and commit the completed documentation, workflow and farmer-intake changes on the feature/intake-location branch.

**Purpose / AI contribution:** Execute the authorized inspection, local checks, commit, push and remote-ref verification.

**Human contribution:** Fardin authorized delivery and required unfinished review and scientific gates to remain visible.

**Changed files:** 105 project files in source revision 7f79196ba7f7b876ca017614c8cc574626a9be78; [delivery evidence](tasks/DELIVERY-INTAKE.json).

**Actual outcome:** Commit 7f79196 was created for 105 inspected project files after the local checks passed, with delivery metadata recorded in a separate follow-up commit. Independent review, browser and phone testing, and scientific acceptance remained pending.

**Review / limitations:** Git automation records delivery rather than additional human creative work or independent approval.

**Related context:** Shared delivery context for [FARDIN-009](#fardin-009); metadata was recorded separately without a self-referential hash.

**Task / source:** DELIVERY-INTAKE; Current Fardin commit-and-push instruction

## Fardin — Prompt 009

<a id="fardin-009"></a>
<a id="p-8321080ab708"></a>
<!-- record-id: P-8321080ab708 -->

**Date:** 2026-10-30

<!-- recorded-utc: 2026-10-30T16:43:10Z -->

**Member:** fardin

**Tool:** Codex

**Type:** push

**Refined implementation prompt (AI-written):** Push the feature/intake-location branch to origin with upstream tracking, while keeping unfinished review and scientific work marked as pending.

**Actual outcome:** Source commit 7f79196 was pushed to origin/feature/intake-location with upstream tracking, and the remote revision was verified. Delivery metadata followed separately; independent review, phone testing and scientific acceptance remained pending, with no force push, merge or deployment.

**Related context:** See [FARDIN-008](#fardin-008) for the shared AI purpose, human contribution, review limits and file evidence.

**Task / source:** DELIVERY-INTAKE; Current Fardin commit-and-push instruction

## Prachurjo — Prompt 001

<a id="prachurjo-001"></a>
<a id="p-5d643ba28c19"></a>
<!-- record-id: P-5d643ba28c19 -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T19:35:45Z -->

**Member:** prachurjo

**Tool:** Cursor

**Type:** implementation

**Refined implementation prompt (AI-written):** Refine the workspace intake and mobile interface, and record Prachurjo's independent UI review against the intake delivery tasks.

**Purpose / AI contribution:** Refine the workspace/mobile interface and record the explicitly requested UI review and delivery.

**Human contribution:** Prachurjo reported that the mounted UI was usable with no blocking frontend issues; that existing approval remains in the QA notes and task reviews.

**Changed files:** 12 files in source revision 0b27bd8d07cb878f101e8d1cac18d4b20bf652a1; [UI review](LOCATION_QA.md#prachurjo-independent-ui-review--2026-11-01), [INTAKE-UI](tasks/INTAKE-UI.json), [INTAKE-MAP](tasks/INTAKE-MAP.json) and [DELIVERY-INTAKE](tasks/DELIVERY-INTAKE.json).

**Actual outcome:** The QA notes and review records for INTAKE-UI, INTAKE-MAP and DELIVERY-INTAKE were updated. Lint, the production build, workflow validation and all 46 workflow tests passed; the tasks remained under review pending main-branch integration and scientific gates.

**Review / limitations:** The review did not document a separate physical-phone HTTPS session; accepted main-branch integration and scientific acceptance remained outstanding.

**Related context:** The commands were recorded on 31 October UTC; the Bangladesh UI review is dated 1 November. Shared context for [PRACHURJO-002](#prachurjo-002) and [PRACHURJO-003](#prachurjo-003); command metadata followed in a separate commit.

**Task / source:** DELIVERY-INTAKE; Current user: UI checked OK; update records; create branch; commit and push.

## Prachurjo — Prompt 002

<a id="prachurjo-002"></a>
<a id="p-8b49eea996ae"></a>
<!-- record-id: P-8b49eea996ae -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T19:35:45Z -->

**Member:** prachurjo

**Tool:** Cursor

**Type:** commit

**Refined implementation prompt (AI-written):** Commit the workspace interface improvements and Prachurjo's UI review records on the feature/workspace-ui-review branch.

**Actual outcome:** Commit 0b27bd8d07cb878f101e8d1cac18d4b20bf652a1 was created on feature/workspace-ui-review for 12 files. The refe/ directory was left untracked at that time, and the tasks remained under review.

**Related context:** See [PRACHURJO-001](#prachurjo-001) for the shared AI purpose, human contribution, review limits and file evidence.

**Task / source:** DELIVERY-INTAKE; Current user: UI checked OK; update records; create branch; commit and push.

## Prachurjo — Prompt 003

<a id="prachurjo-003"></a>
<a id="p-7c95b4a2d1f9"></a>
<!-- record-id: P-7c95b4a2d1f9 -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T19:35:45Z -->

**Member:** prachurjo

**Tool:** Cursor

**Type:** push

**Refined implementation prompt (AI-written):** Push the feature/workspace-ui-review branch to origin with upstream tracking.

**Actual outcome:** Commit 0b27bd8d07cb878f101e8d1cac18d4b20bf652a1 was pushed to origin/feature/workspace-ui-review, and the remote revision was verified. No force push, merge or deployment was performed.

**Related context:** See [PRACHURJO-001](#prachurjo-001) for the shared AI purpose, human contribution, review limits and file evidence.

**Task / source:** DELIVERY-INTAKE; Current user: UI checked OK; update records; create branch; commit and push.

## Fardin — Prompt 010

<a id="fardin-010"></a>
<a id="p-e9bf7acc4d6b"></a>
<!-- record-id: P-e9bf7acc4d6b -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T20:19:36Z -->

**Member:** fardin

**Tool:** OpenAI Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Rewrite existing AI-use and implementation-command records in clear, professional English, and apply the agreed Markdown format to future records.

**Purpose / AI contribution:** Refine records, add legacy-compatible Markdown reading/outcome updates and regression coverage, and align future instructions.

**Human contribution:** Fardin chose professional English interpretations of action requests and excluded raw transcripts and ordinary discussions.

**Changed files:** [Logger](../scripts/workflow.py), [tests](../tests/test_workflow.py), [agent rules](../AGENTS.md), [workflow instructions](WORKFLOW.md) and [OPS-PROMPT-STYLE](tasks/OPS-PROMPT-STYLE.json).

**Actual outcome:** Twelve historical entries and the AI-use disclosure were refined, and future logs now use the agreed Markdown format. All 52 workflow tests, metadata preservation, record and link validation, and whitespace checks passed; independent review is pending, and nothing was committed or pushed.

**Review / limitations:** The application and scientific pipeline were unchanged.

**Task / source:** OPS-PROMPT-STYLE; Fardin's current implementation instruction

## Fardin — Prompt 011

<a id="fardin-011"></a>
<a id="p-5ce01a4722d4"></a>
<!-- record-id: P-5ce01a4722d4 -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T20:45:44Z -->

**Member:** fardin

**Tool:** OpenAI Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Combine the AI-use explanations and implementation history into one compact file, preserving existing information and updating future logging.

**Purpose / AI contribution:** Consolidate duplicated disclosure and command information, and direct the helper to the same record file.

**Human contribution:** Fardin requested one combined information source, with additional sections where useful, rather than duplicated explanations in separate files.

**Changed files:** [Combined record](AI_USE.md), [logger](../scripts/workflow.py), [tests](../tests/test_workflow.py), [workflow rules](WORKFLOW.md) and linked task/reference updates.

**Before → After:** Five AI-use and prompt-history files become one canonical AI_USE.md with linked shared context.

**Actual outcome:** The five AI-use and prompt-history files were combined into AI_USE.md, preserving all 13 earlier records and their contribution context. All 56 workflow tests, metadata/context preservation, record/link validation and whitespace checks passed; independent review is pending, and no commit or push was performed.

**Review / limitations:** Independent review remains pending; no application or scientific acceptance is implied.

**Next action / owner:** A different teammate reviews the merged records and helper behavior after local verification.

**Task / source:** OPS-PROMPT-STYLE; Fardin's current consolidation instruction

## Fardin — Prompt 012

<a id="fardin-012"></a>
<a id="p-f0a4798379bd"></a>
<!-- record-id: P-f0a4798379bd -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T21:02:48Z -->

**Member:** fardin

**Tool:** OpenAI Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Identify each implementation record with the team member’s name and a sequential prompt number instead of an opaque public ID.

**Purpose / AI contribution:** Implement independent member counters, readable headings and stable lookups while preserving earlier references.

**Human contribution:** Fardin selected team-member names and prompt numbers as the visible record identifiers.

**Changed files:** [Combined record](AI_USE.md), [helper](../scripts/workflow.py), [tests](../tests/test_workflow.py), [instructions](WORKFLOW.md) and updated QA references.

**Before → After:** Opaque public record headings become member-name prompt headings with persistent per-member numbering.

**Actual outcome:** Existing headings now use member names and stable prompt numbers; PRACHURJO-002 identifies the requested entry. All 60 workflow tests, record/link validation, preservation and whitespace checks passed; legacy lookup aliases remain valid, independent review is pending, and no commit or push was performed.

**Review / limitations:** Independent review remains pending; historical dates, tools, outcomes and attribution are preserved.

**Next action / owner:** A different teammate reviews the numbered records and helper behavior.

**Task / source:** OPS-PROMPT-STYLE; Fardin's current prompt-numbering instruction

## Fardin — Prompt 013

<a id="fardin-013"></a>
<a id="p-df4c880516c8"></a>
<!-- record-id: P-df4c880516c8 -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T22:41:04Z -->

**Member:** fardin

**Tool:** Codex

**Type:** commit

**Refined implementation prompt (AI-written):** Commit all current documentation and workflow changes.

**Purpose / AI contribution:** Review the existing diff, run configured checks and commit the authorized working-tree changes.

**Human contribution:** Fardin authorized committing everything currently changed and pushing it.

**Changed files:** AGENTS.md, CLAUDE.md, README.md, docs/AI_USE.md, docs/WORKFLOW.md, QA references, affected task records, scripts/workflow.py, tests/test_workflow.py and retired split logs.

**Actual outcome:** All 60 workflow and contribution tests, record/link validation and whitespace checks passed. The changes are prepared for commit; independent teammate review remains pending.

**Review / limitations:** No human approval, main-branch merge or G0 acceptance is inferred.

**Next action / owner:** Commit the reviewed changes on feature/workspace-ui-review, then push and verify delivery.

**Task / source:** OPS-PROMPT-STYLE; Current explicit commit-everything-and-push instruction

## Fardin — Prompt 014

<a id="fardin-014"></a>
<a id="p-841a7bbf4884"></a>
<!-- record-id: P-841a7bbf4884 -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T22:41:09Z -->

**Member:** fardin

**Tool:** Codex

**Type:** push

**Refined implementation prompt (AI-written):** Push the committed current changes to the branch on origin.

**Purpose / AI contribution:** Deliver the authorized workflow consolidation without merging or accepting it.

**Actual outcome:** Push authorization is recorded for feature/workspace-ui-review. No push has been performed yet; the remote revision will be checked after delivery.

**Review / limitations:** Independent teammate review remains pending.

**Related context:** [FARDIN-013](#fardin-013) records the committed change scope and checks.

**Next action / owner:** Push without force and verify the remote branch revision.

**Task / source:** OPS-PROMPT-STYLE; Current explicit commit-everything-and-push instruction
<!-- workflow:ai-records:end -->
