# Field Shift methodology plan

Status: proposed methods. The current frontend's illustrative logic is not this scientific engine. Read [MVP_SCOPE](MVP_SCOPE.md), [API_CONTRACT](API_CONTRACT.md) and [VALIDATION](VALIDATION.md) for release and contract requirements.

## Deterministic sequence

1. Separate measured soil reports, farmer observations, regional estimates, NASA environmental context, reviewed crop rules and preferences. Record provenance and preserve unknowns. Crop history alone cannot establish remaining nutrients.
2. Validate location, dates, units, field availability, baseline and priority. Previous/current crop IDs may match.
3. Select applicable reviewed catalogue and checked local POWER evidence. Validate fill values, expected dates, units, time standard, scale and versions.
4. Compute justified seasonal rainfall/temperature indicators. Add onset/dry-spell/crop-stage checks only after defining and reviewing their parameters.
5. Assess the baseline over the common horizon, retaining repeats/fallow and conflicts. Generate regional crop windows with duration/preparation intervals.
6. Apply sourced hard calendar/water/known-soil/sequence exclusions before ranking. Distinguish conflict, caution and missing essential evidence. A family change does not prove every pest disappears.
7. Search exactly three future main-crop steps, carrying dates and relevant family/host history. Do not independently choose three high-scoring crops. Unsupported long-duration/perennial paths remain unavailable.
8. Compare baseline and distinct water/soil-focused alternatives with common assumptions. Fewer supported alternatives means an incomplete comparison.
9. Reuse the checks for intended-crop assessment. Return fixed translated reason keys, source/rule IDs and useful missing-information actions; no runtime-generated prose.

## Indicators and ranking

Freeze preset orders, indicator definitions, units/categories and stable tie-breaking in G0. Save water prioritizes supported water compatibility; Soil protection / rotation diversity prioritizes reviewed sequence/cover/residue characteristics; Balanced uses an agreed transparent rule. Optional totals require documented normalization/weights and uncertainty. Do not score critical unknowns zero or silently reweight around them. Preferences never change observations or override exclusions.

Soil output describes known compatibility and supported management potential, including host/family breaks, diversity, calendar gaps and explicit cover/residue assumptions. A legume is not an automatic nutrient cure. Essential unknown soil requirements leave checks incomplete. Fertilizer rates, nutrient budgets, NPK depletion, soil-carbon trajectories and numerical restoration percentages are excluded from MVP.

Seasonal rainfall or categorical irrigation access alone cannot justify exact irrigation volume. Use qualified categories until adequate inputs and a reviewed water-balance method exist. [FAO evapotranspiration](https://www.fao.org/4/x0490e/x0490e0a.htm) and [irrigation guidance](https://www.fao.org/4/S2022E/s2022e08.htm) are method references, not copied local calibration; paddy management needs appropriate additional terms.

## Historical replay and story

Predeclare historical stress selection and periods, usable-year counts, missingness, effect-size and uncertainty reporting. Define calendar-day/cross-year alignment and leap-day handling. Hold non-climate inputs fixed and rerun the same engine. Report changed checks, feasibility and rank stability. This is model behavior under recorded climate, not a forecast, yield estimate or actual observed harvest outcome.

Export verified temperature/rainfall arrays and statistics for the four-scene story with units, period, sources and method. Use consistent scales and show no clear shift when supported. Do not cherry-pick periods, infer climate causation from one local series or invent climate-induced nutrient changes. Respect product-specific temporal/spatial coverage.

## Conditional timing methods

The independent guide's seven-day/20-mm onset values are examples, not validated Bangladesh thresholds; its sample function omits the stated dry-spell condition. Before using onset, define season/year, thresholds, windows, follow-up/dry-spell criteria, missingness, incomplete follow-up, multiple onsets and local observation/sensitivity tests. The example 11-day shift is not a finding.

GDD needs crop/variety base temperature, stage convention and missingness rules. max(0, (Tmax + Tmin) / 2 - Tbase), in degree-days, is a candidate convention rather than an approved local rule. Neither onset nor GDD is compulsory just to appear advanced.

## Reproduction and review

Version evidence, executable rules, transforms and ranking. Canonical inputs plus those identities produce stable fingerprints; timestamps are separate. Receipts preserve limitations and reproduce results. Test actual science/source gates; obtain appropriate local review of active rules. Workflow-helper tests are not agronomic validation. Wider soil modeling needs new inputs and review under [future scope](FUTURE_ROADMAP.md).
