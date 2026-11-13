# Frontend result-workspace handoff

Status: local independent UI preparation on `main2`, 13 November 2026. The result
components and fixture states are implemented in the mounted application. No
scientific API, crop engine, reviewed crop catalogue or prepared climate package is
connected. This handoff is not teammate approval, scientific acceptance, main-branch
delivery, deployment or submission evidence.

## Mounted paths and changed surface

`/workspace` still mounts `prototype/reference/workspace-preview.html` through
`prototype/app/workspace/page.js`. The mounted controller remains
`prototype/public/reference/workspace.js`; unused React workspace components were
not rebuilt.

New mounted files:

- `prototype/public/reference/result-adapter.js`: replaceable transport boundary,
  explicit states, fixture gating, abort/generation stale-response protection.
- `prototype/public/reference/result-fixtures.js`: separate authored example inputs
  and state scenarios. It contains no NASA observations or reviewed crop advice.
- `prototype/public/reference/result-ui.js`: field summary, vulnerability,
  comparison, timeline, climate, evidence, intended-crop/replay and receipt views.
- `prototype/public/reference/results.css`: desktop, stacked mobile, print and
  reduced-motion presentation.
- `tests/result-ui.test.cjs`: adapter, fixture, cardinality, stale-response,
  vulnerability and receipt checks.

`prototype/public/reference/intake-ui.js` now exposes a copy of the last valid
submitted request to the result boundary. Genuine submissions show their summary
and an unavailable result. They never enter the fixture or legacy scorer path.

## Implemented UI behavior

The result workspace follows this order:

1. Submitted/example field summary and freshness/coverage state.
2. Current-crop historical-exposure panel with incomplete/unknown checks.
3. Baseline plus up to two distinct alternatives on one common period.
4. Expandable operations timeline with a table alternative.
5. Historical rainfall/temperature presentation with units and spatial limits.
6. Structured why/why-not checks and sources/methods drawer.
7. Intended-crop and replay surfaces that remain unavailable without real services.
8. Fixture-labelled JSON and print actions.

The complete example has an assessed infeasible baseline and two distinct complete
alternatives with exactly three future steps. The incomplete example retains one
complete alternative and visibly omits the second instead of inserting a clone.
No plan is labelled best because the fixture supplies no supported ranking.

## Fixture states

Fixture mode requires the intake screen's explicit **Open separate development
fixture** action. A sticky label remains visible and the JSON receipt repeats the
example warning. Fixture inputs never reuse a submitted field.

Available scenarios:

- `complete-comparison`
- `incomplete-one-alternative`
- `missing-climate`
- `invalid-input`
- `service-unavailable`
- `recoverable-error`

All use `data_mode: development_fixture`; fingerprints remain `null`. A failed real
request has no automatic successful fallback, and retrying the error example does
not activate another scenario.

## Adapter and proposed API needs

The adapter exposes five replaceable calls: planning, current-crop assessment,
climate history, intended-crop check and historical replay. Endpoint values are
intentionally `null`. The proposed current-crop shape is recorded in
`docs/API_CONTRACT.md`; it is not declared implemented.

Fardin needs to supply or freeze:

- request IDs, cancellation/retry behavior and final endpoint paths;
- bundle/plan statuses, common-period policy identity and assumptions identity;
- baseline assessment and distinct alternatives with operation windows;
- four indicator values/categories, units, explanations and unknown semantics;
- structured checks, translated label keys, source/rule/evidence IDs and missing
  information actions;
- canonical input/result fingerprints and generation timestamps;
- intended-crop parity and replay payloads from the same deterministic engine.

Saim needs to supply chart/history payloads rather than a public raw archive:
metric definition, values, units, LST, periods, missingness, returned-position
context, distance/spatial limitations, source metadata and reviewed period
comparison statistics. The local archive/cache was absent during this work.

Maruf needs to supply reviewed crop/system/season/variety applicability, stage and
operation rules, essentiality, source IDs and limitations. UI fixtures do not make
those rules active.

## Checks and screenshots

Passed locally:

- `node --test tests/result-ui.test.cjs` — 8/8.
- `npm run test:intake` — 31/31 existing intake/location tests.
- `npm run lint`.
- `npm run build -- --webpack` — `/` and `/workspace` built successfully.
- `node --check` for result, workspace and intake scripts.
- `git diff --check`.
- Headless Chromium production-build walkthrough — 1/1. It checked explicit
  activation, complete/incomplete/error scenarios, no automatic successful retry,
  Bangla mode, reduced motion, keyboard focus, print stylesheet, JSON label/parity,
  and a 390×844 layout with no document-level horizontal overflow.

Local evidence (not committed assets):

- `/private/tmp/soil-to-stars-result-desktop.png` — SHA-256
  `55b26ffac75ee874a1cd2ae4572f456b5234f49a4f21abec92a5fa1c12957a07`.
- `/private/tmp/soil-to-stars-result-mobile.png` — SHA-256
  `7a95a96d400eef660c4ec12126d6603699882d9b9abf229b342f5cdd95df5300`.
- `/private/tmp/soil-to-stars-result-receipt.json` — SHA-256
  `0b784dbeb62e637f45c59b05659a0c3c4e71764b4ca3e70cc865949de9abf5ba`.

The browser run used a 390 px emulated viewport, not a physical phone or touch
screen. Real map WebGL/tile failure was not rerun in this result walkthrough; the
existing intake/location regression suite passed. Print styling was inspected by
the browser test, but no physical printer/PDF viewer comparison was performed.

## Remaining gaps and recommended resolution

- Connect only accepted backend payloads; keep genuine results unavailable until
  then. Do not rename development fixtures as verified fixtures.
- Replace authored climate values with Saim's prepared chart payload through the
  adapter and rerun unit/period/source review with Saim.
- Replace fixture crop operations/checks with Fardin/Maruf payloads and perform
  plan/intended-crop parity tests.
- Complete professional EN/BN review for all detailed evidence/table terminology;
  the primary journey is bilingual, while fixture identifiers and some technical
  evidence labels intentionally remain English pending agreed translated keys.
- Run the mounted flow on a physical phone over HTTPS and test real touch/map
  behavior before claiming phone/touch verification.
- Obtain independent human review before changing G1D/G3/G3-REPORT to accepted or
  done. Their dependency gates remain unchanged.
