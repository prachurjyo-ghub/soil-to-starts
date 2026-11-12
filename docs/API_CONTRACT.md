# API contract — draft for G0 review

Status: **G0-CONTRACT/s01 draft, 1 November 2026 — ready for technical review after the recorded checks.** Field names and examples below are proposals, not a frozen schema; no endpoints, scientific acquisition or technical-owner sign-off are claimed. [MVP_SCOPE](MVP_SCOPE.md) governs mandatory behavior; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) contains deferred options. Saim, Maruf and Prachurjo still review s02–s04; s05 freezes the agreed contract and s06 records independent review/main-branch acceptance before G1 implementation. This draft does not unlock those gates.

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
2. Expected field availability: one real date or an ordered bounded window, with explicit `expected` or `farmer_estimate` basis. **Available means the current crop has been harvested and removed, so preparation for the next crop can begin**, rather than biological maturity or final harvest alone. Empty fields supply their available-from date. Preserve the existing v2 literal `applies_to: after_harvest` with this meaning.
3. Chronological previous crop entries, each with season/start-year or start/end dates; at least one entry, or explicit `first_cultivation`. Absence of history does not establish absence of rotation risks.
4. Usual upcoming sequence, separate from history and recommendations; each segment has a crop identity or `fallow` plus period. Repeats are allowed. Alternatively explicit `no_established_rotation`, which cannot establish a complete comparison baseline.
5. Explicit `rainfed`, `limited` or `reliable` water access. Irrigated answers must state whether seasonal limitations apply; if so, name at least one affected season. No volumes are inferred.
6. Explicit `water`, `soil_rotation` or `balanced` priority, with no initial selection.

Blank, whitespace, placeholder, unknown and malformed core answers fail. Selected dependent controls must be valid. No compulsory fertilizer, pH, nutrient, organic-matter or demo-estimate controls belong to the six core questions. Short conditional follow-ups may collect a fact required by a reviewed rule; soil reports stay optional and scientific unknowns stay explicit. Crop identities in the intake list have **not** thereby passed regional agronomic review. Soil/science evidence can still be unknown internally.

The mounted workspace imports `prototype/public/reference/intake.js` and uses its `validateAndNormalize` function. Its normalized `farmer-intake.v2` object contains separate `location`, `current`, `availability`, `crop_history`, `baseline`, `irrigation` and `priority` values. Current/baseline fallow uses a null crop ID plus an explicit domain state; absent history/baseline uses an explicit state and empty entries. Inactive controls are omitted from normalized answers. Dates use ISO calendar days; seasons use `kharif_1`, `kharif_2`, `rabi` and an integer season-start year. For chronological reporting, Rabi starts in November and Jan/Feb belong to the previous season-start year. This reporting convention is not a regional crop calendar, validated sowing interval or feasibility calculation. Date entries cannot overlap, run backwards, conflict with a known current sowing date, or place the usual future sequence before field availability. Seasonal entries provide only coarse order checks; no exact dates are inferred.

The intake has no scientific API. Successful input validation saves a browser-local submission and shows `planning.status: unavailable`, `reason: scientific_api_not_connected`, `comparison_status: unavailable`. It does not fabricate a comparison horizon, score or recommendations. A later agreed API adapter must preserve this input, resolve scientific coverage and automatically select a shared comparison period through a versioned regional policy before ranking, through G0/G1C/G2. The farmer does not supply a fixed comparison duration; the exact regional policy awaits Maruf’s review. This input-only JSON is not a scientific result receipt or fingerprint implementation.

Unfinished drafts and the last validated submission use the retained `sts-farmer-intake-v1` key with envelope v2 and the migration above, separately from legacy `sts-studio-v1` demo fields and homepage demo preferences. Only genuine answers in the new intake format are restored; saved submissions are revalidated. Unfinished edits cannot overwrite the last valid summary. Demonstration mode must be explicitly opened and never consumes intake answers.

## Coverage and catalogue proposal

All **64 Bangladesh districts remain selectable** by the existing confirmed map-pin and independent district-search methods. Selection is administrative coverage. A recommendation requires reviewed applicability for the **crop × production/calendar season × variety × scientific region**, together with essential field facts and climate evidence. District names or precise coordinates do not establish that applicability or field-resolution soil measurements. A scientific region may cover only part of a district; a district-only answer is insufficient when its applicable region cannot be resolved without guessing.

Initial **data-audit targets**, using proposed crop IDs: `rice`, `mustard`, `maize`, `potato`, `wheat`, `mungbean`, `lentil`, `onion`, `garlic`, `groundnut`, `chilli`, `jute`. Audit rice separately as **Aman, Boro and Aus**; begin with a small reviewed selection of varieties for each supported region. The first active pilot region and varieties are not selected by this document. These are catalogue targets, not claims of downloaded data, completed agronomic review or nationwide recommendation readiness. Full acquisition/QA belongs to **G1A/G1B**, after G0 acceptance.

Current intake v2 exposes only `rice`, `maize`, `lentil`, `mustard`, `mungbean`, `sesame`, `jute`. Retain these existing IDs, including sesame; an intake option is not scientific approval. Do not silently add the other targets to the current UI or infer Aman/Boro/Aus from `rice`, dates or the reporting season. Unsupported crop/season/variety/region combinations get explicit coverage reasons. A farmer must never choose an incorrect listed crop to continue; free-text names are farmer reports, not scientific evidence.

## Stable identities, dates and missingness — proposed

Identifiers are immutable application keys, separate from translated display names. Correct aliases through a versioned mapping; never recycle a key. Every result records the registry/catalogue versions used. Proposals below do not assert that a scientific registry exists yet.

| Entity | Proposed representation | Boundary |
| --- | --- | --- |
| Field | `field-<opaque-token>` | Browser/request-local identity, not ownership, a cadastral boundary or an account; no coordinates encoded in it. |
| Crop | Existing intake IDs above; proposed targets retain simple IDs such as `potato` | Species/crop identity alone does not identify a rice system or variety. |
| Calendar season | Preserve `kharif_1`, `kharif_2`, `rabi` plus integer season-start `year` | Coarse farmer reporting, not a planting window. |
| Rice production season | `rice-aman`, `rice-boro`, `rice-aus` in `rice_system_id` | Separate from calendar season; null with missingness until known. Non-rice uses explicit not-applicable. |
| Variety | `bd-variety-<registry-slug>` plus registry version | No named real variety is assigned here; no automatic generic-variety fallback. |
| Administrative region | Existing `bd-district-*` | Keep directory/boundary provenance from intake v2. |
| Scientific region | `bd-region-<reviewed-slug>` plus region-definition version | Requires an explicit reviewed definition/spatial support; do not guess pilot membership. |
| Source / evidence | `source-<provider>-<resource>` plus version; `evidence-<artifact>` plus checksum | Source identity differs from a particular downloaded/processed artifact. |
| Rule | `rule-<domain>-<slug>` plus version | Applicability, essentiality, source links and review status accompany executable rules. |
| Plan / step / check | Request-scoped `plan-*`, `step-*`, `check-*` | Stable within a result; IDs do not imply validation. |

Dates are real ISO `YYYY-MM-DD` calendar days in Bangladesh (`Asia/Dhaka`), not UTC instants; `generated_at_utc` is a separate RFC 3339 instant. A date window is inclusive and ordered. Example response event windows use `{earliest, latest}`; null means unresolved, never a fabricated date. Duration ranges use `{min, max, unit: day, from_event, to_event}` with reviewed source/rule IDs. State whether the origin is **sowing or field transplanting**, and whether the endpoint is maturity or final harvest. Preserve `current.sown_on` as reported: v2 does not distinguish nursery sowing from transplanting; request clarification when that affects a rule.

Every scientific numeric value needs an explicit unit (for example `mm` for rainfall, `degC` for temperature, `cm` for observation depth), temporal period, spatial support, method, QA and provenance. These unit tokens are a draft vocabulary; Saim reviews exact climate parameter/time/aggregation conventions. Area/unit remains optional unless an output depends on it; do not invent local conversions. No NaN, infinity, sentinel zero, empty string or string `unknown` stands in for a numeric observation.

Use `null` plus a `missing_reason` such as `not_reported`, `not_acquired`, `not_reviewed`, `unsupported` or `not_applicable`; omission means an optional field was not supplied, not a default observation. A real zero remains zero. Empty arrays mean no entries in the named explicit state, not successful assessment. Preserve `fallow`, `first_cultivation` and `no_established_rotation` as distinct farmer answers. Missing optional facts can remain unknown; missing **essential** evidence prevents completeness. A soil report is optional even when an unanswered essential soil check leaves a plan incomplete.

## Proposed API adapter, without application changes

The future `rotation-request.draft-01` envelope contains:

- `request_id`, `field_id`, and `intake`: preserve the exact normalized `farmer-intake.v2` object. Its local `planning: unavailable` marker is input provenance, not a server calculation or client authority over the response status.
- `crop_context`: optional records addressed by `input_path` relative to intake, such as `/current` or `/baseline/segments/0`, adding `rice_system_id`, `variety_id` and explicit missingness. Never overwrite the original reported crop ID or infer a variety. Context must agree with the referenced slot.
- `field_observations`: optional, rule-linked follow-up answers with a fact key, value/unit, observation date/depth where relevant and provenance (`farmer_reported`, `measured_report` or explicitly separate regional estimate). Report/source references do not turn farmer observations into measurements. A follow-up names the actual reviewed rule and explains why the fact is needed.
- No caller-selected period end, fixed duration, thresholds or preference weights. The server resolves a versioned regional comparison policy and shared assumptions. Optional intended-crop/replay inputs remain separate uses of the same engine.

**Proposed unsupported-name path:** `intake.schema_version: farmer-intake.crop-report.draft-01` is a separate future extension, not existing v2 behavior. Keep the six answer groups/order and their absence states; a crop slot may have `identity_state: unmapped`, `crop_id: null` and a nonblank `reported_crop_name`. For a mapped slot, preserve a registry crop ID. Apply the same approach to history/baseline crop slots. Never pass an unmapped slot to the v2 validator or replace it with a different crop. The current UI cannot emit this extension; Prachurjo/Fardin must agree its controls, validation and migration before implementing it in G1. Unmapped names produce `unsupported_crop` coverage findings, not recommended crops. Malformed names/slots remain input errors.

Short conditional follow-ups appear only when a reviewed rule needs them. Keep the six core questions visible and ordered; do not add a compulsory soil-report form. Return stable rule/reason IDs and the specific missing fact in `next_information_needed`. User text is escaped in EN/BN presentation and excluded from public logs. Coordinates remain within the explicitly submitted request/result scope, not command records or public field URLs; future server transport/log-retention handling requires technical agreement.

## Scheduling and the shared comparison period

A crop step accounts for **preparation → planting → growth → harvesting → collection → field clearance**, plus the reviewed transition to the next crop. Distinguish physiological maturity, final harvest and the date the field is clear for preparation. A duration to maturity cannot silently substitute for duration to clearance. Each scheduled step records:

- `crop_id`, calendar season/year, `rice_system_id` where applicable, variety and scientific-region IDs/versions.
- `operations`: operation ID/type, start/end event windows, duration basis/range, source/evidence/rule IDs and assumptions. Types include preparation, sowing/transplanting, growth, harvesting, collection, clearance and transition.
- `maturity_window`, `final_harvest_window`, `field_clearance_window`, and check/transition-rule IDs. All essential windows and checks must be supported before a step is part of a complete plan.

Do not add an invented universal preparation gap. Reviewed sources may include harvest/collection/clearance inside a stated duration; record the included operations and any overlap/precedence rule so they are counted once. A transition records whether it is already covered by preceding clearance or following preparation. Work on nursery seedlings may overlap field occupation only under a sourced rule and explicit field/transplanting assumptions. Unsupported overlap is not assumed feasible.

Availability windows remain uncertain windows. Do not silently pick the earliest day, average durations or use the optimistic endpoints. Maruf reviews range propagation and whether feasibility must hold across the full reported range or depends on an explicit conditional date. If resolving uncertainty requires a farmer answer, keep the affected check incomplete. Dates crossing years and leap days must remain chronological.

Before generating/ranking competing plans, automatically choose **one shared comparison period** using an agreed, versioned **regional policy**, independent of which candidate would score best. Record `comparison_period: {status, policy_id, policy_version, region_id, start, end, input_refs, assumptions}`. The root comparison period and `environmental_assumptions_id` (field facts, water assumptions, historical climate period/method/evidence) apply to every baseline/alternative by inheritance. Any explicit child references must match them; a different period or assumptions object requires a new comparison. Freeze the period/assumptions for the whole comparison; changing a priority may change order, not retrospectively change the period to favor a plan.

**Pending Maruf:** exact period-selection rule, treatment of the availability window, regional season boundaries and policy inputs. Do not invent a fixed 12- or 18-month duration. Until a reviewed applicable policy can provide dates, return a `comparison_period` object with `status: unavailable`, null dates and a `missing_reason`; do not rank or claim a complete comparison. The planning period is distinct from the historical climate evidence period.

Each plan reports its own `completion_window` (final crop's field-clearance window; an exact `completion_date` only when resolved). Plans must fit the common period; changing their end dates cannot change that period. Report remaining `unallocated_intervals` separately. Unplanned time is **not automatically fallow, bare soil, cover or soil improvement**. Explicit farmer baseline fallow is a reported practice with its own dates/assumptions. No plan is padded with invented crops or fallow to fill a slot.

## Comparison response and status semantics

Proposed response envelope: `schema_version: rotation-comparison.draft-01`, `request_id`, `status`, `data_mode`, `coverage`, `comparison_period`, `environmental_assumptions_id`, `baseline_assessment`, `alternatives`, `checks`, `indicators`, `missing_inputs`, `next_information_needed`, `sources`, `evidence`, `versions`, fingerprints, UTC generation time and limitations. No endpoint returns invented science when a dependency fails.

| Level | Meaning |
| --- | --- |
| Bundle `status` | `complete` only when the baseline is assessed and **two distinct complete alternatives** share the same period/environmental assumptions and essential evidence. An infeasible baseline can be assessed and retained. |
| Baseline `status`, `assessed`, `feasibility` | Separate evidence sufficiency from feasibility (`feasible`, `infeasible`, `undetermined`). Baseline repeats/fallow are allowed; it need not contain exactly three crops. A fully assessed infeasible baseline can have `status: complete`, `assessed: true`, `feasibility: infeasible`. |
| Alternative `status`, `feasibility` | `complete` requires **exactly three chronological future main-crop steps**, all essential evidence/checks and feasible timing/constraints. Three steps need not have three different crop IDs. Keep rejected candidates/reasons in the check ledger; an excluded candidate never becomes a complete recommended alternative. |
| `incomplete` at any applicable level | A usable supported assessment exists, but essential answers/checks, a baseline or enough alternatives are missing. Preserve supported findings and identify the gaps. A complete plan may appear inside an incomplete bundle. |
| `unavailable` | Required coverage, evidence or a reviewed policy is absent so the relevant scientific assessment cannot be provided. Partial supported findings elsewhere survive; use the broadest level actually affected. |
| `invalid_input` | Malformed, contradictory or uninterpretably structured input, with field-specific errors. Scientific unknowns and correctly reported unsupported names are not malformed input. |

Evaluation order: validate input → resolve evidence/coverage and regional period policy → assess essential soil/water/season/date/sequence constraints → generate supported chronological candidates and baseline → derive indicators → rank only eligible comparable alternatives using agreed rules. All relevant fail/unknown reasons remain visible; an early missing item must not erase already supported checks. No hard failure or essential unknown can be overcome by preferences.

Two alternatives must differ substantively in their sourced crop/system/variety sequence or schedule; renaming/cloning a plan or adjusting a display score does not establish distinctness. Exact distinctness, preset ordering and deterministic tie-breaking require Fardin/Maruf agreement at s05. Combined scoring formulas, normalization and weights remain **pending technical agreement**; do not implement or imply an agreed total. When ranking policy is unavailable, `ranking.status: unavailable`, ranks/selected plan are null, and the overall comparison cannot claim a completed recommendation.

Scientific `data_mode` is `cache`, `verified_fixture` or `unavailable`; verified fixtures require authentic, reviewed evidence and provenance, never merely synthetic contract JSON or current demo constants. Acquisition may separately record historical live retrieval; requests/compute use checked local evidence. `OFFLINE=1` and a fully offline browser are still planned/testable behaviors, not implemented promises in this draft.

### Four primary explained indicators

Return the four keys for each assessed baseline/plan, even if their values are unknown. An indicator contains `status`, categorical/quantitative `value` and `unit`, `explanation_key` plus EN/BN label keys, check/rule/source/evidence IDs, period, spatial support, method/version, QA/missingness and limitations. Unknown indicators retain null values with the essential evidence gap, never zero or a silently reweighted score.

| Key | What it can explain | Review required |
| --- | --- | --- |
| `historical_climate_fit` | Fit to the stated historical temperature/rainfall record and reviewed crop-stage/calendar constraints | Saim's periods, units, aggregation, QA and missingness; Maruf's applicable crop/variety rules. No future weather or success probability. |
| `water_compatibility` | Reviewed crop water requirements against explicit seasonal water access and relevant evidence | Maruf/Saim review qualitative or quantitative method; do not infer irrigation volume or water saved. |
| `rotation_compatibility` | Sourced sequence/family/host constraints and supported management compatibility | Maruf reviews history sufficiency and rules; no nutrient depletion or measured soil restoration. |
| `timing_feasibility` | Sourced chronological operation windows, transitions and clearance within the common period | Maruf reviews duration origins/ranges, operations and uncertainty; no invented universal gap. |

A check uses `outcome: pass|fail|caution|unknown`, `essential`, stable reason/rule IDs, input references, explanation/EN-BN keys, source/evidence references and limitations. Only a reviewed applicable rule can prove an agronomic exclusion. `unknown` is neither a pass nor a proven conflict. Farmer reports, observations, historical grid context and any future projection are distinct provenance kinds. NASA grids do not measure exact field pH or nutrients. No yields, future-weather predictions, success percentages, nutrient balances or measured soil-restoration numbers belong in these outputs.

Every scientific source/evidence record needs source/version/URL, artifact/checksum, units, period and spatial support, processing method/version, QA/missingness, applicability/review status and limitations. Rule records add exact crop/season/variety/region applicability and review evidence. Source names/URLs alone cannot establish review. Catalogue, source, method, region and period/ranking-policy identities belong in `versions`. Canonical request and evidence/version identities underpin input/result fingerprints; exclude volatile timestamps. Null until implemented; no dummy hash or scientific-certification claim.

## Synthetic contract examples — payload shape only

**Every JSON block below is synthetic.** Dates are fictional farmer answers or test dates, not Bangladesh planting advice. `synthetic-*` references are deliberately non-production: no data have been acquired or reviewed by these examples. Do not import these blocks as verified scientific fixtures. `case_id`, `synthetic`, `request`, `response` and any `request_changes` are documentation fixture wrappers; only the embedded request/response are proposed API payloads. Syntax checks do not validate agronomy, a frozen schema or endpoint behavior.

### A. Normal current intake, including equal previous/current crop IDs

A valid v2 intake can be saved today, but the scientific API and regional policy are not connected. This normal input therefore has an honest **unavailable** scientific response. There is no complete scientific result implied by a locally valid form. The existing local form still emits its own input summary, rather than this proposed server envelope.

```json
{
  "case_id": "normal-v2", "synthetic": true,
  "request": {
    "schema_version": "rotation-request.draft-01", "request_id": "synthetic-request-a", "field_id": "field-synthetic-a",
    "intake": {
      "schema_version": "farmer-intake.v2",
      "location": {"country_code": "BD", "district_id": "bd-district-bagerhat", "level": "district", "selection_method": "district_search", "coordinates": null, "provenance": {"kind": "farmer_selected_district", "directory_id": "bd-national-portal-districts-2026-10-30", "directory_version": "2026-10-30", "source_url": "https://bangladesh.gov.bd/views/district-list"}},
      "current": {"state": "growing", "crop_id": "rice", "sown_on": "2026-07-01"},
      "availability": {"kind": "window", "start": "2026-11-15", "end": "2026-11-22", "basis": "farmer_estimate", "applies_to": "after_harvest"},
      "crop_history": {"state": "entries", "entries": [{"kind": "crop", "crop_id": "rice", "period": {"kind": "season_year", "season_id": "kharif_2", "year": 2025}}], "provenance": "farmer_reported", "rotation_risks_assessed": false},
      "baseline": {"state": "sequence", "segments": [{"kind": "crop", "crop_id": "mustard", "period": {"kind": "dates", "start": "2026-11-23", "end": "2027-02-23"}}, {"kind": "fallow", "crop_id": null, "period": {"kind": "season_year", "season_id": "kharif_1", "year": 2027}}, {"kind": "crop", "crop_id": "rice", "period": {"kind": "season_year", "season_id": "kharif_2", "year": 2027}}], "provenance": "farmer_reported", "assessed": false},
      "irrigation": {"access": "limited", "seasonal_limitations": "seasonal", "limited_seasons": ["rabi"]},
      "priority": "balanced",
      "planning": {"status": "unavailable", "reason": "scientific_api_not_connected", "comparison_status": "unavailable"}
    },
    "crop_context": [{"input_path": "/current", "rice_system_id": null, "variety_id": null, "missing_reason": "not_reported"}],
    "field_observations": []
  },
  "response": {
    "schema_version": "rotation-comparison.draft-01", "request_id": "synthetic-request-a", "status": "unavailable", "data_mode": "unavailable",
    "coverage": {"district_id": "bd-district-bagerhat", "region_id": null, "status": "unavailable", "reason_ids": ["scientific_coverage_not_reviewed"]},
    "comparison_period": {"status": "unavailable", "policy_id": null, "policy_version": null, "region_id": null, "start": null, "end": null, "input_refs": ["/intake/availability"], "assumptions": [], "missing_reason": "not_reviewed"},
    "environmental_assumptions_id": null,
    "baseline_assessment": {"status": "unavailable", "assessed": false, "feasibility": "undetermined"},
    "alternatives": [], "checks": [], "indicators": [], "sources": [], "evidence": [],
    "missing_inputs": [{"input_path": "/crop_context/0/rice_system_id", "essential": true, "missing_reason": "not_reported", "essentiality_note": "Unresolved applicability; no rice-system rule is selected."}],
    "next_information_needed": [{"reason_id": "scientific_api_not_connected", "owner": "Fardin", "action_key": "await_reviewed_contract_and_evidence"}],
    "ranking": {"status": "unavailable", "selected_plan_id": null},
    "versions": {"contract": "draft-01", "catalogue": null, "method": null}, "input_fingerprint": null, "result_fingerprint": null,
    "limitations": ["No reviewed regional policy, catalogue or scientific result is established by this example."]
  }
}
```

### B. Incomplete assessment with supported partial findings

For compactness this fixture defines a **full request by deterministic substitution**: copy A's embedded request, replace `request_id`, and replace only the paths in `request_changes` (JSON Pointer paths, not an API patch endpoint). This rule applies to C and D too; no scientific values are defaulted. B exercises explicit absence states and a hypothetical partial response **assuming** a reviewed local calendar/period policy exists later. The `synthetic-*` evidence pointer is only a shape stub. It cannot pass a production evidence gate; source/evidence records are omitted here and must be resolved in a real response.

```json
{
  "case_id": "incomplete", "synthetic": true,
  "request_changes": {
    "/request_id": "synthetic-request-b",
    "/intake/current": {"state": "fallow", "crop_id": null, "sown_on": null},
    "/intake/availability": {"kind": "date", "start": "2026-11-15", "end": "2026-11-15", "basis": "farmer_estimate", "applies_to": "available_from"},
    "/intake/crop_history": {"state": "first_cultivation", "entries": [], "provenance": "farmer_reported", "rotation_risks_assessed": false},
    "/intake/baseline": {"state": "no_established_rotation", "segments": [], "provenance": "farmer_reported", "assessed": false},
    "/crop_context": []
  },
  "response": {
    "schema_version": "rotation-comparison.draft-01", "request_id": "synthetic-request-b", "status": "incomplete", "data_mode": "cache",
    "comparison_period": {"status": "complete", "policy_id": "synthetic-regional-policy", "policy_version": "shape-only", "region_id": "synthetic-region", "start": "2026-11-15", "end": "2027-10-31", "input_refs": ["/intake/availability"], "assumptions": ["Synthetic policy output; not an agreed regional duration."]},
    "environmental_assumptions_id": "synthetic-assumptions-b",
    "baseline_assessment": {"status": "incomplete", "assessed": false, "feasibility": "undetermined", "reason_ids": ["no_established_rotation"]},
    "alternatives": [{"plan_id": "synthetic-partial-plan", "status": "incomplete", "feasibility": "undetermined", "steps": [], "completion_window": null, "completion_date": null, "unallocated_intervals": [], "check_ids": ["check-timing-b", "check-soil-b"], "indicator_ids": ["indicator-climate-b", "indicator-water-b", "indicator-rotation-b", "indicator-timing-b"], "rank": null}],
    "checks": [
      {"check_id": "check-timing-b", "rule_id": "synthetic-calendar-rule", "rule_version": "shape-only", "outcome": "pass", "essential": true, "explanation_key": "timing.supported_window", "label_keys": {"en": "timing.supported_window.en", "bn": "timing.supported_window.bn"}, "source_ids": ["synthetic-calendar-source"], "evidence_ids": ["synthetic-calendar-evidence"]},
      {"check_id": "check-soil-b", "rule_id": "synthetic-soil-rule", "rule_version": "shape-only", "outcome": "unknown", "essential": true, "input_refs": ["/field_observations"], "explanation_key": "soil.essential_fact_missing", "label_keys": {"en": "soil.essential_fact_missing.en", "bn": "soil.essential_fact_missing.bn"}, "source_ids": ["synthetic-rule-source"], "evidence_ids": [], "missing_reason": "not_reported"}
    ],
    "indicators": [
      {"indicator_id": "indicator-climate-b", "key": "historical_climate_fit", "status": "unavailable", "value": null, "unit": null, "explanation_key": "climate.evidence_missing", "evidence_ids": [], "missing_reason": "not_acquired"},
      {"indicator_id": "indicator-water-b", "key": "water_compatibility", "status": "incomplete", "value": null, "unit": null, "explanation_key": "water.rule_pending", "evidence_ids": [], "missing_reason": "not_reviewed"},
      {"indicator_id": "indicator-rotation-b", "key": "rotation_compatibility", "status": "incomplete", "value": null, "unit": null, "explanation_key": "rotation.history_absent", "evidence_ids": [], "missing_reason": "not_reported"},
      {"indicator_id": "indicator-timing-b", "key": "timing_feasibility", "status": "incomplete", "value": "partial_window_supported", "unit": "category", "explanation_key": "timing.partial_only", "check_ids": ["check-timing-b"], "evidence_ids": ["synthetic-calendar-evidence"], "period": {"start": "2026-11-15", "end": "2027-10-31"}, "spatial_support": "synthetic-region", "method_version": "shape-only", "qa": {"status": "synthetic_only"}, "limitations": ["One supported window does not establish three feasible crops."]}
    ],
    "missing_inputs": [{"fact_key": "synthetic-required-field-fact", "rule_id": "synthetic-soil-rule", "essential": true, "value": null, "missing_reason": "not_reported"}],
    "next_information_needed": [{"rule_id": "synthetic-soil-rule", "action_key": "answer_conditional_field_question", "soil_report_required": false}],
    "ranking": {"status": "unavailable", "selected_plan_id": null},
    "limitations": ["Shape stub assumes future reviewed timing evidence; missing source records and other essentials prevent a production complete result."]
  }
}
```

An unavailable climate component leaves this hypothetical partial comparison incomplete because a supported timing finding remains. If no usable scientific assessment exists at all, use A's unavailable result. Explicit first cultivation does not prove that all rotation/host checks pass.

### C. Unsupported crop report — proposed extension only

C replaces the v2 discriminator and current crop slot; other six-group data come from A. It deliberately **cannot** pass today's v2 validator. A well-formed future reported-name path preserves the farmer's answer without pretending to recognize the crop. A mapped crop with no reviewed region/season/variety evidence likewise has a coverage gap; it is not silently substituted.

```json
{
  "case_id": "unsupported", "synthetic": true,
  "request_changes": {
    "/request_id": "synthetic-request-c",
    "/intake/schema_version": "farmer-intake.crop-report.draft-01",
    "/intake/current": {"state": "growing", "identity_state": "unmapped", "crop_id": null, "reported_crop_name": "Unlisted sample crop", "sown_on": null},
    "/crop_context": []
  },
  "response": {
    "schema_version": "rotation-comparison.draft-01", "request_id": "synthetic-request-c", "status": "unavailable", "data_mode": "unavailable",
    "coverage": {"status": "unavailable", "reason_ids": ["unsupported_crop"], "unsupported_inputs": [{"input_path": "/intake/current", "reported_crop_name": "Unlisted sample crop", "resolved_crop_id": null}]},
    "comparison_period": {"status": "unavailable", "policy_id": null, "policy_version": null, "region_id": null, "start": null, "end": null, "input_refs": ["/intake/current"], "assumptions": [], "missing_reason": "unsupported"}, "environmental_assumptions_id": null, "baseline_assessment": {"status": "unavailable", "assessed": false, "feasibility": "undetermined"},
    "alternatives": [], "checks": [], "indicators": [],
    "next_information_needed": [{"reason_id": "unsupported_crop", "action_key": "request_catalogue_review", "owner": "Maruf"}],
    "ranking": {"status": "unavailable", "selected_plan_id": null},
    "limitations": ["Farmer-entered crop text is not reviewed evidence. Extension is proposed, not implemented."]
  }
}
```

### D. Invalid date window

D's reversed date window fails structural/date consistency validation before any scientific ranking. The existing local validator rejects this input; the future adapter proposes the following error envelope and HTTP 422. Unsupported names use C's coverage result, not this error, when the agreed extension is valid.

```json
{
  "case_id": "invalid", "synthetic": true,
  "request_changes": {
    "/request_id": "synthetic-request-d",
    "/intake/availability": {"kind": "window", "start": "2026-11-22", "end": "2026-11-15", "basis": "farmer_estimate", "applies_to": "after_harvest"}
  },
  "response": {
    "schema_version": "rotation-comparison.draft-01", "request_id": "synthetic-request-d", "status": "invalid_input", "data_mode": "unavailable",
    "errors": [{"input_path": "/intake/availability", "reason_id": "availability_window_reversed", "label_keys": {"en": "availability.window_reversed.en", "bn": "availability.window_reversed.bn"}}],
    "comparison_period": null, "baseline_assessment": null, "alternatives": [], "checks": [], "indicators": [],
    "ranking": {"status": "unavailable", "selected_plan_id": null}
  }
}
```

### E. Complete-status relationship, synthetic projection of the result

This deliberately reduced **status projection**, not a full response, demonstrates the cardinality rule without invented real crop calendars or varieties. The synthetic step IDs stand for fully sourced operation records in a future complete payload. All six step records, four explained indicators per plan, policy/assumptions and authentic evidence would be mandatory in a real complete result; this projection itself cannot be submitted as one. If one alternative were missing/incomplete, the bundle would be incomplete even while the other remains complete.

```json
{
  "case_id": "complete-status-projection", "synthetic": true,
  "status": "complete",
  "comparison_period_id": "synthetic-shared-period",
  "environmental_assumptions_id": "synthetic-shared-assumptions",
  "baseline_assessment": {"status": "complete", "assessed": true, "feasibility": "infeasible", "reason_ids": ["synthetic-reviewed-conflict"]},
  "alternatives": [
    {"plan_id": "synthetic-a", "status": "complete", "feasibility": "feasible", "comparison_period_id": "synthetic-shared-period", "environmental_assumptions_id": "synthetic-shared-assumptions", "steps": [{"step_id": "synthetic-a1"}, {"step_id": "synthetic-a2"}, {"step_id": "synthetic-a3"}], "completion_date": "2027-09-01"},
    {"plan_id": "synthetic-b", "status": "complete", "feasibility": "feasible", "comparison_period_id": "synthetic-shared-period", "environmental_assumptions_id": "synthetic-shared-assumptions", "steps": [{"step_id": "synthetic-b1"}, {"step_id": "synthetic-b2"}, {"step_id": "synthetic-b3"}], "completion_date": "2027-10-01"}
  ],
  "limitations": ["Shape projection only; distinct IDs do not prove substantive plan distinctness, evidence sufficiency or feasible dates."]
}
```

### F. Unresolved operation record, not a timed recommendation

This standalone step fragment shows duration origins and distinct endpoint fields. Null ranges/events stay unresolved until sourced; this is not a crop plan or an assumption of zero preparation time. A real step expands `operations` to include all applicable phases listed above, with rule-backed overlap/coverage references.

```json
{
  "case_id": "operation-fragment", "synthetic": true,
  "step": {
    "step_id": "synthetic-step", "crop_id": "rice", "rice_system_id": "rice-aman", "variety_id": null, "region_id": null,
    "status": "incomplete", "missing_reason": "not_reviewed",
    "operations": [{"operation_id": "synthetic-growth", "type": "growth", "start_window": null, "end_window": null, "duration_range": {"min": null, "max": null, "unit": "day", "from_event": "field_transplanting", "to_event": "maturity", "missing_reason": "not_reviewed"}, "included_operation_ids": [], "overlap_rule_ids": [], "source_ids": [], "evidence_ids": []}],
    "maturity_window": null, "final_harvest_window": null, "field_clearance_window": null,
    "transition": {"rule_ids": [], "covered_by_operation_id": null, "missing_reason": "not_reviewed"},
    "limitations": ["Aman identity is synthetic farmer context here; no reviewed variety, duration, harvest or clearance evidence is supplied."]
  }
}
```

## Intended crop, replay, receipt and transport review

Intended-crop assessment reuses exactly the planner's validation/check functions; return checked windows, evidence and missingness. It is not diagnosis of a growing crop. Historical replay identifies scenario/version, historical periods and the baseline run; hold non-climate inputs fixed and return comparable checks/rank changes. It is neither a future forecast nor observation of historical crop failure. One reviewed preset is sufficient.

JSON download and print consume the same actual API result/receipt without client-side scientific recalculation. Unknowns, incomplete status, units and limitations survive export. Input-only v2 download is not this receipt. No PDF server or account is required.

Proposed routes under `/api/v1`: GET health, regions, crops, sources, climate/history; POST fields/validate, suitability/evaluate, rotations/generate and simulations/run. Names, version negotiation and transport details remain draft. Proposed HTTP 200 covers interpreted `complete`/`incomplete` and domain `unavailable` results; HTTP 422 covers `invalid_input`; HTTP 503 covers service outages with a readable unavailable error, never fabricated results. Prachurjo/Fardin review errors, CORS/timeouts, size limits and retries. No projection/chat endpoint in MVP.

## Remaining decisions and acceptance handoff

| Owner / step | Required review before freeze |
| --- | --- |
| **Saim / s02** | Climate parameter fields, units/time standard, historical periods/comparability, spatial support, QA, missingness and indicator methods; source/artifact provenance. No full scientific acquisition in G0. |
| **Maruf / s03** | First reviewed region/varieties; crop/system/season applicability; calendars, duration origins/ranges, preparation/harvest/collection/clearance and transitions; agronomic essentiality; exact versioned common-period rule and availability uncertainty. |
| **Prachurjo / s04** | Preserve six inputs and v2 migration; proposed rice/variety/unsupported-name and conditional follow-up controls; EN/BN four-indicator explanations, baseline/plan/bundle states and adjacent errors; no fabricated API fallback. |
| **Fardin with technical owners / s05** | Freeze reviewed payload schemas/examples, period/assumption identity, distinctness, constraint-first preset order/ties, any separately agreed formulas/weights, transport and canonical fingerprints. |
| **Independent human reviewer + Fardin / s06** | Record genuine review and accepted main-branch revision; only afterward hand off G1 implementation. A branch push or parsed synthetic JSON is not acceptance. |

Review cases: equal previous/current crops; repeats/fallow and explicit absence; unknown rice system/variety; supported vs unsupported combinations; optional soil report with essential unanswered fact; shared-policy selection before ranking; availability ranges; sowing/transplanting duration origins; maturity/final-harvest/clearance distinction; cross-year/leap-day windows; operation overlap/double counting; distinct alternatives with different completion dates; unallocated time; assessed infeasible baseline; one complete alternative in an incomplete bundle; source absence; intended-crop parity; replay/receipt reproduction.

Only s01's **draft preparation** is delivered here. Owner agreement, schema freeze, scientific evidence, implementation and acceptance remain pending in [G0-CONTRACT](tasks/G0-CONTRACT.json). Local JSON/workflow checks verify document syntax and tracking, not agricultural validity.
