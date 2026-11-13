# AI use and contributions

The project is now maintained by one person. Previous collaborators' work and detailed command records are preserved in [the historical ledger](archive/team-workflow/docs/AI_USE.md). Nothing in this transition reassigns their authorship or implies scientific approval.

New entries contain only actual implementation instructions and outcomes. Discussions, explanations, brainstorming and status questions are excluded. Refined English prompts are AI-written interpretations of the implementation request. Name actual tools and evidence-backed human contributions.

## FARDIN-016 — Solo UI transition — 13 November 2026

**Refined implementation instruction:** Simplify the repository for solo development, retire obsolete team gates and coordination prompts, and finish the frontend before proceeding through the remaining backend work.

**Tool and purpose:** OpenAI Codex assisted with workflow simplification and frontend implementation/verification.

**Human contribution:** The maintainer chose solo ownership, a UI-first sequence and permission to remove obsolete development coordination.

**Outcome:** Replaced active team gates with a solo UI-first checklist; archived prior records without changing their authorship. Fixed independent result requests, stale-response handling, actual-response rendering/receipts, zero/missing values and chart gaps/dates. Updated mounted frontend scripts, tests and project instructions. No scientific backend was added.

**Verification:** 51 UI tests, 66 Python tests, lint and production build passed. Mounted browser checks covered required errors, complete/incomplete fixtures, language switching, return to intake and a 390px no-overflow check. Detailed translation, full accessibility/print/touch and end-to-end real-backend verification remain open in DEVELOPMENT.md. No commit, push or deployment performed.

## FARDIN-017 — Workspace navigation and weather UI — 13 November 2026

**Refined implementation instruction:** Repair all workspace destinations and homepage navigation, run the app on localhost:3000, and integrate the current-crop vulnerability interface and weather-change story.

**Tool / purpose:** OpenAI Codex implemented and checked the existing frontend, deterministic local weather-payload build and browser flows.

**Human contribution:** The maintainer requested the routes, port, feature coverage and UI-first scope. Previous crop/data/UI contributions remain attributed in the historical ledger.

**Work completed:** Separate route views; plan snapshot persistence/export; independent what-if requests; current-crop unknown states; local NASA POWER temperature/rainfall history for 64 district selections; bilingual scrolling homepage story and source/method labels. No crop-risk threshold or agricultural score was invented.

**Verification:** 60 Node UI tests, 70 Python tests, lint and production build passed. Pinned-archive weather payload reproduced. Browser checks covered navigation/history, valid submission, example saving/reload, scenario isolation, real climate controls, EN/BN story and 390px mobile menu/layout. Remaining scientific and physical-device checks are listed in DEVELOPMENT.md. No commit, push or deployment.

## FARDIN-018 — Local data integration and output pipeline — 13 November 2026

**Refined implementation instruction:** Process and connect the collected crop evidence, NASA climate data and farmer inputs using stable identities, explicit units/periods, local persistence and reproducible output generation. Assess regression suitability and implement the supported system step by step.

**Tool / purpose:** OpenAI Codex implemented the SQLite catalogue and submission/result storage, shared server intake validation, same-origin API, historical daily weather index, canonical metric bridge, rule primitives and genuine-report UI/restoration.

**Human contribution:** The maintainer chose autonomous local implementation and requested joint preprocessing of Maruf's and Saim's data. Prior source collection and UI contributions remain attributed in the historical ledger.

**Outcome:** The system produces real, source-linked evidence reports and preserves unknowns. Original evidence bytes remain unchanged. No crop threshold, expert approval, training outcome, three-crop alternative or numerical suitability score was invented. Regression was not trained because the imported data has no suitable labelled crop outcomes.

**Verification:** 94 Python tests, 60 UI tests and 11 API integration tests passed; lint and production build passed. The 383,502-row daily NASA index matches all 2,100 annual summaries within absolute tolerance 0.001. Browser checks verified a genuine submission/report, SQLite restoration, a non-fixture JSON receipt, separate irrigation/priority scenario with explicit seasonal limits, unchanged original inputs, EN/BN report presentation and no document overflow at the tested 605px width. Local database foreign-key checks were clean. Crop rules remain inactive and full scientific planning remains incomplete. No commit, push or deployment.

## FARDIN-019 — Commit and push main — 14 November 2026

**Refined implementation instruction:** Commit the current project changes and push them to the main branch.

**Tool / purpose:** OpenAI Codex assisted with repository inspection, verification and Git delivery.

**Human contribution:** Fardin requested delivery to main.

**Scope:** Solo workflow/archive, workspace navigation and weather story, local SQLite evidence API, crop/NASA identity and metric integration, daily data indexing, tests and documentation. Scientific planning remains incomplete; no new score or recommendation is claimed.

**Verification:** Remote main had no divergent commits. make check passed (94 Python, 60 UI and 11 API tests, reproducible UI climate payload and lint); production webpack build and whitespace checks passed. Local database, cache, dependencies and private environment files are excluded from delivery.

## FARDIN-020 — Real-data QA and reliability — 14 November 2026

**Refined implementation instruction:** Audit the complete application using real NASA and crop evidence, correct functional and processing defects, remove product mock data, improve useful visualizations, verify current-crop and rotation outputs honestly, keep the Mac awake during work, then commit and push to main.

**Tool / purpose:** OpenAI Codex for code, tests, source consistency checks and Git; browser automation for mounted desktop/mobile flows; PDF extraction/rendering for original-source review. No LLM runs in the scientific application.

**Human contribution:** Fardin defined the QA scope, required real data and authorized delivery. Earlier crop collection, NASA acquisition and UI contributions remain attributed in the historical archive. No independent agronomic review is invented.

**Outcome:** Fixed unchecked-radio capture, cache invalidation and report restoration; removed public mock data and fabricated rankings; added real recent POWER observations, monthly climate comparisons, source-scoped mustard warning counts, genuine report saving and explicit input usage. Complete crop planning remains incomplete where source definitions are missing. See QA_AUDIT.md for verification and limitations.

**Verification:** Actual-project make check passed (99 Python, 63 UI, 12 API tests, deterministic climate reproduction, lint); production build passed. The 1,920 crop/district evidence-join audit passed; 252 NASA publisher samples matched, and the source PDF checksum matched. Browser district/map submission, real report saving/restoration, isolated scenarios and 390px EN/BN climate flows passed. These checks do not establish agronomic predictive accuracy.
