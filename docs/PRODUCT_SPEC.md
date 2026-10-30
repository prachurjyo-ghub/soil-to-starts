# Product specification

Status: intended behavior, rebaselined for the 30 October 2026 planning implementation. The board identifies actual implementation. [Mandatory-now context](MVP_SCOPE.md) and [future-only context](FUTURE_ROADMAP.md) supersede older scope wording; external challenge requirements remain separate from team product choices.

## The decision we are building

The [official challenge](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/) asks for rotation decision support using NASA Earth observations, local soil information, crop characteristics, and farmer priorities. Bangladesh-wide selection, exactly three future crops, bilingual presentation, and scenario replay are **our product choices**.

The central demonstration is: “For this supported Bangladesh field, compare your usual practice with two distinct feasible alternatives, each containing three future main-crop steps after the current harvest. Inspect timing, water/rotation trade-offs, rejected choices and the same evidence in a quick crop check, historical replay and printable result receipt.”

### Inputs and outputs

- Latest required intake (30 October 2026): confirmed map pin or independent 64-district search, separately from scientific pilot coverage; six core questions visible together in the order defined in [API_CONTRACT](API_CONTRACT.md), with explicit required answers and no demo defaults; current crop/harvest or field-available date; dated recent history and usual future rotation including fallow; seasonal water access and priority preset. Previous/current crops are separate roles and may be identical. Area/unit is required for dependent outputs. Known soil/report/variety/equipment/excluded-crop details are progressive and may be unknown. No fertilizer input or login required.
- A complete result contains **exactly three new future steps** after the current crop, chronological sowing/harvest intervals, crop names/families, transition reasons, constraints, assumptions, alternatives, exclusion reasons, score components, and source IDs. “New” means future steps; crop repetition follows sourced rules rather than an arbitrary all-distinct requirement.
- Return `complete`, `incomplete`, `unavailable`, or `invalid_input` at both defined bundle/plan levels. A complete comparison needs an assessed baseline and two distinct complete alternatives sharing a horizon. A baseline can be infeasible but assessed. One complete plan can appear in an incomplete bundle. Preserve supported checks and essential unknowns; never invent alternatives or filler crops.
- Hard feasibility constraints apply before preference ranking. Raising a water-conservation or soil-health preference cannot make an infeasible sequence valid. Three presets use documented deterministic ranking. Aggregate scores are optional comparison indices, not yield, probability of success, measured soil restoration or calibrated confidence.
- Geography can be selectable nationwide while evidence coverage varies. Label the difference. NASA grid context does not measure a field's exact soil nutrients or pH.

### User journey to implement in the existing application

1. **Home:** a light, accessible agricultural introduction, EN/BN controls, and a persistent **Plan My Field** action. Keep the existing frontend; no second application.
2. **Field setup:** required validated map/district location above six visible ordered questions: current crop, availability, previous history, usual future sequence, water access and priority. Validate every core answer and dependent control, preserve drafts, and allow the named empty/absence states rather than general unknown answers. Scientific unknowns remain explicit. Provide text/admin selection without a map. Until integration, show an input-only summary and planning unavailable.
3. **Workspace:** show the three-strategy matrix and selected future timeline, intended-crop check, source-linked why/why-not ledger and missing-information actions. Three presets replace compulsory weighting sliders. A sidebar belongs inside the workspace, not before entry.
4. **Climate explorer:** show authentic temperature/rainfall arrays, units, period, scale, missingness and source details. Missing data stays a gap; trends require a defined method and uncertainty.
5. **Scenario comparison:** hold field/history/preferences fixed and replay a documented historical dry/wet/hot period or an explicitly labeled scenario. Separate historical evidence from any later sourced projection.
6. **Evidence/receipt:** visible data mode, coverage, source/rule/method versions and stable input/result fingerprints. JSON download and basic print preserve actual results and limitations. Test phone, keyboard, EN/BN, reduced motion, source failure and export.

Preserve current routes `/` and `/workspace`. Separate `/climate`, `/plan`, `/about`, `/team`, or `/methodology` pages are proposed; inspect existing navigation and agree an issue before creating routes. Scrollytelling can enhance the story after the scientific path works; it must not invent data, hide the primary action, or block reduced-motion users.

### Two implementation scopes

**Mandatory now:** one reviewed pilot and small catalogue; short intake; authentic POWER rainfall/temperature; deterministic constraint-first three-strategy comparison; quick intended-crop check; evidence-linked rejection/missing-information ledger; one historical stress replay; stable result receipt with basic print/JSON; compact four-scene climate story after the first integrated slice; accessible EN/BN workspace; tested offline scientific replay and authorized public pilot. Exact feature/gate acceptance is in [MVP_SCOPE](MVP_SCOPE.md).

**Future only:** wider reviewed coverage and long-duration/perennial paths, additional NASA products/maps, rich motion/3D/voice/PWA, broader scenarios/projections, optional fertilizer/nutrient/carbon research, optional accounts/economics/sensors and optional runtime assistance. See [FUTURE_ROADMAP](FUTURE_ROADMAP.md). Each track is blocked pending accepted G5 and a separate activation decision; none is a hidden release condition.

A small active pilot catalogue does not erase the long-term Bangladesh-wide selection and crop-diversity targets. Unsupported locations/crops must say so. Fertilizer tracking, nutrient-depletion simulation and numerical soil-restoration claims are excluded from MVP. Development assistance from AI remains permitted with truthful command/contribution records; runtime AI is not required.

## Evidence and scientific boundaries

Data, agronomy and result contracts

**First evidence source:** [NASA POWER daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/). Saim starts with precipitation and temperature at an explicit Bangladesh location. Aim for 2001–2025 where suitable, but validate actual coverage, parameters, grid support, units, missing codes and time standard before claiming a complete record. POWER daily supports UTC/LST; record the selected standard. Cache per relevant grid cell rather than repeatedly requesting the same location.

Candidate additions, not integrated sources: [GPM IMERG](https://gpm.nasa.gov/data/imerg), [SMAP](https://nsidc.org/data/spl3smp_e/versions/6), [MODIS vegetation indices](https://lpdaac.usgs.gov/products/mod13q1v061/), and [NEX-GDDP-CMIP6](https://www.nasa.gov/ames/earth-science/nasa-earth-exchange-nex/gddp/downscaled-climate-projections-nex-gddp-cmip6/). Each needs an exact product/version, license, quality mask, dates and scale; do not merge different coverage into one supposed continuous record.

Maruf verifies exact Bangladesh references from [BARC crop zoning](https://apps.barc.gov.bd/cropzoning/), [BAMIS calendars](https://www.bamis.gov.bd/en/calendar), and relevant BARI/BRRI/DAE/SRDI or FAO publications. These organizations are **candidate sources**, not proof that we already have validated crop rules. Record the exact publication, location relevance, rule, units, rights, and review status.

Each crop record needs stable ID; Bangla/English/scientific names; category/family; annual/perennial status; regional sowing/harvest windows and duration; sourced water/soil constraints; sequence/repetition rules; reference IDs and recommendation-readiness status. Missing essential thresholds cannot be replaced with plausible AI-generated numbers.

Each source manifest needs:

```text
dataset_id, provider, product_id/version, source_url/doi
date_range, retrieved_at_utc, coordinates/bounding_box/grid
native/output_resolution, units, time_standard
QA_and_missing_rules, transformations, processing_script/version
checksum, license/redistribution_terms, limitations
```

Trace every scientific value through source → raw payload → normalization → deterministic method/version → API result → UI claim. Save small licensed, reproducible fixtures with manifests; large downloads stay in ignored `cache/`. Source status progresses from `candidate` → `downloaded` → `validated` → `integrated`; do not skip stages in claims.

Draft result contract: separate bundle/plan statuses, common horizon, baseline assessment, distinct alternatives, check/reason ledger, supported indicators, missing-information actions, source/catalogue/method versions and stable receipts. Complete recommended plans have exactly three future main-crop steps; baseline segments are flexible. Scientific data modes are `cache`, `verified_fixture`, or `unavailable`; a historical acquisition may separately record that it was fetched live. Existing illustrative UI constants must never be relabeled as a verified fixture. Older docs use `fixture`; align that legacy wording with the agreed contract before implementation.

Typical exclusions: `WATER_INSUFFICIENT`, `SOIL_UNSUPPORTED`, `SALINITY_CONFLICT`, `SEASON_WINDOW_MISSED`, `HARVEST_OVERLAP`, `FAMILY_REPEAT_RISK`, `CLIMATE_STRESS`, `MISSING_EVIDENCE`, and `PERENNIAL_NOT_ROTATABLE`. Each reason points to the actual rule/source. Explain preference trade-offs separately from hard exclusions.

No invented NASA trends, soil tests, planting dates, yields, nutrient balances or confidence percentages. The independent guide's seven-day/20-mm onset rule and “11-day shift” are examples, not validated Bangladesh findings. Historical stress replays are not future forecasts. Projections, if added later, need pathway/model/period/baseline/ensemble and limitations clearly separated from historical data.
