> Current acceptance: [QA_AUDIT](QA_AUDIT.md), 14 November 2026, supersedes the historical evidence notes below. Real reports and limited source-warning observations are implemented; complete scientific crop planning is still blocked by missing applicable rules.

# Solo development — UI first

Updated 13 November 2026. The maintainer owns all remaining work. Previous collaborators' contributions are retained. This checklist replaces task JSONs, owner handoffs and G0/G1 merge/approval gates. Tick an item only after implementation and relevant checks; report scientific or external-review limitations separately.

## 1. Finish the existing UI

- [x] Distinct workspace destinations, homepage entry and browser Back/Forward.
- [x] Labelled plan snapshot save/restore/export and separate what-if request controls.
- [x] Local NASA weather history for all 64 district selections and a homepage scrolling story.

- [x] Result adapter: independent request channels and safe invalidation/retries.
- [x] Genuine response lifecycle: loading, invalid, unavailable, incomplete and complete response presentation, ready for the future API.
- [x] Result details: zero/missing values, dynamic stage/period, source-aware labels, real-result receipts and safe errors.
- [x] Charts: actual dates/units, missing gaps, arbitrary lengths and explicit comparison availability.
- [ ] Complete EN/BN, keyboard, narrow-screen, print and reduced-motion review.
- [ ] Verify mounted homepage/workspace in a browser and record limitations.

Backend absence is expected during this phase. Real submissions stay unavailable unless an actual response is provided. Explicit development fixtures remain separate; their dates, values and crop sequences are not science. Preserve the existing visual design. Further visual changes can be made sequentially after behavior is stable.

## 2. Integrate evidence

- [x] Verify the sealed archive and build a small local historical-weather UI payload.
- [x] Index the archived daily NASA records locally and implement exact historical-window indicators.
- [ ] Define reviewed crop-stage windows and connect them to active crop rules.
- [ ] Resolve crop-rule metrics, periods, applicability and duration/operation definitions.
- [ ] Define shared IDs, units, missingness and stable response adapters.

## 3. Implement the calculations and API

- [x] Local SQLite, shared input validation, evidence joins, result persistence and source fingerprints.
- [x] Tested rule/metric/operation primitives with unknown and inactive-rule gates.
- [ ] Activate applicable reviewed crop checks and integrate full scheduling/ranking.
- [ ] Source-backed current-crop exposure checks with explicit unknowns.
- [ ] Shared-period baseline and three-step alternative scheduling/ranking.
- [ ] Intended-crop parity, historical replay, source identities and receipts.
- [ ] Connect actual responses and replace fixture-only paths where appropriate.

## 4. Verify and release

- [ ] Reproduce actual results and assess source/field applicability.
- [ ] Test whole-app offline behavior, including assets and district fallback.
- [ ] Check physical-phone/touch, EN/BN and printed/exported result parity.
- [ ] Complete source/asset rights, factual media and submission disclosure.
- [ ] Deploy/publish/submit only when authorized.

## Working rhythm

Choose one coherent change, implement it, run relevant checks, record the outcome and continue. There is no teammate approval queue. Preserve unknown scientific facts rather than inventing them to tick a box. Old task states are historical, not current product percentages. Record new AI-assisted implementation briefly in AI_USE.md; ordinary discussion is never logged.

## UI pass evidence — 13 November 2026

Passed: 51 intake/location/result Node tests, 66 Python evidence tests, frontend lint and production webpack build. Browser walkthrough checked mounted intake, required-answer errors, complete and incomplete fixtures, EN/BN switching and return to intake. At an emulated 390px width, document width and scroll width both measured 390px.

Next: finish remaining Bangla result terminology and status text, then review desktop/mobile/theme/keyboard/print/reduced-motion behavior across all result states. Physical-phone/touch, full valid-submission browser flow, print output and whole-app offline behavior were not verified in that initial pass; the later pass below verifies valid submission. The later routing/weather pass below adds the homepage descriptive-history story. Genuine-response rendering is unit-tested with supplied responses; no actual scientific endpoint is connected. These checks do not certify scientific accuracy or a finished UI.


## Routing and weather pass — 13 November 2026

The app runs at http://localhost:3000; workspace destinations use /workspace#overview, #profile, #rotations, #compare, #simulator, #climate, #saved and #methodology. They are UI destinations on one origin, not extra API servers.

Climate Insights and the homepage weather story load a 114KB static payload built reproducibly from the pinned NASA POWER archive. It covers representative grid points for all 64 district selections, with 2001–2025 annual temperature and precipitation and descriptive comparisons of 2001–2010 versus 2016–2025. Source/chart hashes, anchor distances, methods and review limits are visible. No farm average, trend significance, causation or forecast is inferred.

Browser verified: sidebar destinations, homepage/workspace entry and Back/Forward, explicit example comparison, saving and reload restoration, a complete valid district input submission, current-crop unknown state, mobile More navigation, separate what-if evaluation and temperature/rainfall controls. At 390px, the climate page had equal document/scroll widths. EN/BN story controls worked. Scientific planning remains unavailable, as expected; no example fallback was used for the genuine submission. No physical-phone, printer or full disconnected-browser certification was performed.

Next UI work: finish detailed result terminology translation and full keyboard/print/reduced-motion review; connect only accepted scientific payloads. Current-crop heat/water assessment is displayed as unassessed until reviewed stage rules and the engine exist. Intended-crop/replay calculations remain pending.

## Local output pipeline — 13 November 2026

Farmer inputs now reach `/api/plan`, are validated by the shared intake validator (including map containment), saved in SQLite, joined to matched BAMIS source calendars and NASA grid context, and returned as a persisted evidence report. Reports restore after reload and export their input/result/source fingerprints. Current intake accepts 30 label identities, including retained sesame with explicitly missing source calendars.

Source preprocessing preserves original bytes and source-table identities. Canonical SQL contains 29 crop labels, 30 intake mappings, 14 regions, 64 districts, 366 calendars, 7,834 entries, 54,838 crop-weather observations, 14 inactive candidate-evidence records, 42 NASA points and 2,100 annual summaries. The offline daily index contains 383,502 rows (four weather variables per row), verified against every annual summary.

Complete crop planning is still **not implemented**: zero active reviewed crop rules, unresolved planting/stage/operation definitions and no outcome-labelled regression training set. The returned report is real; its incomplete planning status and unknown checks are intentional. Next work is resolving the exact rule definitions listed in each report, then implementing reviewed shared-period three-crop scheduling/ranking. Do not replace this with a tuned model trained on invented labels.

Verification: 94 Python tests, 60 UI tests, 11 API integration tests, lint and production build passed. The actual database contains 383,502 daily rows and passes all 2,100 daily/annual comparisons plus foreign-key checks. Browser submission, persistent restore, real JSON export, scenario isolation/seasonal-limit follow-ups, bilingual report headings and 605px no-overflow passed. Crop recommendations remain incomplete; source-rule activation and three-step scheduling/ranking are still unchecked above.
