# API contract — draft for G0 review

Status: proposed contract, no endpoints implemented or technical-owner sign-off claimed. [MVP_SCOPE](MVP_SCOPE.md) governs mandatory behavior; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) contains deferred options. G0 freezes exact schemas, examples and ranking rules before G1.

## Location extension and schema v2 - 30 October 2026

Fardin authorized **INTAKE-MAP** as bounded independent local work. Either **Choose on map** or **Search district by name** satisfies location above the unchanged six ordered questions. MapLibre GL JS 6.16.0 is loaded through a lazy Next.js Client Component bridge; the reference-script interface is still mounted. The default basemap is OpenFreeMap Liberty (street/reference, not satellite). No NASA API, rotation engine, field-boundary drawing or area calculation is added.

`farmer-intake.v2` uses these location shapes:

- District search: `country_code: BD`, real `district_id`, `level: district`, `selection_method: district_search`, `coordinates: null`; provenance has `kind: farmer_selected_district`, `directory_id`, `directory_version` and source URL. Search text alone is not a selected district. It needs no map or boundary download.
- Confirmed pin: `country_code: BD`, containing `district_id`, `level: point`, `selection_method: map_pin`, `coordinates: {latitude, longitude}` with the actual user-selected numbers. Provenance has `kind: farmer_confirmed_map_pin`, boundary ID/version/SHA-256, source shape ID and URL. GeoJSON/map positions are `[longitude, latitude]`; conversion is explicit. A new/moved pin is unconfirmed until the farmer acts. Each validation resolves containment again, checking confirmation, district and boundary version. Map center never automatically becomes a selection.

Geometry is local [geoBoundaries gbOpen BGD ADM2](../data/admin/README.md), pinned at revision `9469f09`, represented year 2020 per metadata, under declared CC BY 3.0 IGO. All 64 features have explicit ID/name mappings. Display and checks share the same simplified polygons/multipolygons/holes; no separate country bounding-box mask controls acceptance. Bboxes accelerate rejection only. Exact/numerically border-touching points and overlaps are ambiguous; no containing polygon inside the dataset extent is unresolved; points beyond that extent are outside the available geometry. None is assigned to a nearest district. The numerical tolerance of 1e-9 degrees handles segment arithmetic, not source positional accuracy. Correct the pin or choose district search.

Drafts now have `locationMethod`, `districtId` and nullable `mapPin`. Switching methods clears inactive pin/district values; normalization emits only the active valid method. Other six answers and the last valid submission survive invalid edits or map failure. Existing storage key `sts-farmer-intake-v1` is deliberately retained for discovery, with **envelope version 2**. Genuine envelope-v1 answers migrate to district search and null pin, ignoring incidental coordinates. Envelope-v2 points are rechecked against local geometry on reload. If boundaries cannot load, the last submitted answers are retained as pending recheck, without claiming a freshly validated point; a later successful check restores the summary. No demo fields/preferences enter migration.

Coordinates stay in browser-local draft/submission/explicit input downloads. Map hash/URL position tracking is disabled; coordinates are not written to command logs or public field URLs. Basemap tile requests still go to the configured provider and are not an offline-browser promise. Precise pins do not change NASA grid resolution or establish scientific coverage. All successful inputs retain planning/comparison unavailable until scientific integration.

## Latest required intake — 30 October 2026

Fardin explicitly authorized **INTAKE-UI** as independent frontend/input validation work before G0 technical-owner sign-off. This section supersedes pilot-only intake and general unknown-answer wording for the six core answers. It does not accept G0, G1D, scientific rules or national advice coverage.

Location is required above one visible ordered form; either active method in the v2 extension can satisfy it. Every Bangladesh district is selectable using the local 64-district directory checked against the [Bangladesh National Portal](https://bangladesh.gov.bd/views/district-list). IDs such as `bd-district-bagerhat` are stable application identifiers, not official geocodes. Names and membership are administrative reference data, not NASA evidence. English labels are display transliterations; Bangla names follow the portal. District-search selection records `level: district`, `coordinates: null` and the source/version. Never infer farm coordinates. The original mounted reference had only an illustrative landscape; INTAKE-MAP now adds the actual map described above.

All six questions stay visible in exactly this order:

1. Current crop identity, or explicit `fallow` field state. An optional known sowing date constrains date consistency. Current and previous crop IDs may match.
2. Expected field availability: one real date or an ordered bounded window, with explicit schedule-based expectation or `farmer_estimate`. Empty fields supply their available-from date.
3. Chronological previous crop entries, each with season/start-year or start/end dates; at least one entry, or explicit `first_cultivation`. Absence of history does not establish absence of rotation risks.
4. Usual upcoming sequence, separate from history and recommendations; each segment has a crop identity or `fallow` plus period. Repeats are allowed. Alternatively explicit `no_established_rotation`, which cannot establish a complete comparison baseline.
5. Explicit `rainfed`, `limited` or `reliable` water access. Irrigated answers must state whether seasonal limitations apply; if so, name at least one affected season. No volumes are inferred.
6. Explicit `water`, `soil_rotation` or `balanced` priority, with no initial selection.

Blank, whitespace, placeholder, unknown and malformed core answers fail. Selected dependent controls must be valid. No fertilizer, pH, nutrient, organic-matter or demo-estimate controls belong to this form. Crop identities in the intake list have **not** thereby passed regional agronomic review. Soil/science evidence can still be unknown internally.

The mounted workspace imports `prototype/public/reference/intake.js` and uses its `validateAndNormalize` function. Its normalized `farmer-intake.v2` object contains separate `location`, `current`, `availability`, `crop_history`, `baseline`, `irrigation` and `priority` values. Current/baseline fallow uses a null crop ID plus an explicit domain state; absent history/baseline uses an explicit state and empty entries. Inactive controls are omitted from normalized answers. Dates use ISO calendar days; seasons use `kharif_1`, `kharif_2`, `rabi` and an integer season-start year. For chronological reporting, Rabi starts in November and Jan/Feb belong to the previous season-start year. This reporting convention is not a regional crop calendar, validated sowing interval or feasibility calculation. Date entries cannot overlap, run backwards, conflict with a known current sowing date, or place the usual future sequence before field availability. Seasonal entries provide only coarse order checks; no exact dates are inferred.

The intake has no scientific API. Successful input validation saves a browser-local submission and shows `planning.status: unavailable`, `reason: scientific_api_not_connected`, `comparison_status: unavailable`. It does not fabricate a comparison horizon, score or recommendations. A later agreed API adapter must add/confirm the common horizon, evidence and transport schema through G0/G1C/G2. This input-only JSON is not a scientific result receipt or fingerprint implementation.

Unfinished drafts and the last validated submission use the retained `sts-farmer-intake-v1` key with envelope v2 and the migration above, separately from legacy `sts-studio-v1` demo fields and homepage demo preferences. Only genuine answers in the new intake format are restored; saved submissions are revalidated. Unfinished edits cannot overwrite the last valid summary. Demonstration mode must be explicitly opened and never consumes intake answers.

## Request

- Location: a confirmed contained map pin or nationwide district selection as above; scientific pilot/coverage is assessed separately. Field: area/unit for dependent outputs, optional known soil measurements with source/date/depth/units or unknown.
- History: dated recent crops, current crop and expected harvest/field-available date. Previous/current crop IDs may match. Baseline: the farmer's usual upcoming crop/fallow segments, separate from past history.
- Common planning-horizon start/end; seasonal water access; priority preset water/soil_rotation/balanced. Optional variety, equipment restrictions, excluded crop IDs and intended crop/sowing interval.
- No compulsory fertilizer, nutrient-budget, account or AI-prompt fields. Three future main-crop steps per complete recommended alternative. Never silently compare different horizons.

## Comparison response

Proposed fields: schema_version, status, data_mode, coverage, baseline_assessment, alternatives, selected_plan_id, checks, indicators, assumptions, missing_inputs, next_information_needed, sources, catalogue_version, method_version, input_fingerprint, result_fingerprint, generated_at_utc and limitations.

- Root status: complete/incomplete/unavailable/invalid_input. Complete bundle needs an assessed baseline and at least two distinct complete alternatives on a common horizon with essential evidence. An infeasible baseline is still a valid assessed finding. Missing baseline/alternatives makes the bundle incomplete.
- Each recommended plan has its own status, plan_id, steps, feasibility/check IDs, criterion values/categories, preset rank and limits. Complete plan means exactly three chronological future main-crop steps with essential checks supported. A complete plan may appear inside an incomplete bundle; label both levels.
- Baseline segments can repeat crops or contain fallow and need not contain three crop names. Each recommended step has crop/season/variety IDs, sowing/harvest intervals, duration, transition rule IDs and sources. Never invent fillers.
- Each check has stable check/rule IDs, outcome pass/fail/caution/unknown, essentiality, EN/BN label keys, input/evidence references and source IDs. Only reviewed rules create hard exclusions. Unknown evidence is not a pass or a measured conflict.
- Indicators include explicit units/categories, period, spatial support, method and quality. Aggregate scores are optional. Missing criteria cannot be silently scored zero or reweighted away; ranking and tie-break rules are versioned.
- Scientific data_mode: cache/verified_fixture/unavailable. Acquisition may separately record historical live retrieval. Current demo constants are never verified fixtures.
- Fingerprints derive from canonical inputs and source/catalogue/method identities, excluding volatile timestamps. They support reproduction, not authentication or agronomic certification. No public field URLs or identity logging by default.

## Intended crop, replay and receipt

Intended-crop assessment reuses exactly the planner's validation/check functions. Return checks, windows and missingness; this is not diagnosis of a growing crop.

Historical replay identifies the scenario/version, periods and baseline run; holds non-climate inputs fixed; returns comparable checks and rank changes. It is neither a future forecast nor observation of historical crop failure. One reviewed preset is sufficient.

JSON download and print consume the same API result and receipt without client-side scientific recalculation. Unknowns, incomplete status, units and limitations survive export. No PDF server or cloud account required.

## Proposed routes and agreement tests

Under an agreed /api/v1 prefix: GET health, regions, crops, sources, climate/history; POST fields/validate, suitability/evaluate, rotations/generate and simulations/run. Planning returns the comparison bundle. Names remain draft. No projection/chat endpoint in MVP.

Agree typed cases for equal previous/current crops, baseline repeats/fallow, complete bundle, complete alternative in incomplete bundle, missing soil, date overlap, absent source/coverage, intended-crop parity and replay/receipt reproduction. Define errors/statuses, CORS/timeouts, request limits and canonicalization. Label synthetic contract fixtures; authentic evidence is required for scientific result tests. Consumer agreement precedes integration.
