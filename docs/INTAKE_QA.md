# INTAKE-UI verification

**Regression note:** INTAKE-MAP subsequently changed shared location files and introduced schema/envelope v2. Earlier observations below are historical intake evidence, not proof of the new map. Current regression, provider details, browser limitations and changed files are in [LOCATION_QA](LOCATION_QA.md). Independent approval remains pending.

Scope: Fardin-authorized local intake work on 30 October 2026. The mounted `/workspace` still comes from `app/workspace/page.js` → `lib/reference.js` → `reference/workspace-preview.html`. Its `public/reference/workspace.js` imports the intake domain/UI modules. No unused React intake is substituted, dependency is added, or scientific gate accepted.

## Files changed by this task

- Runtime: `prototype/public/reference/intake.js`, `intake-ui.js`, `workspace.js`, `workspace-fixes.css`; `prototype/reference/workspace-preview.html` adds the loading/noscript state.
- Checks/onboarding: `tests/intake.test.cjs`, `prototype/package.json` (targeted test command), `prototype/README.md`.
- Requirements/source/evidence: `docs/API_CONTRACT.md`, `docs/UI_UX_SPEC.md`, `docs/MVP_SCOPE.md`, `docs/PRODUCT_SPEC.md`, `docs/DATA_SOURCES.md`, `docs/INTAKE_QA.md`.
- Records: `docs/tasks/INTAKE-UI.json`, `docs/tasks/G1D.json`, `docs/prompt_logs/fardin-0001.md`; regenerated `README.md`, `docs/PROGRESS.md`, `docs/PROMPT_LOG.md`. Existing changes elsewhere are preserved.

## Reproduce

From `prototype/`:

```bash
npm run test:intake
node --check public/reference/intake.js
node --check public/reference/intake-ui.js
node --check public/reference/workspace.js
npm run lint
npm run build -- --webpack
```

From the repository root:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/workflow.py render
python3 scripts/workflow.py check
```

## Automated evidence

The 18 Node tests use the production validator and UI controller, including their actual submit handler. They cover each required answer missing/whitespace/placeholder/malformed; every district ID; eight-division counts and source identity; no demo defaults; real calendar/leap dates; reversed/estimated windows; crop-date contradictions and chronological entries; equal previous/current crops; repeated baseline crops and fallow; empty field/first cultivation/no established rotation; seasonal irrigation dependencies; normalized provenance and unavailable status; genuine draft restoration; live-control re-reading; invalid edits preserving the last valid submission; linked errors and first-invalid focus with scrolling; EN/BN rendering and HTML escaping. The UI-controller tests use a small document/event harness, not an automated browser.

Frontend lint excludes public/reference scripts; direct Node syntax checks and the behavior tests above cover those changed scripts separately. The production build and existing 46 Python workflow tests pass; the latter validate development records, not agriculture. Final exact check records are in [INTAKE-UI](tasks/INTAKE-UI.json).

## Observed browser checks

Native Chrome was used against the loopback development server at port 3012:

- `/workspace` loaded the actual new form with location above Q1–Q6 in the required order. Crop, date mode/basis, history, baseline, water and priority began unselected; no demo coordinates/soil controls appeared.
- Empty submission displayed an adjacent error for each missing control, a linked error summary, and accessibility focus on the first invalid district control. Correcting the district then submitting left focus on the current-crop control. The initial focus implementation kept the invalid field offscreen; it was corrected to allow scrolling and covered by the automated submit test.
- Searching `বাগেরহাট` returned one district. Native keyboard selection chose `Bagerhat · বাগেরহাট`; that value remained when switching languages.
- The Bangla switch translated all six questions, absence states, notices and errors, retaining the district identity. English rendering was also observed. Native date-picker subcontrol terminology follows the browser/OS locale.
- Chrome Responsive mode at **400 × 748 CSS pixels** showed a single-column form, wrapped Bangla question/error/help text, reachable language/navigation controls and no visible form overflow in the inspected district/Q1/Q2 area. Desktop layout and dark-mode errors were also inspected. This is browser emulation, not a physical-device or full assistive-technology review.

Valid submission/summary, invalid live edits and preservation of the previous validated submission are verified by the UI-controller tests. A complete successful browser-submission walkthrough and physical-phone review are not claimed; Prachurjo's independent review should include them. Browser connector access was unavailable, so the browser observations used native Chrome controls rather than a Playwright run.

## Remaining dependencies and limits

- The [district directory source](https://bangladesh.gov.bd/views/district-list) is integrated only as local administrative reference data, checked on 30 October 2026. It includes no farm coordinates, boundaries or scientific coverage. The old reference had an illustrative landscape, not a real map; no live map is added or removed.
- Seven intake crop identities are not a source-reviewed national agronomic catalogue. Farmers with an unlisted crop are told to retain a draft rather than guess another identity. Season/year reporting supports coarse chronology; exact sowing windows and feasibility remain scientific work.
- G0 technical-owner agreement, G1A NASA acquisition/QA, G1B crop-rule review, G1C API transport/validation, G2 engine and G3 scientific integration remain pending. No common scientific comparison horizon is invented by the intake. No NASA, agronomic, nutrient, runtime AI or rotation model is implemented here.
- The saved/exported object is input-only `farmer-intake.v1`, with planning/comparison unavailable. It is not the G3-REPORT scientific receipt. District selection does not establish advice availability nationwide. Unknown scientific evidence stays unknown.
- Genuine intake storage is `sts-farmer-intake-v1`; legacy demo storage and homepage demo preferences do not populate it. One unfinished draft and the last validated submission are retained. Browser storage is local to an origin/device, and failures are surfaced. Test-origin answers on port 3012 are browser-local QA data.
- Independent human review and accepted main-branch delivery remain outstanding. No commit, push, merge or deployment was performed at the original intake handoff. Later authorized feature-branch delivery is tracked by DELIVERY-INTAKE.

Command log: `P-40f8b1c01bd7` (one Fardin implementation instruction). Existing unassigned entries and discussions are unchanged.
