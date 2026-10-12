# Data sources and provenance

**Integration status: planned.** The current app uses illustrative values, not the datasets below. Listing a dataset here does not mean it has been downloaded, processed, or used in a result.

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

Carry source IDs and a `data_mode` (`cache` or `fixture`) into every API result and the visible interface. Never label an illustrative UI constant as `fixture` or `NASA data`.
