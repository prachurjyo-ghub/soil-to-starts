# Data sources and provenance

**Integration status: partial.** The workspace has a BAMIS regional crop-calendar lookup from a user-provided CSV. Its source readiness remains `candidate`: the lookup preserves source PDF/page identifiers and exposes calendar rows without ranking them. It does not produce a complete rotation. NASA/optional products and locally reviewed soil/sequence rules remain unintegrated unless stated otherwise.

| Source | Intended role | Current status and caveat |
| --- | --- | --- |
| [BAMIS crop-weather calendar](https://www.bamis.gov.bd/en/) — project-prepared `assets/crop_planning_dataset.csv` | Regional crop/season weekly calendar, growth-stage, duration, district coverage, and associated weather reference | Candidate data connected through `prototype/app/api/bamis-calendar/route.js`. The CSV has 7,834 rows for 14 BAMIS regions; `assets/bamis_region_district_mapping.csv` maps those regions to 64 districts and eight administrative divisions. Exact-region rows are grouped by crop/season; exact duplicate rows are removed; PDF/page identifiers and missing values are retained. Three copied district headers were corrected from agreeing region labels and repeated regional weather rows; one ambiguous Mymensingh/Cumilla onion calendar was excluded and recorded in `assets/crop_planning_dataset_report.json`. For repository consistency, 106 Bengali/OCR-corrupted `month` cells were mapped exactly to full English Gregorian month names; no week-based inference or scientific-value change was made. The external builder does not yet include this normalization. This mapping describes calendar coverage, not district measurements. No ranking, season aliasing, annual/perennial classification, crop-sequence, soil/water constraints, field availability, reuse-rights review, or agronomic validation is claimed. Results remain incomplete. |
| `data/catalog/rajshahi_crop_evidence_catalog.csv` using retained BAMIS PDFs and linked Kew Plants of the World Online taxonomy pages | First bounded crop identity/calendar research package for Rajshahi | Six inactive `candidate` records: Aman rice, Boro rice, wheat, lentil, mustard and Kharif-1 mungbean. Proposed IDs are not an API contract. Lentil has a source month/week conflict and mustard species is unresolved. Taxonomy supports identity/family/life-cycle review only and does not establish Bangladesh suitability. |
| `data/catalog/rajshahi_candidate_rule_evidence.csv` using Bangladesh Agricultural Information Service and Bangladesh Rice Research Institute pages | Candidate soil, drainage, irrigation and full-pattern evidence for the six Rajshahi records | Fourteen inactive `candidate` evidence rows: four soil, six water and four sequence. Scope is preserved as preferred conditions, conditional management, variety-specific guidance, or complete regional patterns. No row is an executable hard constraint. Missing numeric thresholds, generic-to-variety mismatches, unresolved mustard species, absent Aus records and unapproved field-input mappings block activation. |
| [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | Daily precipitation and temperature for season indicators; possibly solar radiation for context | First acquisition target. Document selected parameter IDs, grid point, time standard, units, missing values, and retrieval date. POWER gives gridded regional context, not a field rain gauge. |
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

Carry source IDs and a `data_mode` (`cache` or `fixture`) into every API result and the visible interface. Never label an illustrative UI constant as `fixture` or `NASA data`.
