# Regional climate method and handoff

Current local status, 13 November 2026: Saim independently authorized Regional
acquisition/preparation and adopted representative-point context. The collection,
preparation, extreme-value audit and coordinate-role recheck are complete locally
on `main2`. Their task records remain under independent review; no accepted
scientific, agronomic or application integration is implied. Step 2 changes
method documentation and adds read-only checks only.

## Prepared evidence and application boundary

All 100 annual parameter requests completed: 99 downloads and one exact 2001
PRECTOTCORR preflight reuse; no final failed/pending requests. Coverage is
2001-01-01–2025-12-31, four parameters, 140 returned locations, 9,131 dates per
location and 5,113,360 values. Exact raw bytes total 86,654,505; the measured
collection run took 363.922261 seconds. Earlier sandbox DNS failures remain in
error evidence; they are not hidden by successful later acquisition.

The source is NASA POWER Daily Regional API v2.10.3, AG community, metric units,
explicit **LST (local solar time)**. PRECTOTCORR is mm/day; T2M, T2M_MIN and
T2M_MAX are C. PRECTOTCORR/T2M report MERRA2; daily extrema report MERRA2 and
POWER. Parameter-specific source metadata is retained. LST is not Bangladesh
civil time. These historical reanalysis/context records are not forecasts,
weather-station measurements or field observations.

Local receipts and detailed findings:

- [Acquisition receipt](../../data/climate/nasa_power_regional_full_summary.json).
- [Preparation receipt](../../data/climate/nasa_power_regional_preparation_summary.json).
- [Extraction diagnostics](../../data/climate/regional_district_extraction_diagnostics.json).
- [Extreme-value audit](CLIMATE_EXTREME_VALUE_AUDIT.md) and
  [audit JSON](../../data/climate/climate_extreme_value_audit.json).
- [Coordinate-role check](../../data/climate/climate_coordinate_role_check.json).

Ignored raw cache:
`cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/`.
Ignored derived cache: `cache/nasa_power_regional/prepared-v1/` contains
100 long-form `*.jsonl.gz` partitions, 100 `*.monthly.json` partitions with
168,000 complete monthly rows, 560 `chart-*.json` payloads, 25
`YYYY.wide-replay.jsonl.gz` partitions with 1,278,340 regional date/location rows,
and `inventory.json`. Its `district-context/` directory contains 1,600
district-year files with 584,384 district/date rows and `manifest.json`.
Two offline preparation runs produced 786 byte-identical regional files.

The mapping-only diagnostics retain `district_weather_produced: false`; the
actual district export manifest reports `district_weather_produced: true` and
lists output checksums. Use the export receipt to determine whether derived
series exist, rather than treating the mapping artifact as an export status.

These are prepared local evidence files. They are **not integrated** into the
frontend, scientific API, rotation engine or story. The app remains an
illustrative frontend. The previously documented route
`prototype/app/api/bamis-calendar/route.js` is absent on this checkout; no
connected BAMIS API is verified. No crop rule is activated by climate preparation.

## Coordinate roles and representative-point method

The original district registry contains one WGS84 anchor derived by the
pinned-geometry point-on-surface method. Anchors are administrative sampling
references; they are not farmer field coordinates or NASA observations.
`data/climate/district_sampling_registry.csv` is unchanged, SHA-256
`0b31748796de714f73de135ee3e0ec77c2e44813985d790b44f2d62e18c62dfa`.

Regional output positions are the coordinates returned by the API. Their
longitude/latitude values are retained unchanged and are not assigned NASA
native-cell IDs. An output position has a different role from its district
anchor, even when the values happen to coincide. GeoJSON and containment checks
use `[longitude, latitude]`; the CSV has separately named latitude/longitude columns.

Saim adopted nearest-returned-position representative-point context on
13 November 2026. For each unchanged anchor, candidates are ranked by
great-circle distance (Earth radius 6371.0088 km), then returned latitude, then
returned longitude. Exact distance ties use that deterministic coordinate order;
no invented near-tie tolerance or maximum-distance threshold is applied.
Both coordinates, distance, second-nearest distance and tie count are retained.
The recheck verifies the existing mapping; it does not generate a replacement.

The 64 anchors use 42 returned positions; 17 positions are shared, and at most
four districts share one position. Anchor-to-output distances range from
1.569374 to 40.500284 km. Shared series are the same regional observations,
not independent district climate samples. Regional summaries stay keyed to
returned positions; district exports are derived contextual views.

A selected position can be outside its assigned district, or outside all pinned
Bangladesh polygons. No district-containment constraint was part of the adopted
nearest-position method. The padded box (87.383628–93.305257°E,
20.090609–27.134513°N) provides regional spatial context. Being inside the
returned coordinate extent is not the same as being inside a country/district
polygon. Exact coordinate/date joins do not establish source-cell footprints,
Point API equivalence, district-area averages or field precision.

The Step 2 recheck finds all **64 original anchors uniquely inside their assigned
pinned districts**. Of the 64 district mappings, 53 selected output positions
are strictly inside the pinned country polygons and 11 are outside; none is on
a pinned boundary. The outside-position mappings are Barishal, Chandpur,
Chapainawabganj, Cumilla, Kushtia, Lakshmipur, Meherpur, Panchagarh, Rangamati,
Shariatpur and Thakurgaon. This counts district mappings, not unique output nodes.
The checker records stable IDs in its JSON evidence.

## Chapainawabganj: only the output position is outside

For `bd-district-chapainawabganj`:

- Original registry anchor: **longitude 88.256694, latitude 24.688357**.
  It is strictly inside Chapainawabganj's original pinned feature and inside
  exactly one of the 64 district features.
- Selected Regional API output position: **longitude 88.125, latitude 24.5**.
  It is outside Chapainawabganj's feature and all 64 pinned Bangladesh features;
  it is not on a polygon boundary. It is not the original registry anchor.
- Great-circle anchor-to-output distance: **24.8185734952679 km**.
  The second-nearest returned position is 37.11368586097449 km away.
  There is one candidate at the exact minimum distance (no tied winner).

The check reads the original compressed source,
`data/admin/bgd-adm2-source.geojson.gz`, not a new download or altered boundary.
Source ID/version: `BGD-ADM2-16705992@9469f09-local1`; uncompressed SHA-256:
`7dbdb186f3b8af10417147a99859196fcd89c619fb5c6ac3804251fb6b449b6a`.
The existing shape-ID mapping resolves the assigned feature. The existing strict
ray-crossing polygon-with-holes test is applied separately to each coordinate;
boundary membership is checked separately. The selected output is verified
against actual returned preflight coordinates and the unchanged export mapping.
Exact evidence paths and hashes are in the coordinate-role JSON.

There is **no original-anchor containment failure or registry/mapping inconsistency**.
The selected output supplies nearby regional context, not a district-contained
measurement. The 31.59 C T2M_MIN on 2012-06-05 traced in the extreme audit comes
from this output position; its faithful propagation does not prove district
representativeness. Neither coordinate, extraction rule nor observation was moved.

“Outside” here means outside the **pinned simplified administrative polygons**.
It does not independently establish a foreign location, surveyed international
border crossing, land/sea classification or exact source-cell footprint.
The source's represented-year metadata (2020) and linked source title (2015)
differ; positional accuracy and simplification tolerance remain unresolved.
Appropriateness of this context for downstream decisions needs scientific review.
A district-area average would require a separately reviewed footprint/weighting
method; this documentation does not adopt one.

## Observation processing, monthly calculations and missingness

The long schema contains collection_id, request_id, parameter, date,
output_longitude, output_latitude, value, unit, time_standard, missing_reason and
raw_artifact (raw SHA-256, resolved to path/metadata through `inventory.json`).
Raw response bytes, full request identity, retrieval metadata, byte count,
SHA-256, API/source metadata and failed-attempt evidence remain preserved.
Checksum-aware reuse verifies the full request and response structure; short
smoke responses are never annual coverage. The historical Point API reuse
blocker remains unchanged; separate Regional acquisition did not resolve it.

The parser rejects malformed numbers, booleans, non-finite values, duplicate
JSON dates/coordinates, wrong parameters/units/time standard and unexpected or
missing dates; leap days are checked. Documented -999 fill becomes null with
`source_fill_value`. Zero remains a valid observed zero. There is no silent
interpolation, resampling, clipping or replacement with zero. Accepted raw
responses contain zero fills. The wide view joins all four parameters only
where coordinate/date keys are exactly compatible. All 25 annual joins passed;
all years/parameters share coordinate-support SHA-256
`697c347b6623d74914550ccad34b640a2060647250c9a549a8fa5ddfbd58ad4f`.
Metadata differences remain even when keys align.

Monthly PRECTOTCORR integrates each daily mm/day rate over one daily interval,
then sums those amounts once to give mm. It does not sum monthly mean rates or
apply an extra hourly/second conversion. Monthly temperatures are arithmetic
means of daily T2M, T2M_MIN or T2M_MAX respectively. A mean of daily extrema is
not the month's absolute extreme. Each payload carries units, valid/expected
days, coverage, artifacts and processing version `regional-preparation-v1`.
If any expected daily value is missing, the primary monthly value is null;
`available_day_statistic` is explicitly partial and remains null when no valid
values exist. No acceptable-missingness threshold is invented.

Source interpretation already recorded during preparation:
[NASA Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/),
[meteorological methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/),
and [hydrology units](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/).
These links are references, not independent validation of the local series.
No documentation or data was downloaded during Step 2.

## Replay inputs and extreme-value audit

Chart JSON carries dates, values, units, coverage, source/artifact identities,
period and processing version. Wide daily series are historical replay **inputs**;
no decision-engine replay has run. Selection remains configurable and provisional:
`--start-month` and `--month-count` define a period (default calendar year),
including cross-year seasons. Only complete periods qualify. Rainfall is summed;
temperature period means are day-weighted. Descriptive minima/maxima use earliest
start as the tie-break. They are not agreed crop stress thresholds or forecasts.
No crop-failure, yield, planting-date or rotation-ranking conclusion follows.

The Step 1 audit traced 14 selected extremes through raw → long → monthly →
chart/wide replay → applicable district exports. All were category B, faithfully
preserved source values; no category A processing error was proved in the audited
lineages. All 1,278,340 matched raw temperature triplets satisfy minimum ≤ mean ≤
maximum. All 17 negative T2M_MIN values were recounted; negative Celsius is not
an error marker. Category C physical-accuracy and sampling questions remain.

The padded-area PRECTOTCORR maximum is 965.18 mm/day on 2017-07-22 LST at
91.25°E, 20.5°N. That position and the six reported padded-area temperature
extrema are outside pinned Bangladesh polygons and unused by district exports;
they remain in their regional chart/replay inputs. Do not label them
Bangladesh-only or district extrema. District-used rainfall reaches 521.24 mm/day
at the Cox's Bazar context position on 2019-07-07. Selected district-used extremes
propagate faithfully; none was corrected. Statistical rarity and neighbouring
values are diagnostics, not independent meteorological validation.

## Agronomy handoff and remaining decisions

All 64 stable district IDs join the exact district labels in
`assets/bamis_region_district_mapping.csv`; diagnostics retain the mapping hash
and per-ID BAMIS region lists. The BAMIS Rajshahi region covers Chapainawabganj,
Naogaon, Natore and Rajshahi, distinct from the eight-district administrative
division. Calendar coverage is not downscaled district weather or a crop threshold.
Maruf's six catalogue records and fourteen candidate-rule rows remain inactive;
lentil's printed month/week conflict and mustard's unresolved species remain open.

Maruf and Fardin still need to resolve:

1. Printed standard-week convention (not assumed ISO weeks), actual period bounds,
   sowing/transplanting origin, inclusive ends, maturity/final harvest/clearance,
   cross-year handling and lentil's month conflict.
2. Source/variety/stage-specific rainfall triggers: amounts, intervals, consecutive
   day logic, seasonal bounds, units, missingness behavior and source/version/page.
   Weather normals and qualitative “rain absent” wording are not numeric rules.
3. Conditional irrigation guidance versus water-access inputs. Event counts do
   not establish water volumes; BR3 rice and zero-tillage mustard evidence must
   retain their limited scope.
4. Predeclared replay season/selection, usable-period policy and fixed non-climate
   assumptions before future same-engine replay.
5. Representative-point labels, distance visibility, outside-polygon limitations,
   source IDs and partial/unavailable states before scientific API integration.

Saim's representative-point method choice is recorded; it is not pending adoption.
Independent source/method review and appropriate agronomic validation remain
pending. Step 2 stops with these documented limits; no method change is authorized.

## Recheck commands and historical records

Read-only checks from repository root (the coordinate-role command writes only
its small new check receipt):

```bash
OFFLINE=1 python3 -B src/acquire/check_climate_coordinate_roles.py
python3 -B src/acquire/build_district_sampling_registry.py --check
python3 -B -m unittest tests.test_climate_coordinate_roles -v
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/workflow.py render
python3 scripts/workflow.py check
git diff --check
```

[Sampling record](NATIONWIDE_SAMPLING.md),
[Regional smoke/proposal](NASA_POWER_REGIONAL_PROPOSAL.md) and
[annual preflight](NASA_POWER_REGIONAL_PREFLIGHT_2001.md) preserve historical
bounded findings. Their earlier unselected-method/proposal-only language applies
to those stages, not the current prepared status. Raw acquisition did not require
prior district extraction adoption. No G0 or teammate acceptance was advanced.
Step 2 verification passed: the original registry check, the new coordinate-role
check, four focused coordinate-role tests and all 99 repository tests. All 82
files referenced by the prior audit retain their recorded hashes. Whitespace
and workflow checks pass; no frontend check was run because frontend files are
unchanged. Current task: `CLIMATE-METHOD-DOCS`, pending independent review.
Current tasks, checks and handoffs are in `docs/tasks/`; actual contribution
history remains solely in `docs/AI_USE.md`.


## Step 3 — portable local package

The versioned climate-only delivery is
`cache/climate_handoff/soil-to-stars-climate-bgd-v1.0.0.tar.gz` in ignored storage.
Its exact archive size/SHA-256, manifest hash, source snapshot and actual isolated
verification results are recorded in
`data/climate/climate_data_package_v1_receipt.json`; the matching `.tar.gz.sha256`
and `PACKAGE_MANIFEST.json` sidecars sit beside the archive. No upload or public
sharing is performed. See the [teammate setup guide](CLIMATE_DATA_PACKAGE_GUIDE.md)
for bootstrap verification, safe extraction, exact offline validation/reproduction
commands, examples and separately intentional reacquisition instructions.

The bundle includes the 100 raw responses/manifests, original provenance and
2,387 prepared artifacts; explicit profiles distinguish raw reproduction inputs
from prepared consumption views. It snapshots relevant working source bytes and
hashes as well as HEAD, rather than assuming HEAD identifies the implementation.
No scientific observations or district mappings are changed. The
[package terms](CLIMATE_DATA_PACKAGE_TERMS.md) retain attribution and outstanding
public-sharing limitations, including the supplied BAMIS mapping's unverified
redistribution terms. Integrity is not scientific or agronomic approval.


Step 3 measured delivery result: **88,023,118 archive bytes**; **2,618 payload
files plus the package manifest** (2,619 archive members). Archive SHA-256:
`4a0ba04c9c8beaa0a908e0b4d61cc23c6b90f87ad927bbe229405860eda6117b`.
Manifest SHA-256:
`230b58fdc12b0cc12742387ab542e944d99facf35e6b7e071fa3636423dca29b`.

Safe extraction into `/private/tmp/soil-climate-package-test.UeroHE/extracted/`
verified every payload file. Offline validation passed for all 100 raw requests,
the original registry and coordinate-role checks. Reproduction in the separate
`/private/tmp/soil-climate-package-test.UeroHE/reproduced/` tree copied no derived
inputs and recreated all **2,387 derived files byte-for-byte**, retaining all
222 required raw/source/input files unchanged. Regional and Chapainawabganj
examples loaded successfully. All 105 repository tests, including six archive
safety/offline tests, passed. The nine working source hashes and 82 previous audit
evidence hashes remain unchanged. The archive/sidecars/bootstrap are Git-ignored.

No hidden working-repository dependency was found. Exact compressed reproduction
was tested with Python 3.9.6 / zlib 1.2.12; other compression runtimes may produce
different bytes and require investigation. The setup/terms guide is included in
the immutable package snapshot; this measured-result addendum and the external
producer receipt are recorded after the package was sealed to avoid circular
archive/receipt hashing. The scientific method and packaged source are unchanged.
No data refresh, upload, publication, staging or commit occurred. Step 3 stops here.

## Ready-to-copy teammate delivery (after Git publication)

Git at `db37c6d` contains the implementation/receipts but does not deliver ignored
climate data. The verified existing v1.0.0 archive and matching sidecars/receipt/
bootstrap are now assembled at
`cache/climate_delivery/Saim_to_Fardin_climate_v1.0.0/`, with START_HERE, a recipient
checklist, local producer results, real loaded example and file inventory.
See the [concise delivery report](CLIMATE_TEAM_HANDOFF_REPORT.md),
[local consumption interface](CLIMATE_CONSUMPTION.md) and
[Maruf/Fardin parameter dictionary](CLIMATE_PARAMETER_COMPATIBILITY.json).
New clean-directory offline validation/reproduction passed without changing the
sealed archive, source observations or mappings. Manual/separately authorized
transfer and Fardin's independent verification remain outstanding; no recipient
acceptance or backend/frontend integration is claimed. Do not confuse available
producer files or Git receipts with delivery to another computer.


## Current delivery — Git-hosted archive

Saim now authorizes Git-based distribution, superseding manual transfer as the
current workflow. The unchanged 88,023,118-byte v1.0.0 archive is included under
`data/climate/packages/v1.0.0/`, with original SHA-256
`4a0ba04c9c8beaa0a908e0b4d61cc23c6b90f87ad927bbe229405860eda6117b`.
Teammates clone/pull `main2` and run `python3 scripts/setup_climate_data.py`.
The command verifies and extracts local data with no NASA request; expanded
files remain ignored. See [current setup](CLIMATE_GITHUB_SETUP.md) and
`data/climate/climate_git_distribution_receipt.json` for measured Git-delivery
checks. Original archive/producer records remain unchanged as historical
provenance. Scientific applicability, NASA notification and BAMIS mapping rights
limitations remain explicit; Git publication is not scientific validation or
automatic backend/frontend integration.


Git publication outcome: local commit `ebbada9` and merge `38b97a4` preserve the
new data/setup work and teammate changes. Automatic approval review rejected
`git push origin main2` before execution because the 88 MB payload contains a
BAMIS mapping whose redistribution rights are unverified and requires explicit
archive/destination authorization. No alternate upload or bypass was attempted.
Local fresh-clone installation passed, but remote availability/fresh GitHub-clone
verification are not claimed. See the current Git distribution receipt/status.
