# Data sources and provenance

**Integration status: partial.** The workspace has a BAMIS regional crop-calendar lookup from a user-provided CSV. Its source readiness remains `candidate`: the lookup preserves source PDF/page identifiers and exposes calendar rows without ranking them. It does not produce a complete rotation. NASA/optional products and locally reviewed soil/sequence rules remain unintegrated unless stated otherwise.

| Source | Intended role | Current status and caveat |
| --- | --- | --- |
| [BAMIS crop-weather calendar](https://www.bamis.gov.bd/en/) — project-prepared `assets/crop_planning_dataset.csv` | Regional crop/season weekly calendar, growth-stage, duration, district coverage, and associated weather reference | Candidate data connected through `prototype/app/api/bamis-calendar/route.js`. The CSV has 7,834 rows for 14 BAMIS regions; `assets/bamis_region_district_mapping.csv` maps those regions to 64 districts and eight administrative divisions. Exact-region rows are grouped by crop/season; exact duplicate rows are removed; PDF/page identifiers and missing values are retained. Three copied district headers were corrected from agreeing region labels and repeated regional weather rows; one ambiguous Mymensingh/Cumilla onion calendar was excluded and recorded in `assets/crop_planning_dataset_report.json`. For repository consistency, 106 Bengali/OCR-corrupted `month` cells were mapped exactly to full English Gregorian month names; no week-based inference or scientific-value change was made. The external builder does not yet include this normalization. This mapping describes calendar coverage, not district measurements. No ranking, season aliasing, annual/perennial classification, crop-sequence, soil/water constraints, field availability, reuse-rights review, or agronomic validation is claimed. Results remain incomplete. |
| `data/catalog/rajshahi_crop_evidence_catalog.csv` using retained BAMIS PDFs and linked Kew Plants of the World Online taxonomy pages | First bounded crop identity/calendar research package for Rajshahi | Six inactive `candidate` records: Aman rice, Boro rice, wheat, lentil, mustard and Kharif-1 mungbean. Proposed IDs are not an API contract. Lentil has a source month/week conflict and mustard species is unresolved. Taxonomy supports identity/family/life-cycle review only and does not establish Bangladesh suitability. |
| `data/catalog/rajshahi_candidate_rule_evidence.csv` using Bangladesh Agricultural Information Service and Bangladesh Rice Research Institute pages | Candidate soil, drainage, irrigation and full-pattern evidence for the six Rajshahi records | Fourteen inactive `candidate` evidence rows: four soil, six water and four sequence. Scope is preserved as preferred conditions, conditional management, variety-specific guidance, or complete regional patterns. No row is an executable hard constraint. Missing numeric thresholds, generic-to-variety mismatches, unresolved mustard species, absent Aus records and unapproved field-input mappings block activation. |
**Scientific integration status: planned.** A four-request NASA POWER acquisition smoke test is complete, but Step 3 stopped before full acquisition because no authoritative parameter-complete request-reuse mapping was found. No response is integrated into the app, API, indicators or recommendations. [MVP_SCOPE](MVP_SCOPE.md) requires reviewed evidence; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) defers extra products until separately activated. The current app uses illustrative values, not the datasets below.

| [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | Daily precipitation and temperature for season indicators | [Configuration and four-request Point smoke evidence](data/NASA_POWER_ACQUISITION.md) exist for `PRECTOTCORR`, `T2M`, `T2M_MIN`, `T2M_MAX` in AG metric units and explicit LST. The [Point request-reuse review](data/NASA_POWER_REDUNDANCY_REVIEW.md) keeps all 1,600 Point chunks blocked. A separate [Regional API proposal and four-request smoke](data/NASA_POWER_REGIONAL_PROPOSAL.md) is conditionally suitable but changes extraction semantics and is not approved for full acquisition. No full history is downloaded or integrated. POWER gives gridded regional context, not a field rain gauge or district average. |
| [GPM IMERG Final Run](https://gpm.nasa.gov/data/directory/imerg-final-run-pps-research-gis) | Spatial rainfall comparison where a point series is insufficient | Optional. Choose an exact product/version and aggregation method; do not mix precipitation rate and accumulation. |
| [SMAP enhanced L3 soil moisture, v6](https://nsidc.org/data/spl3smp_e/versions/6) | Regional surface-soil-moisture context for water stress | Optional. The product is daily at a 9 km grid and begins in 2015, so it cannot support a 2001-onward soil-moisture comparison. Check quality flags and local representativeness. |
| [MODIS vegetation indices](https://lpdaac.usgs.gov/products/mod13q1v061/) | Observe broad vegetation patterns and help validate season timing | Optional. Select the exact collection, quality mask, spatial subset, and crop/land-cover mask before interpreting NDVI as farm activity. |
| Local soil, crop, and farmer information | Feasibility constraints and priorities in the official challenge | Needs an identified local source, permission to use it, units, and validation. User-entered soil values must remain distinct from measured datasets and estimates. |

NASA POWER's [daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) specifies that daily responses can use UTC or local solar time; choose and record one. [NSIDC's SMAP product page](https://nsidc.org/data/spl3smp_e/versions/6) gives temporal coverage, spatial resolution, version, and citation guidance. The [IMERG product page](https://gpm.nasa.gov/data/directory/imerg-final-run-pps-research-gis) distinguishes accumulation from rate. These are source-specific details to verify again when acquisition is implemented.

The [BAMIS portal](https://www.bamis.gov.bd/en/) describes crop-weather calendars and regional agrometeorological information. The connected view treats the supplied CSV as calendar reference data only. `district_coverage` and the separate mapping file preserve the normalized scope printed across the collected BAMIS PDFs; they do not support downscaling regional weather values to districts. `source_pdf` and `source_page` remain identifiers for the retained local source archive and are not converted into verified direct document links.

The Rajshahi candidate catalog separates evidence roles: BAMIS supports regional calendar identity, duration and printed week spans; linked taxonomy pages support crop identity and family. Later AIS and BRRI research is retained in a separate evidence ledger. It supplies qualitative soil/drainage guidance, conditional irrigation schedules, variety-specific rice guidance and named cropping-pattern examples, but not an approved executable rule schema. The catalog and ledger therefore remain inactive and outside the recommendation path.

## Required manifest for each integrated dataset

Record at least:

```text
source_name, product_id, version, official_url_or_doi
retrieved_at_utc, date_start, date_end, spatial_extent_or_point
native_resolution, output_resolution, time_standard, units
quality_flags_and_missing_values, processing_steps, code_revision
license_or_reuse_terms, checksum
```

Carry source IDs and a `data_mode` (`cache`, `verified_fixture`, or `unavailable`) into every API result and the visible interface. Never label an illustrative UI constant as `fixture` or `NASA data`.

## Pilot catalogue and useful unknowns

Convert exact permitted BAMIS/BARC/BARI/BRRI/DAE/SRDI/FAO references into reviewed regional crop-season rules, with essentiality and pass/fail/caution/unknown semantics. Source names alone are not validated rules. Obtain appropriate local review; record source dates, measurement versus estimate, units and applicability. Current and previous crop IDs may match. No compulsory fertilizer history, nutrient-depletion model or measured soil-restoration percentage in MVP.

Story arrays and the historical replay reuse versioned source evidence, period definitions and missingness. Fingerprints use normalized input and source/catalogue/method identities; a hash is not scientific certification. Extra missions are not first-release dependencies.

## Administrative intake directory (not scientific evidence)

The mounted intake uses the [Bangladesh National Portal district list](https://bangladesh.gov.bd/views/district-list), checked on 30 October 2026, for 64 district memberships/Bangla names across eight divisions. Local directory version: `bd-national-portal-districts-2026-10-30`, in `prototype/public/reference/intake.js`. English labels are transliterations; `bd-district-*` identifiers are application-owned, not official geocodes. Division counts: Dhaka 13, Khulna 10, Chattogram 11, Rajshahi 8, Sylhet 4, Rangpur 8, Mymensingh 4, Barishal 6. The directory includes no boundaries, centroids, field coordinates, crop calendars or evidence-coverage claims. It is embedded locally so district selection needs no map or scientific network call. Review source changes before changing IDs; names are reference facts, and no map tiles or government logos are copied. This administrative integration does not change the planned status of NASA/agronomic sources above.

## Integrated administrative boundaries (location only)

[geoBoundaries gbOpen BGD ADM2 metadata](https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM2/) identifies `BGD-ADM2-16705992`, BBS / OCHA ROAP sources and CC BY 3.0 IGO. The downloaded simplified geometry is pinned to upstream revision `9469f09`; metadata declares represented year 2020, while its source link says as of 2015. This discrepancy and unknown positional accuracy remain explicit. [Local snapshot, aliases and rebuild](../data/admin/README.md) retain the source, retrieval timestamp, license and checksums. [Runtime manifest](../prototype/public/reference/data/district-boundaries.manifest.json) records processing, version `BGD-ADM2-16705992@9469f09-local1`, 64 features and 38,112 vertices.

The runtime asset is 1,494,403 bytes (507,697 bytes with deterministic gzip). Loading and integrity checking are lazy for map selection/saved point rechecking; district-only intake needs neither geometry nor the MapLibre code chunk. Coordinates are unchanged from upstream simplified geometry. No scientific network acquisition runs on intake. OpenFreeMap supplies remote street/reference tiles with visible OpenFreeMap, OpenMapTiles and OpenStreetMap attribution; it is not satellite imagery or a local offline map. Administrative geometry gives location context only, never national advice coverage or surveyed field precision.

## Nationwide climate sampling registry (coordinates only)

Step 1 of the independently authorized nationwide climate work is documented in
[NATIONWIDE_SAMPLING](data/NATIONWIDE_SAMPLING.md). It derives one new,
strictly contained WGS84 point for each of the 64 districts from the pinned
administrative geometry. The registry contains no weather observations and is
not a district-average, field-measurement or NASA-grid-ID dataset. Acquisition
remains a later step.
