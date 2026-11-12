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

**Actual outcome:** Committed all 18 reviewed documentation, workflow and test paths as 5beed23ccc3f8b9e418bb63cb1b7fc39da657a16. All 60 tests, record/link validation and whitespace checks passed; independent teammate review remains pending.

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

**Actual outcome:** Pushed 5beed23ccc3f8b9e418bb63cb1b7fc39da657a16 to origin/feature/workspace-ui-review and verified the exact remote SHA through GitHub. Automatic review initially rejected the push; retry succeeded after GitHub confirmed authenticated push permission. No merge or acceptance was performed.

**Review / limitations:** Independent teammate review remains pending.

**Related context:** [FARDIN-013](#fardin-013) records the committed change scope and checks.

**Next action / owner:** Push without force and verify the remote branch revision.

**Task / source:** OPS-PROMPT-STYLE; Current explicit commit-everything-and-push instruction

## Fardin — Prompt 015

<a id="fardin-015"></a>
<a id="p-6816c1e5bbeb"></a>
<!-- record-id: P-6816c1e5bbeb -->

**Date:** 2026-11-01

<!-- recorded-utc: 2026-10-31T22:45:30Z -->

**Member:** fardin

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Draft G0-CONTRACT s01 with the agreed coverage, intake, scheduling, comparison and evidence semantics, then validate, commit and push it for review.

**Purpose / AI contribution:** Prepare a concrete documentation-only API proposal and synthetic request/response examples while preserving the existing intake v2 implementation.

**Human contribution:** Fardin supplied the crop-audit targets, availability and scheduling decisions, four indicators and pending owner-review responsibilities.

**Changed files:** docs/API_CONTRACT.md, directly affected product/UI references, docs/tasks/G0-CONTRACT.json, generated README/progress and this contribution record.

**Actual outcome:** Delivered the checked s01 draft as c19d97dfe1b3999ef7998a7e053b2b64ef0b142d on origin/feature/g0-contract-draft; GitHub ref readback matched. Six synthetic JSON examples, v2 compatibility/invalid checks and all 60 workflow tests passed; teammate agreement remains pending, G0 stays in_progress and G1 remains gated.

**Review / limitations:** Saim, Maruf and Prachurjo reviews remain pending; G0 acceptance and G1 implementation remain gated.

**Next action / owner:** Fardin prepares and checks the s01 draft before authorized branch delivery.

**Task / source:** G0-CONTRACT; Current explicit G0-CONTRACT s01 draft and delivery instruction

## Saim — Prompt 001

<a id="saim-001"></a>
<a id="p-f231b8aa1983"></a>
<!-- record-id: P-f231b8aa1983 -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T19:45:01Z -->

**Member:** saim

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Create and validate a nationwide registry with one newly derived interior sampling point for each of Bangladesh's 64 districts, without downloading weather data or advancing G0.

**Purpose / AI contribution:** Inspect the pinned administrative assets; implement a deterministic offline point-on-surface generator and checker; document provenance, coordinate order, checksums, validation and limitations.

**Human contribution:** Saim set the 64-district scope, prohibited reuse of prior weather coordinates, authorized work independently of G0 and limited delivery to Step 1.

**Changed files:** data/climate/district_sampling_registry.csv; data/climate/district_sampling_manifest.json; docs/data/NATIONWIDE_SAMPLING.md; src/acquire/build_district_sampling_registry.py; src/acquire/README.md; docs/DATA_SOURCES.md

**Actual outcome:** The registry contains 64 unique complete rows; all 64 points are strict unique interiors and independently resolve to their assigned districts. Generation is byte-reproducible from the pinned geometry; no weather observations were downloaded, G0 was unchanged and human method/source review remains pending.

**Review / limitations:** Administrative geometry is simplified and has a 2020 represented-year versus as-of-2015 source-title discrepancy. One point is regional grid context, not a district average or farm measurement.

**Next action / owner:** An independent teammate should review the source provenance and sampling method before Step 2 weather collection.

**Task / source:** CLIMATE-SAMPLING; Current Saim Step 1 implementation instruction

## Saim — Prompt 002

<a id="saim-002"></a>
<a id="p-e85f784a5655"></a>
<!-- record-id: P-e85f784a5655 -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T20:21:42Z -->

**Member:** saim

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Build and verify a versioned NASA POWER configuration and resilient downloader with exactly four smoke requests, without starting the full 64-district historical collection or advancing G0.

**Purpose / AI contribution:** Verify official POWER parameters, units, availability and service restrictions; implement dry-run, structural validation, raw-byte preservation, retries, safe resume and synthetic tests; record live smoke evidence.

**Human contribution:** Saim set the 64-point 2001-2025 scope, required AG daily precipitation and temperature in explicit LST, limited live acquisition to two districts and two months, and prohibited full collection or G0 acceptance.

**Changed files:** data/climate/nasa_power_daily_v1.json; data/climate/nasa_power_smoke_test_manifest.json; src/acquire/download_nasa_power.py; tests/test_nasa_power_acquire.py; docs/data/NASA_POWER_ACQUISITION.md; src/acquire/README.md; cache/README.md; docs/DATA_SOURCES.md

**Actual outcome:** The 64-point configuration plans 1,600 annual requests. Seven synthetic tests and all four Bagerhat/Rangamati January 2001/2025 smoke requests passed exact date, parameter, unit, LST, fill and checksum validation; raw bytes remain in ignored cache. The full collection was not run, G0 was unchanged and human review remains pending.

**Review / limitations:** POWER documents at most five concurrent requests but no requests-per-second quota; the client uses one. Same-grid deduplication and full-period availability remain unresolved before the guarded full run.

**Next action / owner:** An independent teammate should review the POWER contract and same-grid strategy before authorizing the full command.

**Task / source:** CLIMATE-POWER-ACQUIRE; Current Saim Step 2 implementation instruction

## Saim — Prompt 003

<a id="saim-003"></a>
<a id="p-0472fd2ed2f7"></a>
<!-- record-id: P-0472fd2ed2f7 -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T20:34:24Z -->

**Member:** saim

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Resolve NASA POWER request redundancy with official evidence, then execute the full 64-district 2001-2025 collection only if a parameter-complete reuse method is defensible.

**Purpose / AI contribution:** Review official POWER grid/source/schema evidence, preserve smoke metadata, implement a checksum-bound execution gate, and generate a complete district-to-request dry-run plan and honest acquisition summary.

**Human contribution:** Saim authorized the full historical collection conditionally on a defensible reuse method, required all 64 district points and four parameters to remain traceable, and required the process to stop rather than guess grid equivalence.

**Changed files:** data/climate/nasa_power_request_reuse_v1.json; data/climate/nasa_power_full_acquisition_plan.json; data/climate/nasa_power_full_acquisition_summary.json; src/acquire/download_nasa_power.py; tests/test_nasa_power_acquire.py; docs/data/NASA_POWER_REDUNDANCY_REVIEW.md; docs/data/NASA_POWER_ACQUISITION.md; docs/DATA_SOURCES.md; src/acquire/README.md; docs/tasks/CLIMATE-POWER-FULL.json

**Before → After:** The downloader had a generic full-run confirmation flag but no evidence-bound same-grid decision; it now refuses full execution until an authoritative parameter-complete equivalence mapping is checked in.

**Actual outcome:** Official sources exposed no defensible point-to-cell equivalence key, so the exact full command stopped before network access. The plan records 1,600 pending logical chunks, zero safe reuses and zero full coverage; 10 targeted and 70 repository tests passed. The four smoke responses remain intact, G0 was unchanged and no commit or push occurred.

**Review / limitations:** The Daily API grid warning and meteorological native-resolution documentation differ, while OpenAPI v2.10.3 defines no cell identifier or snapping rule. Official clarification and independent review remain required.

**Next action / owner:** Saim or an independent reviewer should obtain official parameter-complete grid-equivalence guidance, update and review the checksum-bound mapping, then run the documented resume command.

**Task / source:** CLIMATE-POWER-FULL; Current Saim Step 3 implementation instruction

## Saim — Prompt 004

<a id="saim-004"></a>
<a id="p-8bf55dc1ea5a"></a>
<!-- record-id: P-8bf55dc1ea5a -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T20:42:28Z -->

**Member:** saim

**Tool:** Codex

**Type:** commit

**Refined implementation prompt (AI-written):** Commit the completed nationwide NASA POWER sampling and acquisition work on a new, relevant feature branch.

**Purpose / AI contribution:** Create a reviewable branch containing Saim Steps 1–3, their evidence, tests and safety gate without changing G0 or merging.

**Human contribution:** Saim explicitly authorized creating a new branch and committing the completed NASA/climate work with a relevant message.

**Changed files:** Nationwide climate registry, NASA POWER configuration/downloader, smoke and Step 3 plan evidence, tests, documentation and workflow records across the 22-file reviewed scope.

**Actual outcome:** Created feature/saim-nasa-power-nationwide and committed the reviewed 22-file scope as 77b623a798b28466897b807be6da4d753d6b29bb with message feat(climate): add nationwide NASA POWER acquisition workflow. The preserved package-lock stash was not changed; no merge or review acceptance was claimed.

**Review / limitations:** The task remains scientifically blocked on an authoritative POWER equivalence mapping, and independent review remains pending.

**Next action / owner:** Push the new commit to the same-named origin branch once repository write permission is available.

**Task / source:** CLIMATE-POWER-FULL; Current Saim branch, commit and push instruction

## Saim — Prompt 005

<a id="saim-005"></a>
<a id="p-2233c041e295"></a>
<!-- record-id: P-2233c041e295 -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T20:42:28Z -->

**Member:** saim

**Tool:** Codex

**Type:** push

**Refined implementation prompt (AI-written):** Push the committed nationwide NASA POWER work to the new feature branch on origin.

**Purpose / AI contribution:** Publish the reviewable climate branch without merging, deploying or changing G0.

**Human contribution:** Saim explicitly authorized pushing the newly committed branch.

**Actual outcome:** The push to origin/feature/saim-nasa-power-nationwide was attempted but GitHub returned HTTP 403: the active saim1sh credential lacks write permission to prachurjyo-ghub/soil-to-starts. No remote branch was created or falsely reported as delivered.

**Review / limitations:** A repository owner must grant saim1sh write access or provide an authorized writable remote; the local commit remains intact and ready to push.

**Next action / owner:** After access is granted, rerun git push -u origin feature/saim-nasa-power-nationwide and verify the remote SHA.

**Task / source:** CLIMATE-POWER-FULL; Current Saim branch, commit and push instruction

## Saim — Prompt 006

<a id="saim-006"></a>
<a id="p-a58322aad62e"></a>
<!-- record-id: P-a58322aad62e -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T21:07:06Z -->

**Member:** saim

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Evaluate and smoke-test NASA POWER Daily Regional acquisition as a separate alternative without changing the blocked Point API reuse decision or starting the full collection.

**Purpose / AI contribution:** Verify the official and live Regional contract, implement exact-byte resumable acquisition, test four parameters over a bounded Bangladesh area, and document a reproducible returned-coordinate extraction proposal.

**Human contribution:** Saim authorized Step 3B independently of G0, required at most four successful data requests, preserved original district points, prohibited native-cell claims and limited the outcome to a regional recommendation.

**Changed files:** data/climate/nasa_power_daily_regional_v1.json; data/climate/nasa_power_regional_smoke_test_manifest.json; src/acquire/download_nasa_power_regional.py; tests/test_nasa_power_regional_acquire.py; docs/data/NASA_POWER_REGIONAL_PROPOSAL.md; docs/data/NASA_POWER_REDUNDANCY_REVIEW.md; docs/DATA_SOURCES.md; src/acquire/README.md; cache/README.md; docs/tasks/CLIMATE-POWER-REGIONAL.json

**Before → After:** The repository had only a blocked point-based full plan; it now has a separate Regional API mode and bounded evidence while the Point execution gate remains unchanged.

**Actual outcome:** The live API required a minimum 2 degree by 2 degree box and rejected multiple parameters. Four sequential single-parameter responses each returned 12 coordinates and three LST dates with expected units and zero fills; exact output-coordinate alignment was observed, five regional tests and all 75 repository tests passed, and no full acquisition ran.

**Review / limitations:** Regional output nodes are not claimed as native cells or Point API equivalents. Nearest-node extraction changes the sampling method; national edge/size preflight and independent review remain required.

**Next action / owner:** A different teammate reviews the output-coordinate join, nearest-node distances and one-year national-extent preflight proposal before any historical execution.

**Task / source:** CLIMATE-POWER-REGIONAL; Current Saim Step 3B implementation instruction

## Saim — Prompt 007

<a id="saim-007"></a>
<a id="p-a68941c20ad8"></a>
<!-- record-id: P-a68941c20ad8 -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T21:09:43Z -->

**Member:** saim

**Tool:** Codex

**Type:** commit

**Refined implementation prompt (AI-written):** Commit the completed NASA POWER Regional Step 3B implementation and smoke-test evidence with the existing nationwide climate branch history.

**Purpose / AI contribution:** Package the separate Regional API client, bounded live evidence, tests and proposal for review without changing the blocked Point gate or G0.

**Human contribution:** Saim explicitly authorized retrying branch delivery for the nationwide NASA POWER steps.

**Changed files:** Regional configuration and smoke manifest, regional downloader and tests, acquisition proposal, source/cache documentation, task evidence and generated progress views.

**Actual outcome:** Committed the validated 13-file Step 3B scope as bf4e8bb2e786d27e0367f5e84dbfee0cf3521123 with message feat(climate): evaluate NASA POWER regional acquisition. The commit follows the existing Steps 1-3 branch history; no merge, review acceptance or G0 advancement was performed.

**Review / limitations:** The Regional task remains in_review and full historical collection still requires the documented method review and national-extent preflight.

**Next action / owner:** Push the feature branch and verify the exact remote SHA.

**Task / source:** CLIMATE-POWER-REGIONAL; Current Saim retry-push instruction

## Saim — Prompt 008

<a id="saim-008"></a>
<a id="p-64868289a1cc"></a>
<!-- record-id: P-64868289a1cc -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T21:09:43Z -->

**Member:** saim

**Tool:** Codex

**Type:** push

**Refined implementation prompt (AI-written):** Push the complete nationwide NASA POWER branch, including the Regional Step 3B evaluation, to origin.

**Purpose / AI contribution:** Publish the reviewable Steps 1-3B climate work without merging, deploying or changing scientific acceptance.

**Human contribution:** Saim explicitly requested another push attempt after repository access was corrected.

**Actual outcome:** Pushed feature/saim-nasa-power-nationwide to origin and set upstream tracking. GitHub ref readback matched bf4e8bb2e786d27e0367f5e84dbfee0cf3521123 exactly; no pull request, merge or acceptance was created.

**Review / limitations:** Remote branch delivery is verified, but independent scientific review and the Regional preflight blockers remain open.

**Next action / owner:** A teammate reviews the branch; do not run the full historical collection until the recorded Regional blockers are resolved.

**Task / source:** CLIMATE-POWER-REGIONAL; Current Saim retry-push instruction

## Saim — Prompt 009

<a id="saim-009"></a>
<a id="p-a5fffff987ce"></a>
<!-- record-id: P-a5fffff987ce -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T21:22:35Z -->

**Member:** saim

**Tool:** Codex

**Type:** implementation

**Refined implementation prompt (AI-written):** Run exactly one national-extent PRECTOTCORR Regional preflight for calendar year 2001, validate its cached response and revise the full-acquisition proposal without selecting district extraction.

**Purpose / AI contribution:** Measure annual national JSON size and timing, verify spatial/date/value QA and edge coverage, add network-forbidden resume validation, and keep raw Regional coverage separate from unresolved district-derived coverage.

**Human contribution:** Saim authorized one bounded national-area annual request, selected PRECTOTCORR/AG/LST, prohibited nearest-node approval and limited work to the preflight and recommendation.

**Changed files:** data/climate/nasa_power_regional_preflight_2001_manifest.json; docs/data/NASA_POWER_REGIONAL_PREFLIGHT_2001.md; docs/data/NASA_POWER_REGIONAL_PROPOSAL.md; src/acquire/download_nasa_power_regional.py; tests/test_nasa_power_regional_acquire.py; cache/README.md; src/acquire/README.md; docs/DATA_SOURCES.md; docs/tasks/CLIMATE-POWER-REGIONAL-PREFLIGHT.json

**Before → After:** The Regional route had only a three-day smoke test; it now has one validated annual national PRECTOTCORR response and a no-network reproducible cache audit, without district extraction.

**Actual outcome:** One JSON request returned 823,232 bytes in 2.865375 seconds with 140 unique coordinates, 365 complete dates per coordinate, 51,100 values, zero fills or unexpected numeric types and all 64 sampling points within the returned extent. Cached validation, six regional tests and all 76 repository tests passed; no other year or parameter was downloaded.

**Review / limitations:** The 100-request storage/time figures are linear estimates from one observed parameter-year. District extraction, cross-parameter national alignment and scientific review remain unresolved; G0 was unchanged.

**Next action / owner:** A different teammate reviews the preflight evidence before authorizing any multi-year or multi-parameter Regional collection.

**Task / source:** CLIMATE-POWER-REGIONAL-PREFLIGHT; Current Saim Step 3C implementation instruction

## Saim — Prompt 010

<a id="saim-010"></a>
<a id="p-9bea875d53aa"></a>
<!-- record-id: P-9bea875d53aa -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T21:28:24Z -->

**Member:** saim

**Tool:** Codex

**Type:** commit

**Refined implementation prompt (AI-written):** Commit the completed NASA POWER national Regional preflight on the existing nationwide climate feature branch.

**Purpose / AI contribution:** Package the Step 3C acquisition code, bounded live evidence, QA tests and proposal for teammate review without changing G0 or scientific acceptance.

**Human contribution:** Saim explicitly authorized committing the completed Step 3C work while remaining on the existing feature branch.

**Changed files:** National Regional preflight manifest and report, regional downloader and tests, acquisition/source/cache documentation, task evidence and generated workflow views.

**Actual outcome:** Committed the validated 12-file Step 3C scope as e94b566e0aa762636cf3775115f327e9b560ebe5 with message feat(climate): validate annual regional preflight. No merge, review acceptance or G0 advancement was performed.

**Review / limitations:** CLIMATE-POWER-REGIONAL-PREFLIGHT remains in_review; district extraction and cross-parameter national alignment remain unresolved.

**Next action / owner:** Push the same feature branch and verify the remote SHA.

**Task / source:** CLIMATE-POWER-REGIONAL-PREFLIGHT; Current Saim commit and push instruction

## Saim — Prompt 011

<a id="saim-011"></a>
<a id="p-4b4352a1d502"></a>
<!-- record-id: P-4b4352a1d502 -->

**Date:** 2026-11-13

<!-- recorded-utc: 2026-11-12T21:28:24Z -->

**Member:** saim

**Tool:** Codex

**Type:** push

**Refined implementation prompt (AI-written):** Push the NASA POWER Step 3C preflight commit to the existing nationwide climate feature branch on origin.

**Purpose / AI contribution:** Publish the reviewable preflight implementation and evidence without creating another branch, merging or changing scientific acceptance.

**Human contribution:** Saim explicitly authorized pushing while staying on feature/saim-nasa-power-nationwide.

**Changed files:** Existing feature branch containing commit e94b566e0aa762636cf3775115f327e9b560ebe5.

**Actual outcome:** Pushed feature/saim-nasa-power-nationwide to origin and verified the remote ref exactly matched e94b566e0aa762636cf3775115f327e9b560ebe5. No pull request, merge, deployment or acceptance was created.

**Review / limitations:** The branch is delivered for independent review; the full historical Regional collection remains unstarted.

**Next action / owner:** A teammate reviews the preflight evidence and unresolved extraction/alignment decisions before any broader acquisition authorization.

**Task / source:** CLIMATE-POWER-REGIONAL-PREFLIGHT; Current Saim commit and push instruction
<!-- workflow:ai-records:end -->
