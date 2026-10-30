# Team task board

Generated from `docs/tasks/*.json`; update a record or use the helper, then render. This is the single human-readable list of owners, small steps, errors, evidence and handoffs.

**Read this way:** choose your next available work package, follow its small checklist items in order, record errors and real evidence, then hand it off. A checked checklist item means that output is implemented/observed locally. A checked work-package row means passing checks, independent review and an accepted main-branch commit. Neither means national scientific validation.

[Team playbook](TEAM_PLAYBOOK.md) · [Command reference](WORKFLOW.md) · [Validation requirements](VALIDATION.md)

**Accepted tasks: 0/29. Tasks with recorded failing checks: 0.** Counts are task records, not product-completion percentages.

| Done | Task | Owner | State | Depends on | Next action |
| --- | --- | --- | --- | --- | --- |
| [ ] | [DELIVERY-INTAKE](tasks/DELIVERY-INTAKE.json): Verify, commit and push the intake-location feature delivery | Fardin | in_review | none | Prachurjo independently reviews the delivered feature branch and performs pending browser/physical-phone checks; Fardin coordinates later accepted G0/scientific work. |
| [ ] | [DOC-FOUNDATION](tasks/DOC-FOUNDATION.json): Team onboarding and root execution rules | Fardin | in_review | none | Arrange a teammate review of the concise onboarding and canonical specifications; record accepted merge only afterward. |
| [ ] | [OPS-LICENSE](tasks/OPS-LICENSE.json): Choose license and complete source/asset rights review | Fardin | blocked | none | Nadim/Prachurjo resolve exact font/media rights; Fardin records release review. This does not block G0 drafting. |
| [ ] | [OPS-LINT](tasks/OPS-LINT.json): Configure frontend ESLint and verify it | Prachurjo | in_review | none | Review the bounded lint/state-initialization changes and record accepted delivery; full usability testing remains G3. |
| [ ] | [OPS-SECURITY](tasks/OPS-SECURITY.json): Verify and patch the Next.js security advisory | Fardin | in_review | none | Prachurjo reviews the targeted patch; Fardin records actual main-branch delivery only after approval. |
| [ ] | [OPS-WORKFLOW](tasks/OPS-WORKFLOW.json): Prompt logging and evidence-based progress tracking | Fardin | in_review | none | Request independent review of the board/helper/PR checks; publish only when authorized. |
| [ ] | [PLAN-SCOPE](tasks/PLAN-SCOPE.json): Document strengthened mandatory MVP and gated future roadmap | Fardin | in_review | none | Arrange independent teammate review of the scope changes. Fardin can draft G0 contracts while that review is pending; no product work is accepted by these documentation ticks. |
| [ ] | [G0-CONTRACT](tasks/G0-CONTRACT.json): Agree source, crop, field and API contracts | Fardin | ready | none | Draft bounded contracts and obtain agreement from Saim, Maruf and Prachurjo. |
| [ ] | [MEDIA-STORY](tasks/MEDIA-STORY.json): Draft factual story, claims checklist and presentation outline | Hla | ready | none | Draft story and mark every unverified claim; final narration waits for actual app evidence. |
| [ ] | [MEDIA-STORYBOARD](tasks/MEDIA-STORYBOARD.json): Prepare storyboard, capture plan and asset ledger | Nadim | ready | none | Draft storyboard and rights ledger with Hla; defer final footage to accepted app behavior. |
| [ ] | [INTAKE-MAP](tasks/INTAKE-MAP.json): Add independent confirmed map-pin and district-search intake locations | Fardin | in_review | none | Prachurjo independently verifies both full browser submissions, real WebGL/worker/tile and touch behavior, phone layout and persistence; Fardin coordinates later G0/API integration. |
| [ ] | [INTAKE-UI](tasks/INTAKE-UI.json): Implement nationwide required farmer intake without scientific recommendations | Fardin | in_review | none | Prachurjo independently reviews both location methods and all six questions, including full browser submissions, persistence and physical-phone behavior; Fardin coordinates accepted contracts/API later. |
| [ ] | [G1A](tasks/G1A.json): Acquire and validate the first NASA POWER evidence sample | Saim | waiting | G0-CONTRACT | Review G0 contracts now; acquire the first evidence slice after G0 is accepted. |
| [ ] | [G1B](tasks/G1B.json): Source Bangladesh crop, soil and rotation rules | Maruf | waiting | G0-CONTRACT | Review G0 rules/schema now; source the minimum crop catalog after G0 is accepted. |
| [ ] | [G1C](tasks/G1C.json): Implement API validation and schema/test foundation | Fardin | waiting | G0-CONTRACT | Implement schema/API validation after G0 acceptance; coordinate independent tooling work. |
| [ ] | [G1D](tasks/G1D.json): Extend required farmer intake and API/error-state shell | Prachurjo | waiting | G0-CONTRACT | Extend the current app against accepted G0 contracts; do not create a second frontend. |
| [ ] | [G2](tasks/G2.json): Deliver the sourced baseline/alternatives engine and API | Fardin | waiting | G1A, G1B, G1C | Wait for accepted G1 evidence, rules and API contracts; then integrate one vertical slice. |
| [ ] | [G3](tasks/G3.json): Connect actual scientific outputs to the existing frontend | Prachurjo | waiting | G2, G1D, OPS-LINT | Integrate only after G2/G1D acceptance and the lint blocker is resolved. |
| [ ] | [G3-REPORT](tasks/G3-REPORT.json): Deliver the reproducible print and JSON receipt | Prachurjo | waiting | G3 | Preserve result and evidence identities |
| [ ] | [G3-STORY](tasks/G3-STORY.json): Add the compact verified climate story | Prachurjo | waiting | G3 | Agree four scenes and source-backed captions |
| [ ] | [G4](tasks/G4.json): Validate historical comparison, uncertainty and offline science | Fardin | waiting | G3, G3-STORY, G3-REPORT | Wait for accepted G3, G3-STORY and G3-REPORT; then implement and validate the historical replay, pilot limits and offline science. |
| [ ] | [G5](tasks/G5.json): Release the reviewed MVP and prepare submission handoff | Fardin | waiting | G4, OPS-LICENSE, MEDIA-STORY, MEDIA-STORYBOARD | Wait for accepted evidence and rights gates; verify portal requirements before freeze. |
| [ ] | [FUT-ASSIST](tasks/FUT-ASSIST.json): Evaluate optional sourced runtime assistance | Fardin | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |
| [ ] | [FUT-COVERAGE](tasks/FUT-COVERAGE.json): Expand reviewed regions, crops and long-duration paths | Maruf | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |
| [ ] | [FUT-DATA](tasks/FUT-DATA.json): Add decision-relevant NASA sources and overlays | Saim | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |
| [ ] | [FUT-EXPERIENCE](tasks/FUT-EXPERIENCE.json): Extend motion, voice, saved plans and browser offline UX | Prachurjo | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |
| [ ] | [FUT-OPERATIONS](tasks/FUT-OPERATIONS.json): Evaluate a selected account, market, sensor or alert service | Fardin | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |
| [ ] | [FUT-SCENARIOS](tasks/FUT-SCENARIOS.json): Extend stress exploration and qualified projections | Fardin | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |
| [ ] | [FUT-SOIL](tasks/FUT-SOIL.json): Research optional fertilizer and richer soil modeling | Maruf | waiting | G5 | Do not start now. After accepted G5, select and explicitly authorize one bounded extension; then resolve the activation blocker. |

### Next action by member

| Member | Available now / next dependency |
| --- | --- |
| Fardin | DELIVERY-INTAKE: Prachurjo independently reviews the delivered feature branch and performs pending browser/physical-phone checks; Fardin coordinates later accepted G0/scientific work.; DOC-FOUNDATION: Arrange a teammate review of the concise onboarding and canonical specifications; record accepted merge only afterward.; OPS-SECURITY: Prachurjo reviews the targeted patch; Fardin records actual main-branch delivery only after approval.; OPS-WORKFLOW: Request independent review of the board/helper/PR checks; publish only when authorized.; PLAN-SCOPE: Arrange independent teammate review of the scope changes. Fardin can draft G0 contracts while that review is pending; no product work is accepted by these documentation ticks.; G0-CONTRACT: Draft bounded contracts and obtain agreement from Saim, Maruf and Prachurjo.; INTAKE-MAP: Prachurjo independently verifies both full browser submissions, real WebGL/worker/tile and touch behavior, phone layout and persistence; Fardin coordinates later G0/API integration.; INTAKE-UI: Prachurjo independently reviews both location methods and all six questions, including full browser submissions, persistence and physical-phone behavior; Fardin coordinates accepted contracts/API later. |
| Saim | Collaborate on G0-CONTRACT |
| Maruf | Collaborate on G0-CONTRACT |
| Prachurjo | OPS-LINT: Review the bounded lint/state-initialization changes and record accepted delivery; full usability testing remains G3.; Collaborate on G0-CONTRACT, MEDIA-STORYBOARD |
| Nadim | MEDIA-STORYBOARD: Draft storyboard and rights ledger with Hla; defer final footage to accepted app behavior.; Collaborate on MEDIA-STORY |
| Hla | MEDIA-STORY: Draft story and mark every unverified claim; final narration waits for actual app evidence.; Collaborate on MEDIA-STORYBOARD |

## Acceptance, checks, bugs and handoffs

### DELIVERY-INTAKE — Verify, commit and push the intake-location feature delivery

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Fardin explicitly authorized branch creation, committing and pushing the completed documentation/workflow/intake/location work, including supporting check configuration. This delivery does not require or grant scientific, review or main-branch acceptance.

- [x] **a1 · Fardin · done:** Review intended documentation, workflow, intake, map and supporting check files; preserve unrelated work.
  - How: Inspect the actual diffs, source/task/license evidence and a fixed explicit path manifest; stage only reviewed project files.
  - Files: docs/, prototype/, scripts/, tests/, data/admin/, .github/
  - Verify: All staged paths belong to this delivery; build/cache/credentials are excluded and any unrelated changes remain untouched.
  - Evidence: Reviewed and explicitly staged all 105 intended documentation/workflow/intake/map/supporting-check files (~3 MB). Staged paths exactly match the reviewed manifest, caches are excluded and historical unassigned logs are unchanged. No unrelated working-tree paths were found.
- [x] **a2 · Fardin · done:** Pass delivery checks and inspect the staged changes before creating scoped commits.
  - How: Run intake/location, workflow, validation, syntax, lint, build and diff checks; inspect the staged diff and create descriptive commits.
  - Files: docs/tasks/DELIVERY-INTAKE.json, docs/prompt_logs/fardin-0001.md
  - Verify: Actual check outputs and actual commit hashes are recorded, without self-referential commit identities or invented review.
  - Before: a1
  - Evidence: Created source commit 7f79196ba7f7b876ca017614c8cc574626a9be78 after reviewing the 105-path staged diff. All required local checks passed. The source commit includes completed docs/workflow, intake/location, licensed assets/tests and supporting lint/security changes; no approval/scientific validation inferred.
- [x] **a3 · Fardin · done:** Push the authorized feature branch and verify the remote revision without accepting review/science gates.
  - How: Push without force to the requested origin branch and verify its advertised revision and upstream tracking.
  - Files: docs/tasks/DELIVERY-INTAKE.json, docs/prompt_logs/fardin-0001.md
  - Verify: Remote ref matches the pushed commit; tasks remain in_review and physical-phone/Prachurjo review stays pending.
  - Before: a2
  - Evidence: git push --set-upstream origin feature/intake-location succeeded. Independent git ls-remote readback advertised 7f79196ba7f7b876ca017614c8cc574626a9be78 for refs/heads/feature/intake-location. No force push, merge or deployment; independent review and physical-phone/browser testing remain pending.
- Check **passed**: `npm run test:intake` — 31 intake/location tests passed. summary (1.67975ms) ✔ English/Bangla render keeps IDs unchanged and escapes restored user text (0.715ms) ✔ actual UI submit handler requires pin confirmation and supports either method without stale data (10.521958ms) ✔ pinned source/license/checksums and all 64 exact boundary mappings agree (10.876042ms) ✔ Polygon, holes, MultiPolygon and numerical border handling (0.179584ms) ✔ outside, unresolved holes/gaps, overlap and shared borders never snap to a district (0.182458ms) ✔ invalid, non-finite and reversed longitude/latitude inputs are rejected (0.121166ms) ✔ 64 independent source-derived interiors resolve and normalize to their explicit district IDs (16.62825ms) ✔ new/moved pin needs confirmation and stale district, source version or geometry cannot pass (0.641042ms) ✔ method switching clears inactive coordinates/districts and district search needs no boundaries (0.152833ms) ✔ genuine v1 district answers migrate to v2 without coordinates or demo defaults (0.344417ms) ✔ boundary loader rejects missing/duplicate mappings and unsupported or broken rings (12.659125ms) ✔ map rerenders reuse one instance/listeners and preserve pin/answers; leaving removes resources (16.5455ms) ✔ WebGL and boundary-network failure retain answers and leave district fallback independent (7.887667ms) ✔ tile errors and lost WebGL context surface fallback without destroying other answers (8.887459ms) ℹ tests 31 ℹ suites 0 ℹ pass 31 ℹ fail 0 ℹ cancelled 0 ℹ skipped 0 ℹ todo 0 ℹ duration_ms 218.883167
- Check **passed**: `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` — 46 workflow/contribution tests passed. st_workflow.WorkflowTests) ... ok test_member_logs_are_separate_and_pipe_safe (test_workflow.WorkflowTests) ... ok test_passing_check_does_not_automatically_accept_task (test_workflow.WorkflowTests) ... ok test_pending_or_self_review_cannot_be_done (test_workflow.WorkflowTests) ... ok test_professional_docs_have_small_entrypoint_budgets (test_workflow.WorkflowTests) ... ok test_prompt_amend_updates_outcome_without_extra_entry (test_workflow.WorkflowTests) ... ok test_prompt_rotation_at_fifty (test_workflow.WorkflowTests) ... ok test_readonly_check_detects_stale_view (test_workflow.WorkflowTests) ... ok test_real_git_ancestry_proof (test_workflow.WorkflowTests) ... ok test_render_is_idempotent (test_workflow.WorkflowTests) ... ok test_reopening_checklist_prerequisite_reopens_done_children (test_workflow.WorkflowTests) ... ok test_start_blocked_task_does_not_modify_records (test_workflow.WorkflowTests) ... ok test_unchecked_acceptance_cannot_be_done (test_workflow.WorkflowTests) ... ok test_unknown_dependency_rejected (test_workflow.WorkflowTests) ... ok test_unmerged_commit_cannot_be_done (test_workflow.WorkflowTests) ... ok test_verify_accepts_explicit_project_subdirectory (test_workflow.WorkflowTests) ... ok test_verify_executes_check_and_records_real_failure (test_workflow.WorkflowTests) ... ok test_verify_refuses_directory_outside_project (test_workflow.WorkflowTests) ... ok ---------------------------------------------------------------------- Ran 46 tests in 0.379s OK
- Check **passed**: `python3 scripts/workflow.py check` — Records and generated views valid. Workflow records valid: 29 tasks, 9 prompts. Recorded failed product checks remain visible; this is not a product test pass.
- Check **passed**: `git diff --check` — No whitespace errors.
- Check **passed**: `npm run lint -- --no-cache` — Exit 0.
- Check **passed**: `npm run build -- --webpack` — Exit 0. ✓ Compiled successfully in 665ms Running TypeScript ... Finished TypeScript in 1ms ... Collecting page data using 5 workers ... Generating static pages using 5 workers (0/4) ... Generating static pages using 5 workers (1/4) Generating static pages using 5 workers (2/4) Generating static pages using 5 workers (3/4) ✓ Generating static pages using 5 workers (4/4) in 293ms Finalizing page optimization ... Collecting build traces ... Route (app) ┌ ○ / ├ ○ /_not-found └ ○ /workspace ○ (Static) prerendered as static content
- Check **passed**: `node --check prototype/public/reference/location.js` — Exit 0; executed by the delivery syntax-check loop.
- Check **passed**: `node --check prototype/public/reference/intake-map.js` — Exit 0; executed by the delivery syntax-check loop.
- Check **passed**: `node --check prototype/public/reference/intake.js` — Exit 0; executed by the delivery syntax-check loop.
- Check **passed**: `node --check prototype/public/reference/intake-ui.js` — Exit 0; executed by the delivery syntax-check loop.
- Check **passed**: `node --check prototype/public/reference/workspace.js` — Exit 0; executed by the delivery syntax-check loop.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: Prachurjo reviews the feature branch, completes both browser/phone location submissions and confirms usability; Fardin coordinates later accepted G0/API/science gates. Pushes are delivery only, not approval.

### DOC-FOUNDATION — Team onboarding and root execution rules

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Give every teammate accurate onboarding and preserve shared rules without loading them all for every task.

- [x] **s01 · Fardin · done:** Keep root instructions concise
  - How: Route agents to the assigned task and relevant specifications; preserve all hard product/science rules.
  - Files: AGENTS.md
  - Verify: Root stays under 800 words and source/module boundaries remain explicit.
  - Evidence: Root AGENTS is 764 words with scope routing and hard science/offline/authorization rules; README remains below its configured word budget.
- [x] **s02 · Fardin · done:** Provide a working quick start
  - How: Document only actual frontend/helper commands and current implementation limits.
  - Files: README.md, Makefile, scripts/doctor.py
  - Verify: A teammate can follow the commands; no backend capability is invented.
  - Before: s01
  - Evidence: README.md, Makefile and read-only doctor exist; doctor passed on Python 3.9.6/Node 26.12.1/npm 12.2.1.
- [x] **s03 · Fardin · done:** Publish the detailed team and product rules
  - How: Move full product, UI, source, validation, contribution and submission requirements into linked canonical documents.
  - Files: docs/TEAM_PLAYBOOK.md, docs/PRODUCT_SPEC.md, docs/UI_UX_SPEC.md, docs/VALIDATION.md
  - Verify: All six roles, future/MVP scope, evidence and handoff requirements remain present.
  - Before: s02
  - Evidence: Canonical product/UI/API/team/validation/source/submission specifications now link the mandatory-now and future-only contexts.
- [x] **s04 · Fardin · done:** Validate onboarding and request independent review
  - How: Run diagnostics, record/link validation and helper tests, then obtain another member review.
  - Files: docs/PROGRESS.md, docs/WORKFLOW.md
  - Verify: Checks are recorded; local implementation is distinguished from human approval.
  - Before: s03
  - Evidence: 46 helper tests, record/link validation, lint and production build pass locally; independent review is pending.
- Check **passed**: `python3 scripts/doctor.py` — Local prerequisite/path checks passed; science/API status remains planned.
- Check **passed**: `python3 scripts/workflow.py check` — Task, log, generated view and relative-link validation passed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: All six members use the board/playbook; Fardin coordinates G0 contract drafting after reading the specifications.

### OPS-LICENSE — Choose license and complete source/asset rights review

Owner: **Fardin** · State: `blocked` · Updated UTC: `2026-10-29T17:25:20Z`

**Why:** Keep original code and third-party material suitable for public reuse and a rights-reviewed submission.

- [x] **s01 · Fardin · done:** Add the planned code license
  - How: Use the official Apache-2.0 text for original team-owned code/documentation.
  - Files: LICENSE
  - Verify: License text matches the official distribution; external assets retain their own terms.
  - Evidence: Official Apache-2.0 text added for original team-owned code/documentation; third-party terms remain separate.
- [x] **s02 · Fardin · done:** Inventory third-party material
  - How: List dependencies, photo/video/font/cursor sources and current rights status.
  - Files: THIRD_PARTY_NOTICES.md
  - Verify: Every known asset category has a review action; no blanket clearance is claimed.
  - Before: s01
  - Evidence: THIRD_PARTY_NOTICES.md inventories dependencies, media, fonts, cursor and future datasets; exact asset clearance remains pending.
- [ ] **s03 · Fardin · blocked:** Resolve rights and obtain release sign-off
  - How: Nadim/Prachurjo identify font/media licenses and Fardin records reviewer approval before submission.
  - Files: THIRD_PARTY_NOTICES.md, prototype/public/reference/assets/credits.txt
  - Verify: Exact licenses, redistribution permissions and unresolved items are documented.
  - Before: s02
  - Error/blocker: Font/media license and redistribution clearance has not been supplied.
- **Blocker:** Exact font/media reuse and redistribution clearance is still pending.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Nadim/Prachurjo supply exact media/font rights; Fardin records clearance before G5.

### OPS-LINT — Configure frontend ESLint and verify it

Owner: **Prachurjo** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Make frontend checks reproducible and expose real code problems before integration.

- [x] **s01 · Prachurjo · done:** Configure Next.js flat ESLint
  - How: Use the installed Next.js ESLint config and preserve static reference assets with documented narrow exceptions.
  - Files: prototype/eslint.config.mjs
  - Verify: ESLint finds its configuration and checks maintained application source.
  - Evidence: ESLint flat config uses the matching installed Next.js config, with narrow documented reference-page/static-asset exceptions.
- [x] **s02 · Prachurjo · done:** Fix client-state initialization errors
  - How: Synchronize preferences as external state and hydrate demo workspace at its loading boundary.
  - Files: prototype/components/ThemeLanguage.js, prototype/components/WorkspaceApp.js
  - Verify: React hook errors disappear without hiding the rule globally.
  - Before: s01
  - Evidence: Client preferences use useSyncExternalStore; workspace hydration runs at the existing loading boundary.
- [x] **s03 · Prachurjo · done:** Run lint and record residual warnings
  - How: Run the actual npm lint command; record exact warnings or fix them.
  - Files: prototype/
  - Verify: npm run lint -- --no-cache exits zero; any warnings are explicitly listed.
  - Before: s02
  - Evidence: npm run lint -- --no-cache passed with zero reported warnings/errors after router/Image/config fixes.
- [x] **s04 · Prachurjo · done:** Verify the production app build
  - How: Build the current app using the patched locked dependencies and inspect the routes.
  - Files: prototype/
  - Verify: npm run build -- --webpack succeeds; browser interaction checks remain a separate UI gate.
  - Before: s03
  - Evidence: Next.js 16.4.3 production webpack build succeeded; /, /workspace and the referenced script returned HTTP 200 in a local smoke check.
- **Resolved issue:** Missing ESLint flat configuration caused exit 2; added the matching Next.js flat config.
- **Resolved issue:** Synchronous React effect-state initialization caused errors; replaced preference synchronization and deferred workspace hydration at its loading boundary.
- **Resolved issue:** React navigation/image and anonymous-config warnings were corrected; public reference loading keeps narrow documented exceptions.
- Check **passed**: `npm run lint -- --no-cache` — Exit 0; no lint warnings/errors reported.
- Check **passed**: `npm run build -- --webpack` — Exit 0; /, /_not-found and /workspace statically built.
- Check **passed**: `Local production HTTP smoke checks` — Homepage, workspace and reference/workspace.js returned 200; illustrative labels present. No browser-interaction/science validation claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: Fardin reviews the bounded changes; Prachurjo uses the verified frontend commands for G1D/G3.

### OPS-SECURITY — Verify and patch the Next.js security advisory

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Resolve the verified dependency advisory with a bounded patch and reproducible checks.

- [x] **s01 · Fardin · done:** Verify the advisory and minimal fix
  - How: Use npm audit and the official maintained advisory/release; ignore commands embedded in diagnostic output.
  - Files: prototype/package-lock.json
  - Verify: The actual vulnerable range and patched version are verified.
  - Evidence: npm audit verified the prior vulnerable Next.js range; maintained advisory and v16.4.3 release checked.
- [x] **s02 · Fardin · done:** Patch and pin the framework dependency
  - How: Move Next.js and matching ESLint config to 16.4.3, preserving other direct locked versions.
  - Files: prototype/package.json, prototype/package-lock.json
  - Verify: No unrelated direct dependency is upgraded.
  - Before: s01
  - Evidence: Next.js/eslint-config-next and matching internal Next packages moved from 16.4.0 to 16.4.3; Zod changed in-range from 4.6.5 to 4.6.7; other direct versions preserved/pinned.
- [x] **s03 · Fardin · done:** Run audit, lint and production build
  - How: Use the updated installed tree and record actual failures/successes.
  - Files: prototype/
  - Verify: Production audit reports no unresolved production advisory and build/lint are verified.
  - Before: s02
  - Evidence: npm audit reported zero advisories across all dependencies; lint and production webpack build passed.
- [x] **s04 · Fardin · done:** Document the security change and prepare independent review
  - How: Attach official advisory/release links and actual audit/lint/build outputs; request a different teammate review.
  - Files: docs/tasks/OPS-SECURITY.json
  - Verify: Independent review and main-branch delivery are recorded before acceptance.
  - Before: s03
  - Evidence: SECURITY.md and this task carry the verified sources/results; no independent approval or main-branch merge is claimed.
- **Resolved issue:** Next.js 16.4.0 advisories resolved with the verified 16.4.3 patch and matching internal/config packages.
- **Resolved issue:** Zod development dependency moved in-range from 4.6.5 to 4.6.7; final npm audit reported zero advisories.
- Check **passed**: `npm audit --json --package-lock-only` — Exit 0; info/low/moderate/high/critical counts all zero at this check.
- Check **passed**: `npm run lint -- --no-cache` — Exit 0; no lint warnings/errors.
- Check **passed**: `npm run build -- --webpack` — Exit 0 on Next.js 16.4.3.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: Prachurjo reviews the patch; Fardin records accepted delivery. No deployment or scientific approval is inferred.

### OPS-WORKFLOW — Prompt logging and evidence-based progress tracking

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Keep actual work, dependencies, errors and next actions understandable across manual and AI-assisted contributors.

- [x] **s01 · Fardin · done:** Provide detailed ordered checklist items
  - How: Each small item has an owner, prerequisites, how-to, files, verification and explicit errors/evidence.
  - Files: docs/tasks/, scripts/workflow.py
  - Verify: Checklist state and dependencies validate; false completion is rejected.
  - Evidence: 125 ordered items across 26 packages include explicit owners/how/files/verification/dependencies/evidence; seven future tracks retain activation blockers.
- [x] **s02 · Fardin · done:** Generate one human-readable team board
  - How: Keep detailed steps on PROGRESS and a short member/next-action summary on README.
  - Files: docs/PROGRESS.md, README.md
  - Verify: Regeneration is deterministic and current next actions reflect actual prerequisites.
  - Before: s01
  - Evidence: README summary and detailed PROGRESS board are generated; focused member/task commands and checklist updates exist.
- [x] **s03 · Fardin · done:** Keep command logs action-only
  - How: Require implementation/commit/push kind; exclude discussion and preserve short batches.
  - Files: docs/PROMPT_LOG.md, docs/prompt_logs/
  - Verify: Discussion calls fail without writes; 50-entry rollover and amendments pass tests.
  - Before: s02
  - Evidence: Command-only classification, discussion rejection, batch rollover and outcome amendment tests pass.
- [x] **s04 · Fardin · done:** Support tool-neutral contribution handoffs
  - How: Use a three-field PR declaration and observed GitHub account evidence; never infer AI tools or human names.
  - Files: .github/pull_request_template.md, scripts/verify_pr.py, docs/team.json
  - Verify: Manual and AI declarations validate; unmapped identity remains unconfirmed.
  - Before: s03
  - Evidence: Three-field PR template, event verifier and six-member unconfirmed registry exist; account/tool/approval inference is rejected by tests.
- [x] **s05 · Fardin · done:** Test the workflow and hand it off
  - How: Run all helper tests and record/link checks; document local/remote CI and review limits.
  - Files: tests/, .github/workflows/workflow-records.yml
  - Verify: Tests pass; independent review/main-branch delivery remain explicit.
  - Before: s04
  - Evidence: 46 helper tests pass; local checks are recorded. Remote CI and human review have not run.
- Check **passed**: `python3 -B -m unittest discover -s tests -p test_workflow.py -v` — Exit 0. ow.WorkflowTests) ... ok test_cycle_rejected (test_workflow.WorkflowTests) ... ok test_dependency_regression_reopens_active_and_done_consumers (test_workflow.WorkflowTests) ... ok test_discussion_categories_are_rejected_without_writes (test_workflow.WorkflowTests) ... ok test_failed_or_unrun_checks_cannot_be_done (test_workflow.WorkflowTests) ... ok test_log_refuses_long_or_multiline_summary (test_workflow.WorkflowTests) ... ok test_manual_active_status_cannot_bypass_dependencies (test_workflow.WorkflowTests) ... ok test_member_logs_are_separate_and_pipe_safe (test_workflow.WorkflowTests) ... ok test_passing_check_does_not_automatically_accept_task (test_workflow.WorkflowTests) ... ok test_pending_or_self_review_cannot_be_done (test_workflow.WorkflowTests) ... ok test_prompt_amend_updates_outcome_without_extra_entry (test_workflow.WorkflowTests) ... ok test_prompt_rotation_at_fifty (test_workflow.WorkflowTests) ... ok test_readonly_check_detects_stale_view (test_workflow.WorkflowTests) ... ok test_real_git_ancestry_proof (test_workflow.WorkflowTests) ... ok test_render_is_idempotent (test_workflow.WorkflowTests) ... ok test_start_blocked_task_does_not_modify_records (test_workflow.WorkflowTests) ... ok test_unchecked_acceptance_cannot_be_done (test_workflow.WorkflowTests) ... ok test_unknown_dependency_rejected (test_workflow.WorkflowTests) ... ok test_unmerged_commit_cannot_be_done (test_workflow.WorkflowTests) ... ok test_verify_accepts_explicit_project_subdirectory (test_workflow.WorkflowTests) ... ok test_verify_executes_check_and_records_real_failure (test_workflow.WorkflowTests) ... ok test_verify_refuses_directory_outside_project (test_workflow.WorkflowTests) ... ok ---------------------------------------------------------------------- Ran 27 tests in 0.242s OK
- Check **passed**: `git diff --exit-code -- prototype src cache demo_fixtures .env.example` — Exit 0.
- Check **passed**: `python3 scripts/workflow.py check` — Exit 0. Workflow records valid: 15 tasks, 3 prompts. Recorded failed product checks remain visible; this is not a product test pass.
- Check **passed**: `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` — Exit 0. sts) ... ok test_failed_or_unrun_checks_cannot_be_done (test_workflow.WorkflowTests) ... ok test_focused_member_status_succeeds (test_workflow.WorkflowTests) ... ok test_log_refuses_long_or_multiline_summary (test_workflow.WorkflowTests) ... ok test_manual_active_status_cannot_bypass_dependencies (test_workflow.WorkflowTests) ... ok test_member_logs_are_separate_and_pipe_safe (test_workflow.WorkflowTests) ... ok test_passing_check_does_not_automatically_accept_task (test_workflow.WorkflowTests) ... ok test_pending_or_self_review_cannot_be_done (test_workflow.WorkflowTests) ... ok test_professional_docs_have_small_entrypoint_budgets (test_workflow.WorkflowTests) ... ok test_prompt_amend_updates_outcome_without_extra_entry (test_workflow.WorkflowTests) ... ok test_prompt_rotation_at_fifty (test_workflow.WorkflowTests) ... ok test_readonly_check_detects_stale_view (test_workflow.WorkflowTests) ... ok test_real_git_ancestry_proof (test_workflow.WorkflowTests) ... ok test_render_is_idempotent (test_workflow.WorkflowTests) ... ok test_reopening_checklist_prerequisite_reopens_done_children (test_workflow.WorkflowTests) ... ok test_start_blocked_task_does_not_modify_records (test_workflow.WorkflowTests) ... ok test_unchecked_acceptance_cannot_be_done (test_workflow.WorkflowTests) ... ok test_unknown_dependency_rejected (test_workflow.WorkflowTests) ... ok test_unmerged_commit_cannot_be_done (test_workflow.WorkflowTests) ... ok test_verify_accepts_explicit_project_subdirectory (test_workflow.WorkflowTests) ... ok test_verify_executes_check_and_records_real_failure (test_workflow.WorkflowTests) ... ok test_verify_refuses_directory_outside_project (test_workflow.WorkflowTests) ... ok ---------------------------------------------------------------------- Ran 44 tests in 0.260s OK
- Check **passed**: `python3 -B -m unittest discover -s tests -p 'test_*.py'` — Exit 0. .............................................. ---------------------------------------------------------------------- Ran 46 tests in 0.253s OK
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: All owners use the focused task/checklist helpers and PR declaration. A different teammate reviews this tooling before accepted delivery.

### PLAN-SCOPE — Document strengthened mandatory MVP and gated future roadmap

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Implement planning documents and task handoffs only; do not claim scientific product work is completed.

- [x] **s01 · Fardin · done:** Write the two scope contexts
  - How: Define strengthened mandatory acceptance and explicitly gated optional future tracks.
  - Files: docs/MVP_SCOPE.md, docs/FUTURE_ROADMAP.md
  - Verify: Scope is concrete; fertilizer/runtime AI remain excluded from MVP.
  - Evidence: MVP_SCOPE.md defines 12 mandatory capabilities and FUTURE_ROADMAP.md defines seven separately gated optional tracks.
- [x] **s02 · Fardin · done:** Align canonical specs and execution instructions
  - How: Update README/AGENTS/product/API/UI/method/validation/source/team/submission boundaries without changing app code.
  - Files: README.md, AGENTS.md, docs/
  - Verify: No contradictory baseline, same-crop-history or completion semantics.
  - Before: s01
  - Evidence: README/AGENTS and product/API/UI/method/validation/source/architecture/team/release instructions align on pilot, baseline/alternatives, equal crop history, structured checks and exclusions.
- [x] **s03 · Fardin · done:** Rebase ordered task records and handoffs
  - How: Preserve previous local evidence, add receipt/story/future work and make media preparation distinct from final delivery.
  - Files: docs/tasks/, docs/PROGRESS.md
  - Verify: Dependencies are acyclic, future starts blocked and product steps stay unticked.
  - Before: s02
  - Evidence: 26 packages contain 125 ordered items; story/receipt follow G3, G4 precedes G5, media preparation is separate and all seven future tracks retain explicit blockers.
- [x] **s04 · Fardin · done:** Validate documents and record real outcome
  - How: Run existing helper tests and record/link/generated-view checks; inspect final changes.
  - Files: tests/, docs/PROGRESS.md, docs/PROMPT_LOG.md
  - Verify: Only actual implementation command is logged; human review/merge remain pending.
  - Before: s03
  - Evidence: 46 existing helper tests passed; record/generated-view/link validation passed; scope audit confirmed seven blocked future tracks, no product ticks and no application/helper/test code edits.
- Check **passed**: `python3 -B -m unittest discover -s tests -p 'test_*.py'` — Exit 0. .............................................. ---------------------------------------------------------------------- Ran 46 tests in 0.270s OK
- Check **passed**: `python3 scripts/workflow.py check` — Exit 0. Workflow records valid: 26 tasks, 5 prompts. Recorded failed product checks remain visible; this is not a product test pass.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: All six members read the two scope contexts and assigned task. G0 remains planned until implementation is started; no product feature is accepted by this documentation change.

### G0-CONTRACT — Agree source, crop, field and API contracts

Owner: **Fardin** · State: `ready` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Prevent four technical owners from building incompatible schemas, units and assumptions.

- [ ] **s01 · Fardin · planned:** Draft stable field, crop and source identifiers
  - How: Agree pilot coverage, stable IDs, short intake, equal previous/current crop IDs, dated history, usual baseline/fallow and common horizon; propose comparison bundle and per-plan statuses.
  - Files: docs/API_CONTRACT.md
  - Verify: Every technical owner can distinguish an assessed baseline, complete alternative and incomplete bundle without guessing units.
- [ ] **s02 · Saim · planned:** Agree the climate evidence payload
  - How: Saim specifies parameter IDs, time standard, period, units, missingness and grid support; do not insert invented values.
  - Files: docs/API_CONTRACT.md, docs/DATA_SOURCES.md
  - Verify: Fardin/Prachurjo can consume one versioned schema without guessing units.
  - Before: s01
- [ ] **s03 · Maruf · planned:** Agree executable crop-rule fields
  - How: Define essentiality, pass/fail/caution/unknown, reviewed rule IDs/sources, calendars/duration and soil/water/host constraints; exclude fertilizer and nutrient-depletion calculations.
  - Files: docs/API_CONTRACT.md, docs/METHODOLOGY.md
  - Verify: The rules distinguish unknown/unsupported from actual exclusions.
  - Before: s01
- [ ] **s04 · Prachurjo · planned:** Agree frontend states and errors
  - How: Map three priority presets, comparison matrix, quick crop check, check ledger, replay and print/JSON receipt to API states; keep the form progressive.
  - Files: docs/API_CONTRACT.md, docs/UI_UX_SPEC.md
  - Verify: No failed API is replaced with a fabricated success.
  - Before: s01
- [ ] **s05 · Fardin · planned:** Freeze reviewed examples and contracts
  - How: Freeze reviewed payload examples, deterministic preset/tie-break rules, period comparability and canonical input/result fingerprinting.
  - Files: docs/API_CONTRACT.md
  - Verify: Four technical owners agree schemas and synthetic shape cases; fingerprints exclude volatile timestamps and imply no scientific certification.
  - Before: s02, s03, s04
- [ ] **s06 · Fardin · planned:** Review, merge and announce G1 handoffs
  - How: Record independent review and actual main-branch revision; G1 owners update their branches.
  - Files: docs/tasks/G0-CONTRACT.json
  - Verify: Acceptance/checks/review/merge evidence is real before dependent work starts.
  - Before: s05
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: After acceptance/merge: Saim starts G1A, Maruf G1B, Fardin G1C and Prachurjo G1D in parallel.

### MEDIA-STORY — Draft factual story, claims checklist and presentation outline

Owner: **Hla** · State: `ready` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Make the science and user benefit clear without overstating what the project has built.

- [ ] **s01 · Hla · planned:** Define the problem and audience
  - How: Explain why rotation choices in Bangladesh matter without inventing quantified impact.
  - Files: media/story-outline.md
  - Verify: The story names a real user/problem and distinguishes plans from shipped behavior.
- [ ] **s02 · Hla · planned:** Build a claims and citations checklist
  - How: List every numeric/scientific/feature claim and its evidence owner; mark unknowns.
  - Files: media/claims.md
  - Verify: Saim/Maruf/Fardin can approve or reject each claim explicitly.
  - Before: s01
- [ ] **s03 · Hla · planned:** Draft the timed script
  - How: Use approved behavior and placeholders for unverified claims; coordinate edit timing with Nadim.
  - Files: media/narration.md
  - Verify: The draft fits verified event requirements when available; no unbuilt feature is narrated as live.
  - Before: s02
- [ ] **s04 · Hla · planned:** Prepare provisional narration timing and pronunciation
  - How: Prepare pacing/pronunciation using clearly marked draft text; final narration waits for G5 claim approval.
  - Files: media/narration.md, agreed media storage
  - Verify: No provisional script is presented as a verified final recording.
  - Before: s03
- [ ] **s05 · Hla · planned:** Rehearse and prepare judge Q&A
  - How: Prepare Q&amp;A and rehearsal notes with unknown/unbuilt claims marked; final answers follow accepted science.
  - Files: media/judge-qa.md
  - Verify: The team can reproduce claims and answer known scientific/coverage limits.
  - Before: s04
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Preparation can run in parallel. G5 owns approved final narration, actual scientific captures, edit, subtitles and exports after G4 acceptance.

### MEDIA-STORYBOARD — Prepare storyboard, capture plan and asset ledger

Owner: **Nadim** · State: `ready` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Make actual app evidence understandable and keep every media asset attributable.

- [ ] **s01 · Nadim · planned:** Plan the shots and visual sequence
  - How: Coordinate with Hla; identify which shots need real G3/G4 behavior.
  - Files: media/storyboard.md
  - Verify: Shot list distinguishes illustrative treatment from measured data/app footage.
- [ ] **s02 · Nadim · planned:** Maintain source and rights records
  - How: Record every photo, video, font, sound and generated asset and its reuse terms.
  - Files: media/asset-ledger.md
  - Verify: Nadim/Prachurjo can trace each asset and flag missing permissions.
  - Before: s01
- [ ] **s03 · Nadim · planned:** Prepare the verified-app capture checklist
  - How: Plan shots and test capture tools against labelled current demo; final scientific footage waits for G5.
  - Files: media/shot-list.md, agreed media storage
  - Verify: Preparation does not imply unbuilt scientific UI was captured.
  - Before: s02
- [ ] **s04 · Nadim · planned:** Prepare editing and subtitle templates
  - How: Create clearly labelled draft title/subtitle/edit templates; final edit follows G5 approved narration and actual footage.
  - Files: media/edit-plan.md, agreed media storage
  - Verify: Draft media never claims accepted agricultural outputs.
  - Before: s03
- [ ] **s05 · Nadim · planned:** Verify export preparation and formats
  - How: Test export workflow with labelled sample material; confirm actual portal formats before final G5 export.
  - Files: media/export-checklist.md
  - Verify: Preparation evidence is separate from final submitted files.
  - Before: s04
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Preparation can run in parallel. G5 owns approved final narration, actual scientific captures, edit, subtitles and exports after G4 acceptance.

### INTAKE-MAP — Add independent confirmed map-pin and district-search intake locations

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Explicitly authorized independent local map/intake extension. INTAKE-UI local work exists and is reopened for regression; neither accepted G0 nor science is a prerequisite for this bounded administrative-location UI.

- [x] **a1 · Fardin · done:** Version licensed local boundaries with explicit 64-district mapping and tested containment.
  - How: Pin licensed geoBoundaries metadata/geometry and verify checksums; map all 64 source feature IDs/names explicitly; test containment, holes, multipolygons and border ambiguity.
  - Files: data/admin/, prototype/public/reference/data/, prototype/public/reference/location.js, scripts/prepare_district_boundaries.py, tests/location.test.cjs, tests/fixtures/district-interior-points.json
  - Verify: Source and runtime integrity, mapping bijection, 64 independent geometry-derived interiors and synthetic topology cases pass. No bounding-box or nearest-district acceptance.
  - Evidence: Pinned geoBoundaries BGD-ADM2-16705992 at 9469f09, CC BY 3.0 IGO, verified Git LFS/source/output SHA-256, 64 explicit mappings with ten aliases. Local simplified geometry preserves all rings/coordinates. Containment, holes/multipolygons, border ambiguity and all 64 independent geometry-derived fixtures pass in the 30-test intake/location suite.
- [x] **a2 · Fardin · done:** Integrate MapLibre, independent location methods, migration and accessible map lifecycle in the mounted intake.
  - How: Extend the actual mounted form with independent methods, lazy MapLibre bridge, explicit pin confirmation, local resolution, lifecycle cleanup, v2 migration and no stale location state. Preserve all six required questions.
  - Files: prototype/components/IntakeMapRuntime.js, prototype/app/workspace/page.js, prototype/public/reference/intake.js, prototype/public/reference/intake-ui.js, prototype/public/reference/intake-map.js, prototype/public/reference/workspace.js, prototype/public/reference/workspace-fixes.css, prototype/package.json, prototype/package-lock.json
  - Verify: Actual UI-controller submit handler supports both methods and rejects unconfirmed pins; pure/mocked lifecycle and failure checks pass. Full browser/physical-device checks are separately reported, not assumed.
  - Before: a1
  - Evidence: Mounted reference intake uses a lazy Next Client Component MapLibre bridge, local containment, draggable/keyboard-movable pending pins and explicit confirmation. Separate district search, schema/envelope v2 migration, pending saved-pin recheck and draft/last-valid-submission separation are implemented. UI submit-handler and map lifecycle/failure tests pass; full successful browser walkthroughs remain unverified because browser/native control tools failed.
- [x] **a3 · Fardin · done:** Run regression, browser, syntax, lint/build and workflow checks; document providers, limitations and handoff.
  - How: Run existing/regression tests, direct script syntax, lint/build, reproducible asset/HTTP checks and workflow validation. Record browser attempts and not-performed checks, provider rights, migration and independent handoff.
  - Files: docs/LOCATION_QA.md, docs/INTAKE_QA.md, docs/API_CONTRACT.md, docs/UI_UX_SPEC.md, docs/DATA_SOURCES.md, THIRD_PARTY_NOTICES.md, prototype/public/reference/licenses/maplibre-gl.LICENSE.txt, docs/tasks/INTAKE-MAP.json, docs/tasks/INTAKE-UI.json
  - Verify: Actual check outputs and limitations are recorded; no G0/science or human review acceptance, commit, push or deployment is claimed.
  - Before: a2
  - Evidence: 31 intake/location tests and 46 workflow tests pass; five changed reference scripts pass direct Node syntax checks, lint and webpack production build pass, deterministic boundary rebuild and all eight loopback asset/checksum/license checks pass, and workflow validation passes. Browser connector/native pointer failures prevented reliable complete submissions and current map mobile/physical testing; docs/LOCATION_QA.md explicitly records these unverified checks and next reviewer. One Fardin command is logged; no commit/push/deploy.
- Check **passed**: `node --check prototype/public/reference/intake.js` — Exit 0.
- Check **passed**: `node --check prototype/public/reference/workspace.js` — Exit 0.
- Check **passed**: `npm run lint` — Exit 0. npm notice run soil-to-stars-prototype@1.0.0 lint npm notice run eslint .
- Check **passed**: `npm run build -- --webpack` — Exit 0. ▲ Next.js 16.4.3 (webpack) ✓ Running next.config.mjs took 7ms Creating an optimized production build ... ✓ Compiled successfully in 721ms Running TypeScript ... Finished TypeScript in 1ms ... Collecting page data using 5 workers ... Generating static pages using 5 workers (0/4) ... Generating static pages using 5 workers (1/4) Generating static pages using 5 workers (2/4) Generating static pages using 5 workers (3/4) ✓ Generating static pages using 5 workers (4/4) in 273ms Finalizing page optimization ... Collecting build traces ... Route (app) ┌ ○ / ├ ○ /_not-found └ ○ /workspace ○ (Static) prerendered as static content npm notice run soil-to-stars-prototype@1.0.0 build npm notice run next build --webpack
- Check **passed**: `python3 scripts/prepare_district_boundaries.py` — Exit 0. 64 districts; 38112 vertices; 1494403 bytes; 507697 gzip bytes; SHA-256 9503a358ddcb99714db5866ef049e7ddea0d5fd6e05a0d3719a6553b3953c01a
- Check **passed**: `npm run test:intake` — Exit 0. t; invalid edits never replace the last valid submission (0.52ms) ✔ live form submission uses shared validation, persists only valid answers and renders unavailable summary (0.91575ms) ✔ English/Bangla render keeps IDs unchanged and escapes restored user text (0.722333ms) ✔ actual UI submit handler requires pin confirmation and supports either method without stale data (9.707583ms) ✔ pinned source/license/checksums and all 64 exact boundary mappings agree (9.455375ms) ✔ Polygon, holes, MultiPolygon and numerical border handling (0.190958ms) ✔ outside, unresolved holes/gaps, overlap and shared borders never snap to a district (0.188958ms) ✔ invalid, non-finite and reversed longitude/latitude inputs are rejected (0.061709ms) ✔ 64 independent source-derived interiors resolve and normalize to their explicit district IDs (15.358375ms) ✔ new/moved pin needs confirmation and stale district, source version or geometry cannot pass (0.394875ms) ✔ method switching clears inactive coordinates/districts and district search needs no boundaries (0.127417ms) ✔ genuine v1 district answers migrate to v2 without coordinates or demo defaults (0.34ms) ✔ boundary loader rejects missing/duplicate mappings and unsupported or broken rings (12.853708ms) ✔ map rerenders reuse one instance/listeners and preserve pin/answers; leaving removes resources (14.140958ms) ✔ WebGL and boundary-network failure retain answers and leave district fallback independent (7.372625ms) ✔ tile errors and lost WebGL context surface fallback without destroying other answers (7.753334ms) ℹ tests 31 ℹ suites 0 ℹ pass 31 ℹ fail 0 ℹ cancelled 0 ℹ skipped 0 ℹ todo 0 ℹ duration_ms 184.246083 npm notice run soil-to-stars-prototype@1.0.0 test:intake npm notice run node --test ../tests/intake.test.cjs ../tests/location.test.cjs
- Check **passed**: `node --check prototype/public/reference/location.js` — Exit 0.
- Check **passed**: `node --check prototype/public/reference/intake-map.js` — Exit 0.
- Check **passed**: `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` — Exit 0. sts) ... ok test_failed_or_unrun_checks_cannot_be_done (test_workflow.WorkflowTests) ... ok test_focused_member_status_succeeds (test_workflow.WorkflowTests) ... ok test_log_refuses_long_or_multiline_summary (test_workflow.WorkflowTests) ... ok test_manual_active_status_cannot_bypass_dependencies (test_workflow.WorkflowTests) ... ok test_member_logs_are_separate_and_pipe_safe (test_workflow.WorkflowTests) ... ok test_passing_check_does_not_automatically_accept_task (test_workflow.WorkflowTests) ... ok test_pending_or_self_review_cannot_be_done (test_workflow.WorkflowTests) ... ok test_professional_docs_have_small_entrypoint_budgets (test_workflow.WorkflowTests) ... ok test_prompt_amend_updates_outcome_without_extra_entry (test_workflow.WorkflowTests) ... ok test_prompt_rotation_at_fifty (test_workflow.WorkflowTests) ... ok test_readonly_check_detects_stale_view (test_workflow.WorkflowTests) ... ok test_real_git_ancestry_proof (test_workflow.WorkflowTests) ... ok test_render_is_idempotent (test_workflow.WorkflowTests) ... ok test_reopening_checklist_prerequisite_reopens_done_children (test_workflow.WorkflowTests) ... ok test_start_blocked_task_does_not_modify_records (test_workflow.WorkflowTests) ... ok test_unchecked_acceptance_cannot_be_done (test_workflow.WorkflowTests) ... ok test_unknown_dependency_rejected (test_workflow.WorkflowTests) ... ok test_unmerged_commit_cannot_be_done (test_workflow.WorkflowTests) ... ok test_verify_accepts_explicit_project_subdirectory (test_workflow.WorkflowTests) ... ok test_verify_executes_check_and_records_real_failure (test_workflow.WorkflowTests) ... ok test_verify_refuses_directory_outside_project (test_workflow.WorkflowTests) ... ok ---------------------------------------------------------------------- Ran 46 tests in 0.326s OK
- Check **passed**: `python3 scripts/workflow.py check` — Exit 0. Workflow records valid: 28 tasks, 7 prompts. Recorded failed product checks remain visible; this is not a product test pass.
- Check **passed**: `node --check prototype/public/reference/intake-ui.js` — Exit 0.
- Check **passed**: `python3 scripts/check_location_assets.py --base-url http://127.0.0.1:3014` — Exit 0. {"asset": "/workspace", "status": 200, "encoding": "gzip", "transfer_bytes": 3367, "decoded_bytes": 12864, "loopback_ms": 15.87} {"asset": "/reference/location.js", "status": 200, "encoding": "gzip", "transfer_bytes": 2434, "decoded_bytes": 7057, "loopback_ms": 1.41} {"asset": "/reference/intake.js", "status": 200, "encoding": "gzip", "transfer_bytes": 5115, "decoded_bytes": 15459, "loopback_ms": 1.15} {"asset": "/reference/intake-map.js", "status": 200, "encoding": "gzip", "transfer_bytes": 2710, "decoded_bytes": 7349, "loopback_ms": 0.82} {"asset": "/reference/intake-ui.js", "status": 200, "encoding": "gzip", "transfer_bytes": 12521, "decoded_bytes": 43925, "loopback_ms": 1.36} {"asset": "/reference/data/district-boundaries.v1.geojson", "status": 200, "encoding": "gzip", "transfer_bytes": 513054, "decoded_bytes": 1494403, "loopback_ms": 50.93} {"asset": "/reference/licenses/maplibre-gl.LICENSE.txt", "status": 200, "encoding": "gzip", "transfer_bytes": 1531, "decoded_bytes": 5984, "loopback_ms": 1.12} {"asset": "/_next/static/media/maplibre-gl-worker.36d105f0.mjs", "status": 200, "encoding": "gzip", "transfer_bytes": 146732, "decoded_bytes": 510888, "loopback_ms": 10.39} All 8 loopback assets match; boundary checksum and deployed license verified. Browser/WebGL/mobile not tested.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: Prachurjo independently reviews both complete browser submissions, secure phone-width/physical-device map behavior, keyboard/EN-BN and failure fallbacks; Fardin coordinates later G0/API integration. Scientific gates remain pending.

### INTAKE-UI — Implement nationwide required farmer intake without scientific recommendations

Owner: **Fardin** · State: `in_review` · Updated UTC: `2026-10-30T16:49:54Z`

**Why:** Fardin explicitly authorized independent local intake UI/validation in the current mounted reference route. Shared scientific API/schema agreement, source acquisition and G1D/G3 integration remain separate unaccepted work.

- [x] **a1 · Fardin · done:** Verify the 64-district directory and implement testable required-answer normalization.
  - How: Verify National Portal district membership/names; create stable application IDs and shared validation/normalization with explicit absence states. No coordinate or scientific defaults.
  - Files: prototype/public/reference/intake.js, tests/intake.test.cjs, docs/DATA_SOURCES.md
  - Verify: Reject every missing/malformed required/dependent answer; verify 64 unique districts, date consistency, chronology and separate normalized history/baseline/provenance.
  - Evidence: Local National Portal directory checked on 2026-10-30: 64 distinct application IDs across 8 divisions, EN/BN names and source version; intake.js validates and normalizes required/dependent inputs with 17 passing Node tests.
- [x] **a2 · Fardin · done:** Replace the mounted wizard with bilingual accessible intake and honest summary, preserving drafts and separate demo mode.
  - How: Use the actual reference-script workspace, six ordered questions, explicit priority, accessible errors, local genuine drafts and submitted summary. Keep demo mode separate.
  - Files: prototype/public/reference/intake-ui.js, prototype/public/reference/workspace.js, prototype/public/reference/workspace-fixes.css, prototype/reference/workspace-preview.html
  - Verify: Mounted form uses shared validator; no mock rankings for intake. Check EN/BN, keyboard/native selection, error focus and mobile wrapping.
  - Before: a1
  - Evidence: Mounted static workspace imports the shared intake modules. Six-question EN/BN form, adjacent/summary errors, genuine draft/submission separation, input-only unavailable summary and explicit separate demo are implemented. UI-controller submit tests pass; native Chrome checked blank errors, district search/keyboard selection, language switching and 400x748 mobile layout. Detailed limits in docs/INTAKE_QA.md.
- [x] **a3 · Fardin · done:** Verify intake behavior, lint, build and workflow records; document scientific dependencies.
  - How: Run targeted Node tests/syntax checks, configured lint/build and workflow tests/check; update intake specifications and record the one authorized Fardin instruction.
  - Files: docs/API_CONTRACT.md, docs/UI_UX_SPEC.md, docs/MVP_SCOPE.md, docs/PRODUCT_SPEC.md, docs/INTAKE_QA.md, docs/tasks/INTAKE-UI.json, docs/tasks/G1D.json, prototype/package.json, prototype/README.md
  - Verify: Actual results and limits are recorded, views regenerated, pending G0/G1D/scientific gates stay unaccepted and no commit/push/deploy occurs.
  - Before: a2
  - Evidence: 18 Node intake/UI-controller tests, 46 Python workflow tests, three changed-script Node syntax checks, npm lint, webpack production build and workflow check pass. Latest contract/UI/source/task records updated, one Fardin command logged; scientific gates and human review remain unaccepted. Browser checks and not-claimed checks recorded in docs/INTAKE_QA.md.
- Check **passed**: `node --check prototype/public/reference/intake.js` — Exit 0.
- Check **passed**: `node --check prototype/public/reference/intake-ui.js` — Exit 0.
- Check **passed**: `node --check prototype/public/reference/workspace.js` — Exit 0.
- Check **passed**: `npm run test:intake` — Exit 0. t; invalid edits never replace the last valid submission (0.52ms) ✔ live form submission uses shared validation, persists only valid answers and renders unavailable summary (0.91575ms) ✔ English/Bangla render keeps IDs unchanged and escapes restored user text (0.722333ms) ✔ actual UI submit handler requires pin confirmation and supports either method without stale data (9.707583ms) ✔ pinned source/license/checksums and all 64 exact boundary mappings agree (9.455375ms) ✔ Polygon, holes, MultiPolygon and numerical border handling (0.190958ms) ✔ outside, unresolved holes/gaps, overlap and shared borders never snap to a district (0.188958ms) ✔ invalid, non-finite and reversed longitude/latitude inputs are rejected (0.061709ms) ✔ 64 independent source-derived interiors resolve and normalize to their explicit district IDs (15.358375ms) ✔ new/moved pin needs confirmation and stale district, source version or geometry cannot pass (0.394875ms) ✔ method switching clears inactive coordinates/districts and district search needs no boundaries (0.127417ms) ✔ genuine v1 district answers migrate to v2 without coordinates or demo defaults (0.34ms) ✔ boundary loader rejects missing/duplicate mappings and unsupported or broken rings (12.853708ms) ✔ map rerenders reuse one instance/listeners and preserve pin/answers; leaving removes resources (14.140958ms) ✔ WebGL and boundary-network failure retain answers and leave district fallback independent (7.372625ms) ✔ tile errors and lost WebGL context surface fallback without destroying other answers (7.753334ms) ℹ tests 31 ℹ suites 0 ℹ pass 31 ℹ fail 0 ℹ cancelled 0 ℹ skipped 0 ℹ todo 0 ℹ duration_ms 184.246083 npm notice run soil-to-stars-prototype@1.0.0 test:intake npm notice run node --test ../tests/intake.test.cjs ../tests/location.test.cjs
- Check **passed**: `npm run lint` — Exit 0. npm notice run soil-to-stars-prototype@1.0.0 lint npm notice run eslint .
- Check **passed**: `npm run build -- --webpack` — Exit 0. ▲ Next.js 16.4.3 (webpack) ✓ Running next.config.mjs took 7ms Creating an optimized production build ... ✓ Compiled successfully in 721ms Running TypeScript ... Finished TypeScript in 1ms ... Collecting page data using 5 workers ... Generating static pages using 5 workers (0/4) ... Generating static pages using 5 workers (1/4) Generating static pages using 5 workers (2/4) Generating static pages using 5 workers (3/4) ✓ Generating static pages using 5 workers (4/4) in 273ms Finalizing page optimization ... Collecting build traces ... Route (app) ┌ ○ / ├ ○ /_not-found └ ○ /workspace ○ (Static) prerendered as static content npm notice run soil-to-stars-prototype@1.0.0 build npm notice run next build --webpack
- Check **passed**: `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` — Exit 0. sts) ... ok test_failed_or_unrun_checks_cannot_be_done (test_workflow.WorkflowTests) ... ok test_focused_member_status_succeeds (test_workflow.WorkflowTests) ... ok test_log_refuses_long_or_multiline_summary (test_workflow.WorkflowTests) ... ok test_manual_active_status_cannot_bypass_dependencies (test_workflow.WorkflowTests) ... ok test_member_logs_are_separate_and_pipe_safe (test_workflow.WorkflowTests) ... ok test_passing_check_does_not_automatically_accept_task (test_workflow.WorkflowTests) ... ok test_pending_or_self_review_cannot_be_done (test_workflow.WorkflowTests) ... ok test_professional_docs_have_small_entrypoint_budgets (test_workflow.WorkflowTests) ... ok test_prompt_amend_updates_outcome_without_extra_entry (test_workflow.WorkflowTests) ... ok test_prompt_rotation_at_fifty (test_workflow.WorkflowTests) ... ok test_readonly_check_detects_stale_view (test_workflow.WorkflowTests) ... ok test_real_git_ancestry_proof (test_workflow.WorkflowTests) ... ok test_render_is_idempotent (test_workflow.WorkflowTests) ... ok test_reopening_checklist_prerequisite_reopens_done_children (test_workflow.WorkflowTests) ... ok test_start_blocked_task_does_not_modify_records (test_workflow.WorkflowTests) ... ok test_unchecked_acceptance_cannot_be_done (test_workflow.WorkflowTests) ... ok test_unknown_dependency_rejected (test_workflow.WorkflowTests) ... ok test_unmerged_commit_cannot_be_done (test_workflow.WorkflowTests) ... ok test_verify_accepts_explicit_project_subdirectory (test_workflow.WorkflowTests) ... ok test_verify_executes_check_and_records_real_failure (test_workflow.WorkflowTests) ... ok test_verify_refuses_directory_outside_project (test_workflow.WorkflowTests) ... ok ---------------------------------------------------------------------- Ran 46 tests in 0.326s OK
- Check **passed**: `python3 scripts/workflow.py check` — Exit 0. Workflow records valid: 28 tasks, 7 prompts. Recorded failed product checks remain visible; this is not a product test pass.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: feature/intake-location; issue/PR: not created/recorded
- Handoff: Prachurjo independently reviews the mounted intake and EN/BN usability; Fardin coordinates G0/G1C transport integration only after accepted contracts. Saim/Maruf supply scientific evidence/rules through their existing gates.

### G1A — Acquire and validate the first NASA POWER evidence sample

Owner: **Saim** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Provide authentic reproducible NASA climate context rather than illustrative frontend values.

- [ ] **s01 · Saim · planned:** Select the first POWER subset
  - How: Agree one supported pilot, exact POWER rainfall/temperature parameters, suitable historical period and story/replay needs; no additional mission required.
  - Files: src/acquire/, docs/DATA_SOURCES.md
  - Verify: Selection and limitations are documented; 2001–2025 is conditional on coverage.
- [ ] **s02 · Saim · planned:** Save the authentic raw response
  - How: Implement bounded timeout/error handling and a reproducible acquisition command.
  - Files: src/acquire/, cache/
  - Verify: Raw bytes are authentic; no credential is committed.
  - Before: s01
- [ ] **s03 · Saim · planned:** Validate dates, units and missingness
  - How: Check fill codes, time standard, expected/leap-day counts and native/output grid scale.
  - Files: src/acquire/, tests/
  - Verify: QA tests and an actual quality report identify gaps without silently filling them.
  - Before: s02
- [ ] **s04 · Saim · planned:** Normalize and manifest the subset
  - How: Write a versioned normalized table plus checksum/source/license/processing metadata.
  - Files: cache/, docs/DATA_SOURCES.md
  - Verify: Another teammate can reproduce the exact normalized bytes.
  - Before: s03
- [ ] **s05 · Saim · planned:** Compute baseline climate aggregates
  - How: Use deterministic daily/monthly/seasonal methods with documented missingness.
  - Files: src/compute/, tests/
  - Verify: Reference cases verify units, sums/means and missing-day behavior.
  - Before: s04
- [ ] **s06 · Saim · planned:** Freeze a permitted demo fixture
  - How: Commit only a small redistribution-permitted subset with source manifest.
  - Files: demo_fixtures/
  - Verify: Fixture bytes/source/checksum and replay commands are reviewable.
  - Before: s05
- [ ] **s07 · Saim · planned:** Cross-review and hand off evidence
  - How: Fardin reproduces outputs; Maruf checks agricultural applicability.
  - Files: docs/tasks/G1A.json
  - Verify: Reviewed/merged evidence and schema version are recorded for G2/G3.
  - Before: s06, s08
- [ ] **s08 · Saim · planned:** Prepare versioned chart and replay payloads
  - How: Predeclare comparison periods/stress selection; export real arrays, units, sample counts, missingness and method/source identities.
  - Files: src/compute/, docs/DATA_SOURCES.md
  - Verify: Charts/replay refer to the same verified evidence; no trend or forecast is invented.
  - Before: s05
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Fardin consumes evidence in G2; Prachurjo consumes approved chart arrays in G3; Maruf reviews applicability.

### G1B — Source Bangladesh crop, soil and rotation rules

Owner: **Maruf** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Make recommended crops and exclusions depend on documented local agronomy rather than plausible guesses.

- [ ] **s01 · Maruf · planned:** Select exact local agronomy sources
  - How: Identify Bangladesh-relevant BARC/BAMIS/BARI/BRRI/DAE/SRDI/FAO publications and rights.
  - Files: docs/DATA_SOURCES.md
  - Verify: Exact documents, region/version/rights and limitations are recorded.
- [ ] **s02 · Maruf · planned:** Create stable diverse crop metadata
  - How: Choose one pilot and a small reviewed crop-season catalogue; preserve category/family and annual/perennial metadata. Target 6–10 supported records without inventing any.
  - Files: data/catalog/
  - Verify: Active records are source-gated; wider diversity/coverage remains a future expansion.
  - Before: s01
- [ ] **s03 · Maruf · planned:** Encode regional sowing and harvest windows
  - How: Use cited windows/durations including cross-year seasons; do not guess dates.
  - Files: data/catalog/
  - Verify: Every active calendar/duration has region applicability and source evidence.
  - Before: s02
- [ ] **s04 · Maruf · planned:** Encode soil and water constraints
  - How: Preserve unknown soil values and validate any pH/drainage/salinity/water thresholds.
  - Files: data/catalog/
  - Verify: Unsupported crop-region/soil conditions do not silently pass advice gates.
  - Before: s03
- [ ] **s05 · Maruf · planned:** Encode sequence/family rules
  - How: Encode locally applicable host/family cautions and qualified soil-management traits with source/essentiality; no fertilizer, NPK depletion or numerical restoration model.
  - Files: data/catalog/, docs/METHODOLOGY.md
  - Verify: A family change does not automatically certify disease removal; repeated historical crops remain representable.
  - Before: s04
- [ ] **s06 · Maruf · planned:** Test executable rule behavior
  - How: Review rule parsing, seasons, unknowns and conflicting inputs with Fardin/Saim.
  - Files: tests/, data/catalog/
  - Verify: Reference cases prove unsupported/infeasible candidates are not rescued by preferences.
  - Before: s05
- [ ] **s07 · Maruf · planned:** Review, merge and hand off catalog
  - How: Record validation status for each active crop-region rule and the contract revision.
  - Files: docs/tasks/G1B.json
  - Verify: G2 receives a reviewed catalog, exclusions and explicit evidence gaps.
  - Before: s06, s08
- [ ] **s08 · Maruf · planned:** Obtain appropriate local review of active pilot rules
  - How: Arrange documented review by an appropriately qualified local agronomic reviewer; resolve gaps or keep affected rules inactive. Do not equate student code review with certification.
  - Files: data/catalog/, docs/VALIDATION.md
  - Verify: Reviewer scope/evidence is genuine; unavailable review remains a visible release dependency.
  - Before: s06
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Fardin consumes active rules in G2; Saim reviews climate alignment; unsupported cases remain explicit.

### G1C — Implement API validation and schema/test foundation

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Give compute and frontend a stable validated transport contract with honest failure states.

- [ ] **s01 · Fardin · planned:** Create the backend dependency/test foundation
  - How: Choose minimal FastAPI/Pydantic dependencies in an owned task after contract agreement.
  - Files: src/api/, backend dependency manifest, tests/
  - Verify: Actual install/run/test commands exist and reproduce in a clean environment.
- [ ] **s02 · Fardin · planned:** Implement typed field input validation
  - How: Validate dates, coordinates, units, equal previous/current IDs, baseline/fallow, common horizon, water and preset; preserve optional unknowns.
  - Files: src/api/
  - Verify: Invalid/inconsistent inputs return explicit structured errors.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Implement status and provenance schemas
  - How: Implement bundle/plan statuses, check outcomes and source/version/fingerprint schemas; complete plan inside incomplete bundle is representable.
  - Files: src/api/
  - Verify: No endpoint success invents missing evidence, second alternatives or crop slots.
  - Before: s02
- [ ] **s04 · Fardin · planned:** Add health and local-evidence service boundaries
  - How: Keep downloads in acquisition and read prepared evidence during requests.
  - Files: src/api/, tests/
  - Verify: A missing cache/source returns unavailable rather than network-dependent success.
  - Before: s03
- [ ] **s05 · Fardin · planned:** Review the frontend contract
  - How: Prachurjo checks errors/payload usability; Fardin records actual checks and merge.
  - Files: docs/API_CONTRACT.md
  - Verify: Consumers agree the versioned schema before integration.
  - Before: s04
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Fardin integrates the service in G2; Prachurjo consumes the agreed adapter contract in G1D/G3.

### G1D — Extend required farmer intake and API/error-state shell

Owner: **Prachurjo** · State: `waiting` · Updated UTC: `2026-10-30T15:07:08Z`

**Why:** Make field inputs and failure states usable before connecting scientific results.

- [ ] **s01 · Prachurjo · planned:** Implement nationwide Bangladesh district selection
  - How: Use all 64 sourced districts with stable application IDs and searchable text selection; retain district-level provenance and distinguish intake selection from scientific coverage. INTAKE-UI is independent local preparation, not acceptance of this gate.
  - Files: prototype/
  - Verify: Selecting a national location does not imply validated advice there.
- [ ] **s02 · Prachurjo · planned:** Integrate the six required intake questions
  - How: Keep all six visible in order: current crop, availability, dated previous history, usual upcoming baseline, water and priority. Require meaningful answers or explicit domain absence/fallow states; no demo prefill, soil/fertilizer form or general unknown bypass.
  - Files: prototype/
  - Verify: Invalid/dependent answers and contradictory dates fail with accessible errors; drafts remain separate from submitted answers.
  - Before: s01
- [ ] **s03 · Prachurjo · planned:** Connect documented priorities
  - How: Require an explicit choice among the three priority presets, with no new-farmer default. Keep underlying evidence and hard constraints unchanged.
  - Files: prototype/
  - Verify: UI copy does not imply yield or calibrated success probabilities.
  - Before: s02
- [ ] **s04 · Prachurjo · planned:** Implement the agreed API adapter and states
  - How: Create loading/error/unavailable/incomplete views against the accepted contract.
  - Files: prototype/
  - Verify: A failed/missing API never returns fictional chart/plan constants.
  - Before: s03
- [ ] **s05 · Prachurjo · planned:** Check bilingual and accessible input flows
  - How: Review Bangla/English meaning, focus, keyboard, phone layout and reduced motion.
  - Files: prototype/
  - Verify: Record screenshots/manual checks and actual automated checks where implemented.
  - Before: s04
- [ ] **s06 · Prachurjo · planned:** Review and hand off the shell
  - How: Fardin reviews transport assumptions; preserve illustrative labels until real G2 results arrive.
  - Files: docs/tasks/G1D.json
  - Verify: An independent reviewer can reproduce the bounded shell behavior.
  - Before: s05
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Prachurjo connects G3 only after G2 and this shell are accepted; Fardin reviews transport behavior.

### G2 — Deliver the sourced baseline/alternatives engine and API

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Turn authentic climate and local agronomy into a tested feasible three-future-crop decision.

- [ ] **s01 · Fardin · planned:** Apply deterministic hard exclusions
  - How: Consume accepted climate/rules and field inputs; preserve unknown evidence.
  - Files: src/compute/
  - Verify: Water/soil/season exclusions precede every preference score.
- [ ] **s02 · Fardin · planned:** Generate feasible next-season windows
  - How: Start after current harvest and handle cross-year seasons/duration/overlap.
  - Files: src/compute/, tests/
  - Verify: Boundary cases reject impossible chronology.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Search three-step future sequences
  - How: Search exactly three future main-crop steps after current harvest where supported; retain distinct alternatives and stop honestly when evidence is insufficient.
  - Files: src/compute/
  - Verify: Insufficient evidence returns incomplete without invented filler crops.
  - Before: s02
- [ ] **s04 · Fardin · planned:** Rank and explain feasible alternatives
  - How: Apply G0-approved preset orders and stable tie-breaking over supported indicators; compare baseline and two distinct alternatives on the same horizon. Totals are optional.
  - Files: src/compute/, docs/METHODOLOGY.md
  - Verify: No missing criterion is silently scored/reweighted; priorities never bypass exclusions.
  - Before: s03, s07
- [ ] **s05 · Fardin · planned:** Serve the sourced result through the API
  - How: Serve bundle/plan statuses, common horizon, indicator/check ledger and method/source/catalogue identities with canonical input/result fingerprints.
  - Files: src/api/, tests/
  - Verify: A provenance gate rejects unsupported success and no NASA fetch occurs during requests.
  - Before: s04, s08
- [ ] **s06 · Fardin · planned:** Reproduce and obtain domain review
  - How: Saim/Maruf check real inputs and outputs; record relevant tests and merge.
  - Files: docs/tasks/G2.json
  - Verify: One scientific vertical slice is reproducible before G3 integration.
  - Before: s05, s09
- [ ] **s07 · Fardin · planned:** Assess the existing-practice baseline
  - How: Evaluate usual crop/fallow segments on the common horizon; retain infeasible baseline findings and separate baseline from past history.
  - Files: src/compute/, tests/
  - Verify: Baseline repeats/fallow remain visible; fewer than two supported alternatives leaves comparison incomplete.
  - Before: s02
- [ ] **s08 · Fardin · planned:** Return source-linked checks and why-not ledger
  - How: Emit stable rule/source IDs, pass/fail/caution/unknown and missing-information actions with translated label keys.
  - Files: src/compute/, src/api/
  - Verify: No generated prose or fabricated numeric cause; every exclusion traces to a reviewed rule.
  - Before: s01
- [ ] **s09 · Fardin · planned:** Expose the same-engine intended-crop check
  - How: Reuse validation, calendars and constraint functions; assess a proposed crop/window without building a classifier or diagnosing growing crops.
  - Files: src/compute/, src/api/, tests/
  - Verify: The same crop/input receives the same checks in planner and quick assessment.
  - Before: s02, s08
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Prachurjo consumes the reviewed API in G3; Saim/Maruf retain the evidence/domain review trail.

### G3 — Connect actual scientific outputs to the existing frontend

Owner: **Prachurjo** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Let an ordinary user obtain and inspect a traceable decision in the actual app.

- [ ] **s01 · Prachurjo · planned:** Wire actual field requests and responses
  - How: Replace the scientific result path with the accepted API and preserve error/unknown states.
  - Files: prototype/
  - Verify: Actual requests display sourced results; demo constants remain isolated.
- [ ] **s02 · Prachurjo · planned:** Display the chronological future plan
  - How: Display assessed baseline and distinct alternatives, per-plan/bundle status, common-horizon indicators, exactly three future main crops for complete plans and calendar gaps.
  - Files: prototype/
  - Verify: Previous/current crops are not mislabeled as future recommendations.
  - Before: s01
- [ ] **s03 · Prachurjo · planned:** Connect real climate arrays
  - How: Use backend values with units, dates, missingness, scale and documented baselines.
  - Files: prototype/
  - Verify: Every plotted number traces to a verified source and transformation.
  - Before: s02
- [ ] **s04 · Prachurjo · planned:** Add evidence and uncertainty access
  - How: Expose rule/source-linked why-not labels, missing-information actions, catalogue/method versions, evidence freshness and coverage; no runtime AI.
  - Files: prototype/
  - Verify: Reviewers can trace a selected result and an excluded candidate.
  - Before: s03
- [ ] **s05 · Prachurjo · planned:** Verify the end-to-end experience
  - How: Test mobile/keyboard/EN-BN/error/loading/reduced-motion behavior and domain copy.
  - Files: prototype/, docs/tasks/G3.json
  - Verify: Fardin/Saim/Maruf review the actual integrated build before expansion.
  - Before: s04, s06
- [ ] **s06 · Prachurjo · planned:** Connect the intended-crop assessment card
  - How: Reuse the selected field and API rule checks; preserve limitations and incomplete results.
  - Files: prototype/
  - Verify: Card and plan do not contradict each other for the same crop/window.
  - Before: s01
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Fardin/Saim/Maruf/Prachurjo proceed to G4; Hla/Nadim can capture only approved behavior.

### G3-REPORT — Deliver the reproducible print and JSON receipt

Owner: **Prachurjo** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Give farmers and reviewers a compact takeaway from the same API result rather than a second calculation.

- [ ] **s01 · Fardin · planned:** Preserve result and evidence identities
  - How: Confirm canonical input/source/catalogue/method fingerprints and timestamp separation from G2.
  - Files: src/api/, tests/
  - Verify: Identical scientific inputs reproduce identities; changed evidence changes them.
- [ ] **s02 · Prachurjo · planned:** Implement JSON download and basic print
  - How: Render current comparison, windows, check labels, versions, unknowns and limits from the actual response.
  - Files: prototype/
  - Verify: No separate PDF service, cloud account or illustrative export fallback.
  - Before: s01
- [ ] **s03 · Prachurjo · planned:** Check export parity, layout and privacy
  - How: Compare exported/printed result with screen/API; check incomplete states and phone print layout; avoid public field URLs.
  - Files: tests/, prototype/
  - Verify: Versions/status/units/limitations survive; no client-side science recomputation.
  - Before: s02
- [ ] **s04 · Prachurjo · planned:** Review and hand off the farmer receipt
  - How: Hla checks language; Saim/Maruf check evidence labels; Fardin checks reproduction.
  - Files: docs/tasks/G3-REPORT.json
  - Verify: Actual output and independent review/merge evidence recorded.
  - Before: s03
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Record reviewed outputs, exact revision and next consumer before acceptance.

### G3-STORY — Add the compact verified climate story

Owner: **Prachurjo** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Connect observed regional changes to the same field-planning evidence without delaying the first scientific slice.

- [ ] **s01 · Hla · planned:** Agree four scenes and source-backed captions
  - How: Use place/record, heat/rain, reviewed calendar implication and Plan My Field; Saim/Maruf review each claim.
  - Files: docs/UI_UX_SPEC.md, prototype/
  - Verify: No invented climate trend or nutrient change; conceptual illustrations are labelled.
- [ ] **s02 · Prachurjo · planned:** Consume verified climate-story payloads
  - How: Use G1A arrays/statistics with units, periods, missingness and source IDs; preserve no-clear-shift findings.
  - Files: prototype/
  - Verify: No on-scroll scientific calculations or direct NASA calls.
  - Before: s01
- [ ] **s03 · Prachurjo · planned:** Implement accessible motion and location handoff
  - How: Keep CTA/skip/sources, EN/BN, static reduced-motion path and selected location across workspace entry; Nadim supports motion.
  - Files: prototype/
  - Verify: Phone/keyboard/reduced-motion paths remain usable without watching the full story.
  - Before: s02
- [ ] **s04 · Prachurjo · planned:** Review real story behavior and hand off
  - How: Saim checks values; Hla checks meaning; Fardin checks status and reproduction.
  - Files: docs/tasks/G3-STORY.json
  - Verify: Record actual evidence/review/merge; no claim that planned data were measured.
  - Before: s03
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Record reviewed outputs, exact revision and next consumer before acceptance.

### G4 — Validate historical comparison, uncertainty and offline science

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:06:38Z`

**Why:** Demonstrate reproducibility, uncertainty, regional limits and offline science before making public claims.

- [ ] **s01 · Fardin · planned:** Choose a documented historical stress comparison
  - How: Predeclare one historical dry/wet/hot selection and periods using G1A evidence; freeze field/history/water/priority and baseline horizon. Define calendar-day/cross-year alignment and leap-day handling.
  - Files: src/compute/, docs/METHODOLOGY.md
  - Verify: Period, assumptions, units and missingness are explicit; no forecast precision is claimed.
- [ ] **s02 · Fardin · planned:** Compare decisions deterministically
  - How: Implement deterministic historical replay and API response over the same G2 engine; report changed checks and ranks, not future weather/yield.
  - Files: src/compute/, tests/
  - Verify: Only intended climate inputs change; scenario/source identities and missingness are reproducible.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Validate the supported pilot and coverage boundaries
  - How: Review actual pilot inputs/outputs and local applicability; treat other Barind/Haor/coastal contexts as unsupported until separately evidenced.
  - Files: docs/VALIDATION.md
  - Verify: No requirement to fabricate three validated regions for the first release.
  - Before: s02
- [ ] **s04 · Fardin · planned:** Enforce offline scientific replay
  - How: Use verified local fixtures and test that OFFLINE=1 blocks scientific network requests.
  - Files: src/acquire/, src/api/, demo_fixtures/, tests/
  - Verify: Missing coverage is unavailable; cache badge and source evidence remain truthful.
  - Before: s03
- [ ] **s05 · Fardin · planned:** Assess robustness and sensitivity
  - How: Test missing data, threshold/weight sensitivity, deterministic reruns and rank stability.
  - Files: tests/, docs/VALIDATION.md
  - Verify: Limits/effect sizes/sample counts accompany claims.
  - Before: s04
- [ ] **s06 · Fardin · planned:** Rehearse the actual offline demo
  - How: Test browser assets/fonts/maps separately and record the verified scientific flow.
  - Files: docs/VALIDATION.md, media/
  - Verify: Only demonstrated offline behavior is claimed; fallback recording is available.
  - Before: s05, s07
- [ ] **s07 · Prachurjo · planned:** Connect and verify the single historical replay control
  - How: Expose the reviewed replay preset with fixed field/history/priority, period labels and changed checks.
  - Files: prototype/, tests/
  - Verify: UI and API replay agree; no synthetic future-weather slider in MVP.
  - Before: s02
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Hla/Nadim finalize factual media in G5 while Fardin coordinates freeze and source review.

### G5 — Release the reviewed MVP and prepare submission handoff

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deliver a complete, accessible, source/rights-reviewed submission matching current official requirements.

- [ ] **s01 · Fardin · planned:** Confirm current official submission requirements
  - How: Check portal/Local Lead rules, timezone, media lengths, deadlines and fields.
  - Files: docs/SUBMISSION.md
  - Verify: Record exact source/date; independent guide numbers are not treated as final rules.
- [ ] **s02 · Fardin · planned:** Audit source, rights, AI and contribution evidence
  - How: Resolve asset/data rights and ensure all contributors/tool uses are recorded honestly.
  - Files: THIRD_PARTY_NOTICES.md, docs/AI_USE.md
  - Verify: No missing rights, fabricated citations or private information remain in the package.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Freeze and approve scientific claims
  - How: Saim/Maruf verify every numeric/crop statement; Fardin checks shipped status.
  - Files: media/claims.md, docs/VALIDATION.md
  - Verify: No planned feature or illustrative data is presented as verified functionality.
  - Before: s02
- [ ] **s04 · Fardin · planned:** Capture and edit approved media
  - How: Hla locks narration, Prachurjo supplies actual app captures, Nadim edits/subtitles/exports.
  - Files: media/, agreed media storage
  - Verify: Reviewers approve footage, consent, language, credits and format.
  - Before: s03
- [ ] **s05 · Fardin · planned:** Test public access and reproducibility
  - How: Open repo/demo as a stranger; follow documented setup and exact demo path.
  - Files: README.md, docs/SUBMISSION.md
  - Verify: Access, license, source manifests, tests and fallback behavior reproduce.
  - Before: s04, s07
- [ ] **s06 · Fardin · planned:** Record MVP release acceptance and submission handoff
  - How: Obtain independent release approval and actual main-branch evidence; prepare accurate submission package. Submit only with current authorization.
  - Files: docs/SUBMISSION.md
  - Verify: Accepted MVP release is separate from any unperformed NASA submission; public links and review evidence are real.
  - Before: s05
- [ ] **s07 · Fardin · planned:** Deploy the supported pilot with persistent evidence
  - How: When authorized, deploy frontend/backend with persistent versioned data, refresh/failure visibility and reproducible configuration.
  - Files: docs/SUBMISSION.md, src/api/, prototype/
  - Verify: Anonymous access works; restart does not silently lose scientific cache; unsupported coverage fails honestly.
  - Before: s03
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Accepted G5 establishes the MVP release gate. Future tracks still need a separate activation decision; submission remains separately authorized.

### FUT-ASSIST — Evaluate optional sourced runtime assistance

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Fardin · planned:** Define explicit new scope, useful task, tool contract and budget
  - How: After accepted G5 and explicit activation, document explicit new scope, useful task, tool contract and budget. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/agents/, docs/AI_USE.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Fardin · planned:** Implement bounded source-grounded explanation flow without scientific LLM arithmetic
  - How: After accepted G5 and explicit activation, document bounded source-grounded explanation flow without scientific LLM arithmetic. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/agents/, docs/AI_USE.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Validate unsupported-claim, privacy, offline and failure evaluation
  - How: After accepted G5 and explicit activation, document unsupported-claim, privacy, offline and failure evaluation. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/agents/, docs/AI_USE.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.

### FUT-COVERAGE — Expand reviewed regions, crops and long-duration paths

Owner: **Maruf** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Maruf · planned:** Define exact regional calendars and management horizons
  - How: After accepted G5 and explicit activation, document exact regional calendars and management horizons. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: data/catalog/, docs/DATA_SOURCES.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Maruf · planned:** Implement source-reviewed additional catalogue and coverage
  - How: After accepted G5 and explicit activation, document source-reviewed additional catalogue and coverage. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: data/catalog/, docs/DATA_SOURCES.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Maruf · planned:** Validate new representative cases and unsupported-region behavior
  - How: After accepted G5 and explicit activation, document new representative cases and unsupported-region behavior. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: data/catalog/, docs/DATA_SOURCES.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.

### FUT-DATA — Add decision-relevant NASA sources and overlays

Owner: **Saim** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Saim · planned:** Define specific IMERG/SMAP/vegetation question and product rights
  - How: After accepted G5 and explicit activation, document specific IMERG/SMAP/vegetation question and product rights. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/acquire/, src/compute/, docs/DATA_SOURCES.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Saim · planned:** Implement quality and resolution/period harmonization pipeline
  - How: After accepted G5 and explicit activation, document quality and resolution/period harmonization pipeline. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/acquire/, src/compute/, docs/DATA_SOURCES.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Saim · planned:** Validate incremental decision value, provenance and coverage checks
  - How: After accepted G5 and explicit activation, document incremental decision value, provenance and coverage checks. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/acquire/, src/compute/, docs/DATA_SOURCES.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.

### FUT-EXPERIENCE — Extend motion, voice, saved plans and browser offline UX

Owner: **Prachurjo** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Prachurjo · planned:** Define one bounded user need and device/accessibility budget
  - How: After accepted G5 and explicit activation, document one bounded user need and device/accessibility budget. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: prototype/, tests/, docs/UI_UX_SPEC.md
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Prachurjo · planned:** Implement selected rich-story, voice, calendar, saving or PWA extension
  - How: After accepted G5 and explicit activation, document selected rich-story, voice, calendar, saving or PWA extension. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: prototype/, tests/, docs/UI_UX_SPEC.md
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Prachurjo · planned:** Validate real phone/reduced-motion/offline and regression evidence
  - How: After accepted G5 and explicit activation, document real phone/reduced-motion/offline and regression evidence. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: prototype/, tests/, docs/UI_UX_SPEC.md
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.

### FUT-OPERATIONS — Evaluate a selected account, market, sensor or alert service

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Fardin · planned:** Define one selected farmer need, source permissions and operating/consent plan
  - How: After accepted G5 and explicit activation, document one selected farmer need, source permissions and operating/consent plan. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/api/, prototype/, docs/VALIDATION.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Fardin · planned:** Implement small independently scoped service with truthful inputs
  - How: After accepted G5 and explicit activation, document small independently scoped service with truthful inputs. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/api/, prototype/, docs/VALIDATION.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Validate maintenance, failure and source/financial/sensor validation
  - How: After accepted G5 and explicit activation, document maintenance, failure and source/financial/sensor validation. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/api/, prototype/, docs/VALIDATION.md, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.

### FUT-SCENARIOS — Extend stress exploration and qualified projections

Owner: **Fardin** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Fardin · planned:** Define scenario semantics and exact model/pathway/baseline/ensemble
  - How: After accepted G5 and explicit activation, document scenario semantics and exact model/pathway/baseline/ensemble. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/acquire/, src/compute/, src/api/, prototype/, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Fardin · planned:** Implement bounded extra replay or sourced projection implementation
  - How: After accepted G5 and explicit activation, document bounded extra replay or sourced projection implementation. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/acquire/, src/compute/, src/api/, prototype/, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Fardin · planned:** Validate uncertainty, comparability and non-forecast labels
  - How: After accepted G5 and explicit activation, document uncertainty, comparability and non-forecast labels. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: src/acquire/, src/compute/, src/api/, prototype/, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.

### FUT-SOIL — Research optional fertilizer and richer soil modeling

Owner: **Maruf** · State: `waiting` · Updated UTC: `2026-10-30T10:00:13Z`

**Why:** Deferred optional extension; choose and authorize a bounded implementation after accepted MVP.

- [ ] **s01 · Maruf · planned:** Define explicit optional-scope choice, actual inputs/removals and local reviewer
  - How: After accepted G5 and explicit activation, document explicit optional-scope choice, actual inputs/removals and local reviewer. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: docs/METHODOLOGY.md, src/compute/, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
- [ ] **s02 · Maruf · planned:** Implement bounded nutrient/soil model with consistent units and residue/loss accounting
  - How: After accepted G5 and explicit activation, document bounded nutrient/soil model with consistent units and residue/loss accounting. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: docs/METHODOLOGY.md, src/compute/, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s01
- [ ] **s03 · Maruf · planned:** Validate local parameterization, uncertainty and measurement-versus-budget validation
  - How: After accepted G5 and explicit activation, document local parameterization, uncertainty and measurement-versus-budget validation. Preserve MVP regression fixtures and scope only the selected extension.
  - Files: docs/METHODOLOGY.md, src/compute/, tests/
  - Verify: Evidence is real; this is deferred work, not a hidden MVP requirement.
  - Before: s02
- **Blocker:** Future only: not approved for implementation; requires explicit activation after accepted G5.
- Checks: not run; no pass claimed.
- Review: pending — no approval recorded
- Delivery: no accepted merge recorded; branch: not recorded; issue/PR: not created/recorded
- Handoff: Do not activate other future tracks automatically. Record separate evidence, tests and review for the selected extension.
