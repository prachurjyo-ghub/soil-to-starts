# Data sources and provenance

**Integration status: planned.** [MVP_SCOPE](MVP_SCOPE.md) requires one reviewed pilot POWER record; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) defers extra products until separately activated. The current app uses illustrative values, not the datasets below. Listing a dataset here does not mean it has been downloaded, processed, or used in a result.

| Source | Intended role | Current status and caveat |
| --- | --- | --- |
| [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | Daily precipitation and temperature for season indicators; possibly solar radiation for context | First acquisition target. Document selected parameter IDs, grid point, time standard, units, missing values, and retrieval date. POWER gives gridded regional context, not a field rain gauge. |
| [GPM IMERG Final Run](https://gpm.nasa.gov/data/directory/imerg-final-run-pps-research-gis) | Spatial rainfall comparison where a point series is insufficient | Optional. Choose an exact product/version and aggregation method; do not mix precipitation rate and accumulation. |
| [SMAP enhanced L3 soil moisture, v6](https://nsidc.org/data/spl3smp_e/versions/6) | Regional surface-soil-moisture context for water stress | Optional. The product is daily at a 9 km grid and begins in 2015, so it cannot support a 2001-onward soil-moisture comparison. Check quality flags and local representativeness. |
| [MODIS vegetation indices](https://lpdaac.usgs.gov/products/mod13q1v061/) | Observe broad vegetation patterns and help validate season timing | Optional. Select the exact collection, quality mask, spatial subset, and crop/land-cover mask before interpreting NDVI as farm activity. |
| Local soil, crop, and farmer information | Feasibility constraints and priorities in the official challenge | Needs an identified local source, permission to use it, units, and validation. User-entered soil values must remain distinct from measured datasets and estimates. |

NASA POWER's [daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) specifies that daily responses can use UTC or local solar time; choose and record one. [NSIDC's SMAP product page](https://nsidc.org/data/spl3smp_e/versions/6) gives temporal coverage, spatial resolution, version, and citation guidance. The [IMERG product page](https://gpm.nasa.gov/data/directory/imerg-final-run-pps-research-gis) distinguishes accumulation from rate. These are source-specific details to verify again when acquisition is implemented.

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
