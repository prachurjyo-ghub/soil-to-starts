# Real-data QA — 14 November 2026

The application generates real local evidence reports. It is **not yet a validated crop recommendation engine**. Source consistency, calculation correctness and agricultural predictive accuracy are different checks. No field outcome dataset, independent agronomic acceptance or prediction accuracy percentage is available.

## Findings and fixes

| Finding | Resolution |
| --- | --- |
| Unchecked radio controls overwrote explicit farmer answers during submit | Capture only checked radio values; regression test covers untouched required choices. |
| Crop/source refresh could erase an independently verified daily weather index | Preserve daily records when archive/grid identities are unchanged; regression test also preserves private submissions. |
| Product shipped fabricated example crop plans, weather summaries and rankings | Removed the public fixture dataset and legacy mock planner/components. Isolated synthetic test fixtures remain under tests only. No failure opens a mock result. Old example snapshots are rejected on restore. Decorative landscape illustrations remain labelled. |
| A valid input summary misleadingly said Incomplete | Separate Inputs validated and Evidence report ready from incomplete scientific planning. |
| Recent observations absent | Added checksum-pinned offline POWER observations for 2026-01-01–2026-11-12. All four parameters are complete through 2026-11-10 across mapped points; later source fills remain null. No request downloads data. |
| Climate changes hidden by annual averages | Added paired monthly comparisons for 2001–2010 and 2016–2025, with shared scales, accessible values and coverage tables. |
| No useful current-crop weather calculation | Added strictly scoped observed warning-level counts for mustard in the BAMIS Dhaka source region, based on a visually checked original PDF. Other crop/region combinations remain unavailable. This is not crop damage, suitability, live diagnosis or future risk probability. |
| Saved page required a complete alternative even when only a real evidence report existed | Genuine evidence reports can be saved, restored and exported independently of future plans. |
| Direct comparison navigation did not restore a previous report | Attempt the same immutable API restoration on all workspace routes. |
| Intended-crop control listed only three hardcoded crops and claimed no endpoint | Uses canonical crop identities and checks the collected regional evidence inventory. Planting feasibility remains explicitly unassessed. |
| Some inputs appeared to influence scores when no scoring rules existed | Added an input-usage ledger: district/crop/date joins are used; irrigation, history and priorities are preserved but not scored without applicable rules. |

## Data evidence

- 383,502 archived daily grid rows (2001–2025); all 2,100 annual summaries reproduce within absolute tolerance 0.001.
- 13,272 recent daily grid rows, four parameters, 42 representative grid points; total 396,774 date/grid rows. Zero rainfall remains zero; source fill values remain missing.
- Independently re-downloaded NASA T2M/PRECTOTCORR for predeclared dates 2001-01-01, 2020-06-15 and 2025-12-31: **252/252** mapped observations agree within 0.001. This sample does not independently verify every source value or field accuracy. See [publisher receipt](../data/qa/publisher_verification.json).
- The original [BAMIS Dhaka mustard PDF](https://www.bamis.gov.bd/res/public/calendars/2019/12/30/10981.pdf) matches its preserved SHA-256. Page 1 Weather Warning gives daily maximum >30°C, daily minimum <10°C and rainfall >50 mm/day. Exact boundary equality is not an exceedance. Favorable-weather and disease rows are not substituted. See [warning reference](../data/rules/exposure_references.json).
- Exhaustive identity audit of 64 districts × 30 intake crop labels = **1,920** requests against actual local evidence: 1,266 have matching calendars; 654 do not. None borrow another region. Eight district/crop pairs have the source-scoped mustard warning comparison. Offline assessment network calls were blocked. See [coverage receipt](../data/qa/coverage_matrix.json).
- 29 collected crop labels, 366 source calendars, 7,834 calendar entries and 54,838 normalized weather-context observations are preserved. Multiple regional/seasonal source tables are not incorrectly deduplicated into universal crop rules. Sesame is retained as an intake identity with no fabricated collected evidence.

## What remains scientifically blocked

There are **zero active reviewed planning rules**. Printed BAMIS weather normals are not crop tolerance labels; the printed life span does not establish sowing/maturity/final-harvest/field-clearance events. Generic rice does not identify Aus/Aman/Boro. Stage-specific water/soil needs, planting-window definitions, preparation/harvest/clearance durations, applicable rotation restrictions and ranking policy remain unresolved.

Consequently the application cannot truthfully supply a complete baseline plus two distinct three-crop alternatives, calibrated vulnerability score, intended-crop suitability, or historical plan replay. These remain explicitly incomplete. A regression model cannot create missing crop outcome labels. Adding arbitrary thresholds or three filler plans would reduce reliability.

Next scientific work: curate a small event-defined crop/variety/season catalogue with exact source pages and local agronomic validation; exercise the deterministic checks against independent cases; then connect scheduling, constraint rejection and shared-horizon ranking. Never infer expert approval from this QA pass.

## Reproduce

```sh
make backend
make check
make build
python3 -B scripts/qa_coverage_matrix.py
# Optional explicit acquisition/verification, requiring internet:
python3 -B scripts/qa_verify_sources.py --live
python3 -B scripts/acquire_recent_power.py --start 20260101 --end 20261112
```

Acquisition is separate from serving the application. Recent observations are a dated snapshot, not a live feed. Private SQLite records and downloaded QA raw responses stay ignored. Test-only inputs and thresholds are not product datasets.

Browser and final verification results are recorded below after execution. Physical devices, printed-page rendering, agricultural outcomes, asset rights and public hosting are separate acceptance work; no blanket certification is claimed.

## Executed verification

- Actual project `make check`: **99 Python + 63 UI + 12 API tests passed**, reproducible climate payload passed, ESLint passed. Production webpack build passed.
- Real database setup/import passed; 396,774 daily rows and all existing three submissions/results retained. Historical annual parity still passes after the recent data extension.
- Browser: required errors, explicit district selection, complete real-data evidence report, observed mustard warning counts (2026-11-01–10), report save/reload, scenario with explicit irrigation limits, original-input isolation, map readiness/pin containment/confirmation and map-based submission passed in the isolated local QA instance.
- EN/BN climate controls and monthly charts checked at 390px; report/scenario disclosure overflow was found and fixed. Rechecked report document width = viewport width = 390px.
- Final localhost:3000 climate route and homepage load real local charts with no observed console errors. All eight workspace destinations have automated rendering coverage. No server-side NASA fetch is used.
- Private SQLite/cache/environment files are excluded from Git. Full disconnected-browser/assets certification, physical phone/touch, printer output, independent field outcomes and agronomic validation were not completed. External basemap/fonts may still need internet; district search and scientific processing use local data.

The Mac's caffeinate assertion was verified during the task. This log records implementation and verification, not ordinary AI discussion.
