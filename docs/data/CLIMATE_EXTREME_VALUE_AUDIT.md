# Climate extreme-value audit — Step 1 only

Owner: Saim. Local audit on 13 November 2026; independent review and meteorological validation are not claimed.

## Result

The 14 selected observations are faithfully preserved source values (category B). No processing error was proven. No source or derived climate observation was changed or regenerated; no network/data request was made. Physical accuracy and representative-point limitations remain category C questions. Category A is reserved for a proven processing error.

The reported 965.18 mm/day precipitation maximum is at 91.25°E, 20.5°N on 2017-07-22 LST. Its returned position is outside the pinned Bangladesh geometry, inside the padded acquisition area, and unused by district context. The six reported temperature extrema are also outside the pinned country geometry and unused by district context. They remain in regional charts and replay inputs, so they must not be described as Bangladesh-only extrema.

Among the 42 district-used locations, rainfall reaches 521.24 mm/day at 91.875°E, 21.5°N on 2019-07-07 LST (Cox’s Bazar context). The district-used temperature ranges are T2M 8.39–37.81 C, T2M_MIN 1.23–31.59 C and T2M_MAX 15.2–47.62 C. These are selected-location context statistics, not district-area measurements or independently verified station events.

## Methods and scope

Global padded-area and district-used-location maximum rainfall plus minima/maxima of each temperature parameter; all ties counted, earliest date then longitude then latitude selects one observation.

Same returned coordinate at offsets -2,-1,0,+1,+2 calendar days; four nearest distinct returned points on the same LST date by great-circle distance (6371.0088 km), then latitude, longitude. No interpolation.

Geography uses the existing strict polygon-with-holes test on the pinned simplified ADM2 geometry. Boundary coordinates are distinguished from strict interior. The raw uncompressed boundary SHA-256 is `7dbdb186f3b8af10417147a99859196fcd89c619fb5c6ac3804251fb6b449b6a`. Coordinate containment classifies the returned position only; it does not establish native cell footprints, surveyed borders or land/sea coverage.

All 100 raw requests were reread and checked against request identity, full byte count/SHA-256, stored validation and the existing parser. This verifies 5,113,360 values with zero fills. For all 1,278,340 matched date/location temperature triplets, minimum <= mean <= maximum holds; zero missing triplets or violations were found. Negative Celsius values are preserved.

For each selected observation, the audit independently recomputes the monthly statistic from raw daily values using math.fsum (comparison tolerance 1e-9 absolute / 1e-12 relative to allow floating summation order). It checks a unique matching normalized key, raw identity, units/LST, no missing marker, monthly valid/expected counts, artifact provenance, exact monthly chart record and daily replay values. Selected normalized partitions and replay files are scanned for duplicate keys. All four replay parameter values are checked against raw date/location records. Applicable district files are checksum-verified and matched to the replay record and unchanged anchors. No scaling, fill substitution, repeated accumulation, incorrect join or propagation error was detected in this scope. This is not an exhaustive record-by-record audit of every derived file.

## Rate and temperature interpretation

The existing local handoff and response metadata establish explicit LST daily support and PRECTOTCORR mm/day. A one-day mean rainfall rate multiplied by one day gives mm for that interval. Monthly accumulation sums each daily interval once; daily records and daily replay keep mm/day. No conversion factor of 24 or 86400 is applied. Temperature values remain Celsius. Monthly T2M_MIN/T2M_MAX values are means of daily extrema, not the lowest/highest temperature of the month.

Official references already recorded in the local preparation evidence (no new retrieval in this audit):

- [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [NASA POWER meteorological methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)
- [NASA POWER hydrology units](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/)

## Per-observation evidence

All paths below are repository-relative. Full retained headers, request parameters, exact daily/wide/monthly records, provisional chart selection metadata, neighbours and evidence-file SHA-256 values are in `data/climate/climate_extreme_value_audit.json`. Ties are counted and one observation is selected deterministically.

### 1. PRECTOTCORR — 965.18 mm/day, 2017-07-22 LST

Returned longitude/latitude: [91.25, 20.5]. Selection: padded_regional maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__PRECTOTCORR__20170101_20171231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2']`. Parameter metadata: `{'units': 'mm/day', 'longname': 'Precipitation Corrected'}`. Fill: `-999.0`.

Raw SHA-256: `37009d9e6a8f074ca5432fc494125737324339c92886e3b8e054acebca3b3e23`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/PRECTOTCORR/20170101_20171231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/PRECTOTCORR/20170101_20171231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__PRECTOTCORR__20170101_20171231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__PRECTOTCORR__20170101_20171231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-91.25-20.5-PRECTOTCORR.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2017.wide-replay.jsonl.gz`

Monthly value: 3237.0400000000004 mm; independent calculation: 3237.04; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2017-07-20: 106.49; 2017-07-21: 122.74; 2017-07-22: 965.18; 2017-07-23: 232.21; 2017-07-24: 174.51.

Spatial neighbours (same parameter/unit/date): (91.25, 21.0): 527.46 at 55.597540 km; (90.625, 20.5): 290.76 at 65.095797 km; (91.875, 20.5): 708.66 at 65.095797 km; (90.625, 21.0): 196.4 at 85.525527 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

### 2. PRECTOTCORR — 521.24 mm/day, 2019-07-07 LST

Returned longitude/latitude: [91.875, 21.5]. Selection: district_used_locations maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `inside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__PRECTOTCORR__20190101_20191231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2']`. Parameter metadata: `{'units': 'mm/day', 'longname': 'Precipitation Corrected'}`. Fill: `-999.0`.

Raw SHA-256: `325717e2cee839a5aeb48e594e5f54390920561b00b88f799174a63a24da75d4`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/PRECTOTCORR/20190101_20191231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/PRECTOTCORR/20190101_20191231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__PRECTOTCORR__20190101_20191231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__PRECTOTCORR__20190101_20191231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-91.875-21.5-PRECTOTCORR.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2019.wide-replay.jsonl.gz`

Monthly value: 3321.56 mm; independent calculation: 3321.56; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2019-07-05: 164.75; 2019-07-06: 190.38; 2019-07-07: 521.24; 2019-07-08: 138.79; 2019-07-09: 148.03.

Spatial neighbours (same parameter/unit/date): (91.875, 22.0): 561.92 at 55.597540 km; (91.875, 21.0): 431.3 at 55.597540 km; (91.25, 21.5): 538.55 at 64.661117 km; (92.5, 21.5): 174.9 at 64.661117 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-coxs-bazar`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-coxs-bazar-2019.wide-replay.jsonl.gz`; anchor-to-output distance 29.204961 km.

All observation lineage checks passed.

### 3. T2M — 8.39 C, 2013-01-09 LST

Returned longitude/latitude: [89.375, 26.0]. Selection: district_used_locations minimum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `inside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M__20130101_20131231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters'}`. Fill: `-999.0`.

Raw SHA-256: `7799a6786ad27d007cf294ba58ada979116a679767720b809af572e5d6fbc8ee`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20130101_20131231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20130101_20131231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20130101_20131231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20130101_20131231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-89.375-26.0-T2M.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2013.wide-replay.jsonl.gz`

Monthly value: 14.19225806451613 C; independent calculation: 14.192258064516128; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2013-01-07: 10.32; 2013-01-08: 8.87; 2013-01-09: 8.39; 2013-01-10: 9.79; 2013-01-11: 11.83.

Spatial neighbours (same parameter/unit/date): (89.375, 26.5): 10.35 at 55.597540 km; (89.375, 25.5): 8.99 at 55.597540 km; (88.75, 26.0): 8.65 at 62.463363 km; (90.0, 26.0): 8.44 at 62.463363 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-kurigram`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-kurigram-2013.wide-replay.jsonl.gz`; anchor-to-output distance 36.870778 km.
- `bd-district-lalmonirhat`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-lalmonirhat-2013.wide-replay.jsonl.gz`; anchor-to-output distance 24.942743 km.

All observation lineage checks passed.

### 4. T2M — 2.74 C, 2022-02-05 LST

Returned longitude/latitude: [89.375, 27.0]. Selection: padded_regional minimum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M__20220101_20221231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters'}`. Fill: `-999.0`.

Raw SHA-256: `07db62a5f66f7eb8c24908d75c7f06d236ffb7958ac418222e305999a00fb9b4`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20220101_20221231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20220101_20221231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20220101_20221231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20220101_20221231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-89.375-27.0-T2M.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2022.wide-replay.jsonl.gz`

Monthly value: 7.025 C; independent calculation: 7.0249999999999995; valid/expected days: 28/28. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2022-02-03: 6.2; 2022-02-04: 5.81; 2022-02-05: 2.74; 2022-02-06: 4.66; 2022-02-07: 5.19.

Spatial neighbours (same parameter/unit/date): (89.375, 26.5): 13.07 at 55.597540 km; (88.75, 27.0): 6.06 at 61.922150 km; (90.0, 27.0): 3.68 at 61.922150 km; (88.75, 26.5): 14.1 at 83.321013 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

### 5. T2M — 39.09 C, 2023-06-16 LST

Returned longitude/latitude: [87.5, 23.5]. Selection: padded_regional maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M__20230101_20231231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters'}`. Fill: `-999.0`.

Raw SHA-256: `3a2c42e19c61a0268a051f4fe8fb54db5fc1cabc950bd5de5cca52a82bd41395`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20230101_20231231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20230101_20231231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20230101_20231231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20230101_20231231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-87.5-23.5-T2M.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2023.wide-replay.jsonl.gz`

Monthly value: 33.41266666666666 C; independent calculation: 33.41266666666667; valid/expected days: 30/30. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2023-06-14: 36.66; 2023-06-15: 38.76; 2023-06-16: 39.09; 2023-06-17: 37.68; 2023-06-18: 35.97.

Spatial neighbours (same parameter/unit/date): (87.5, 23.0): 38.05 at 55.597540 km; (87.5, 24.0): 38.78 at 55.597540 km; (88.125, 23.5): 37.58 at 63.732805 km; (88.125, 24.0): 37.8 at 84.483378 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

### 6. T2M — 37.81 C, 2024-04-30 LST

Returned longitude/latitude: [88.75, 23.5]. Selection: district_used_locations maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `inside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M__20240101_20241231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters'}`. Fill: `-999.0`.

Raw SHA-256: `7a0430aa3b01d08025647b4fa110f7af7b2bd376620e56e0f3ab5044282bc63d`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20240101_20241231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M/20240101_20241231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20240101_20241231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M__20240101_20241231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-88.75-23.5-T2M.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2024.wide-replay.jsonl.gz`

Monthly value: 33.60366666666667 C; independent calculation: 33.60366666666667; valid/expected days: 30/30. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2024-04-28: 36.56; 2024-04-29: 36.84; 2024-04-30: 37.81; 2024-05-01: 37.53; 2024-05-02: 36.01.

Spatial neighbours (same parameter/unit/date): (88.75, 23.0): 37.88 at 55.597540 km; (88.75, 24.0): 37.11 at 55.597540 km; (88.125, 23.5): 37.88 at 63.732805 km; (89.375, 23.5): 36.95 at 63.732805 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-chuadanga`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-chuadanga-2024.wide-replay.jsonl.gz`; anchor-to-output distance 13.215459 km.

All observation lineage checks passed.

### 7. T2M_MAX — 47.81 C, 2002-05-20 LST

Returned longitude/latitude: [87.5, 22.5]. Selection: padded_regional maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MAX__20020101_20021231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Maximum'}`. Fill: `-999.0`.

Raw SHA-256: `40a588b2fc9edc03bc36b5070f9b6514dbdea9837161b3f73e4e5ca93a5d5495`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20020101_20021231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20020101_20021231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20020101_20021231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20020101_20021231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-87.5-22.5-T2M_MAX.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2002.wide-replay.jsonl.gz`

Monthly value: 41.12032258064516 C; independent calculation: 41.12032258064516; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2002-05-18: 41.66; 2002-05-19: 45.9; 2002-05-20: 47.81; 2002-05-21: 46.59; 2002-05-22: 46.49.

Spatial neighbours (same parameter/unit/date): (87.5, 22.0): 46.99 at 55.597540 km; (87.5, 23.0): 47.3 at 55.597540 km; (88.125, 22.5): 46.81 at 64.206740 km; (88.125, 23.0): 46.81 at 84.844479 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

### 8. T2M_MAX — 15.2 C, 2019-12-27 LST

Returned longitude/latitude: [89.375, 22.5]. Selection: district_used_locations minimum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `inside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MAX__20190101_20191231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Maximum'}`. Fill: `-999.0`.

Raw SHA-256: `fa0940c5ea0ad9d177205f51c14592ee4f10949d208ce15418f47017d099f4bd`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20190101_20191231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20190101_20191231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20190101_20191231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20190101_20191231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-89.375-22.5-T2M_MAX.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2019.wide-replay.jsonl.gz`

Monthly value: 23.795483870967743 C; independent calculation: 23.79548387096774; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2019-12-25: 22.58; 2019-12-26: 22.76; 2019-12-27: 15.2; 2019-12-28: 20.08; 2019-12-29: 21.47.

Spatial neighbours (same parameter/unit/date): (89.375, 22.0): 15.53 at 55.597540 km; (89.375, 23.0): 15.98 at 55.597540 km; (88.75, 22.5): 15.41 at 64.206740 km; (90.0, 22.5): 15.94 at 64.206740 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-khulna`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-khulna-2019.wide-replay.jsonl.gz`; anchor-to-output distance 4.549507 km.
- `bd-district-satkhira`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-satkhira-2019.wide-replay.jsonl.gz`; anchor-to-output distance 24.499363 km.

All observation lineage checks passed.

### 9. T2M_MAX — 5.89 C, 2022-02-05 LST

Returned longitude/latitude: [89.375, 27.0]. Selection: padded_regional minimum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MAX__20220101_20221231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Maximum'}`. Fill: `-999.0`.

Raw SHA-256: `4b81a4df1c9830bf3e857747352e943b0c77b7a7cc5fe128a376f6d0d6466d1a`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20220101_20221231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20220101_20221231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20220101_20221231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20220101_20221231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-89.375-27.0-T2M_MAX.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2022.wide-replay.jsonl.gz`

Monthly value: 12.427142857142856 C; independent calculation: 12.427142857142856; valid/expected days: 28/28. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2022-02-03: 11.03; 2022-02-04: 9.27; 2022-02-05: 5.89; 2022-02-06: 10.33; 2022-02-07: 10.28.

Spatial neighbours (same parameter/unit/date): (89.375, 26.5): 17.27 at 55.597540 km; (88.75, 27.0): 8.88 at 61.922150 km; (90.0, 27.0): 6.34 at 61.922150 km; (88.75, 26.5): 18.41 at 83.321013 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

### 10. T2M_MAX — 47.62 C, 2024-04-30 LST

Returned longitude/latitude: [88.75, 23.5]. Selection: district_used_locations maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `inside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MAX__20240101_20241231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Maximum'}`. Fill: `-999.0`.

Raw SHA-256: `6d3438221c453f3d68f35401366ca4b59c00de78a03c26c825bd85a726a003f4`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20240101_20241231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MAX/20240101_20241231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20240101_20241231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MAX__20240101_20241231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-88.75-23.5-T2M_MAX.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2024.wide-replay.jsonl.gz`

Monthly value: 42.357666666666674 C; independent calculation: 42.35766666666667; valid/expected days: 30/30. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2024-04-28: 45.38; 2024-04-29: 45.74; 2024-04-30: 47.62; 2024-05-01: 45.89; 2024-05-02: 44.38.

Spatial neighbours (same parameter/unit/date): (88.75, 23.0): 47.61 at 55.597540 km; (88.75, 24.0): 46.94 at 55.597540 km; (88.125, 23.5): 47.55 at 63.732805 km; (89.375, 23.5): 46.72 at 63.732805 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-chuadanga`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-chuadanga-2024.wide-replay.jsonl.gz`; anchor-to-output distance 13.215459 km.

All observation lineage checks passed.

### 11. T2M_MIN — 32.09 C, 2012-06-05 LST

Returned longitude/latitude: [87.5, 24.0]. Selection: padded_regional maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MIN__20120101_20121231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Minimum'}`. Fill: `-999.0`.

Raw SHA-256: `8d44183c0674c35f441ef6cbc6c473912167f56aa1611584e8632c865ed65e02`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20120101_20121231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20120101_20121231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20120101_20121231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20120101_20121231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-87.5-24.0-T2M_MIN.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2012.wide-replay.jsonl.gz`

Monthly value: 28.389333333333333 C; independent calculation: 28.389333333333333; valid/expected days: 30/30. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2012-06-03: 29.15; 2012-06-04: 29.92; 2012-06-05: 32.09; 2012-06-06: 29.58; 2012-06-07: 29.77.

Spatial neighbours (same parameter/unit/date): (87.5, 24.5): 31.34 at 55.597540 km; (87.5, 23.5): 31.74 at 55.597540 km; (88.125, 24.0): 31.73 at 63.488548 km; (88.125, 24.5): 31.59 at 84.297798 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

### 12. T2M_MIN — 31.59 C, 2012-06-05 LST

Returned longitude/latitude: [88.125, 24.5]. Selection: district_used_locations maximum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MIN__20120101_20121231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Minimum'}`. Fill: `-999.0`.

Raw SHA-256: `8d44183c0674c35f441ef6cbc6c473912167f56aa1611584e8632c865ed65e02`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20120101_20121231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20120101_20121231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20120101_20121231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20120101_20121231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-88.125-24.5-T2M_MIN.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2012.wide-replay.jsonl.gz`

Monthly value: 29.03733333333333 C; independent calculation: 29.037333333333333; valid/expected days: 30/30. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2012-06-03: 29.29; 2012-06-04: 29.74; 2012-06-05: 31.59; 2012-06-06: 29.33; 2012-06-07: 30.23.

Spatial neighbours (same parameter/unit/date): (88.125, 24.0): 31.73 at 55.597540 km; (88.125, 25.0): 30.7 at 55.597540 km; (87.5, 24.5): 31.34 at 63.239456 km; (88.75, 24.5): 30.07 at 63.239456 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-chapainawabganj`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-chapainawabganj-2012.wide-replay.jsonl.gz`; anchor-to-output distance 24.818573 km.

C: The adopted representative-point context uses a returned position outside the pinned Bangladesh geometry; this is a sampling limitation, not evidence of a processing error.

All observation lineage checks passed.

### 13. T2M_MIN — 1.23 C, 2013-01-09 LST

Returned longitude/latitude: [89.375, 26.0]. Selection: district_used_locations minimum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `inside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MIN__20130101_20131231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Minimum'}`. Fill: `-999.0`.

Raw SHA-256: `fb7f7142954a28f5a44720e95634b60d3c76201de5781904194dab5ac6e4888d`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20130101_20131231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20130101_20131231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20130101_20131231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20130101_20131231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-89.375-26.0-T2M_MIN.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2013.wide-replay.jsonl.gz`

Monthly value: 7.077419354838712 C; independent calculation: 7.077419354838709; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2013-01-07: 4.0; 2013-01-08: 1.74; 2013-01-09: 1.23; 2013-01-10: 2.53; 2013-01-11: 4.69.

Spatial neighbours (same parameter/unit/date): (89.375, 26.5): 3.63 at 55.597540 km; (89.375, 25.5): 2.08 at 55.597540 km; (88.75, 26.0): 2.18 at 62.463363 km; (90.0, 26.0): 1.75 at 62.463363 km.

District context (same daily values and provenance, no correction needed):

- `bd-district-kurigram`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-kurigram-2013.wide-replay.jsonl.gz`; anchor-to-output distance 36.870778 km.
- `bd-district-lalmonirhat`: `cache/nasa_power_regional/prepared-v1/district-context/bd-district-lalmonirhat-2013.wide-replay.jsonl.gz`; anchor-to-output distance 24.942743 km.

All observation lineage checks passed.

### 14. T2M_MIN — -0.93 C, 2013-12-15 LST

Returned longitude/latitude: [89.375, 27.0]. Selection: padded_regional minimum (1 tied observations).

Classification: **B**. Faithfully preserved unusual source value; physical accuracy unresolved. Geography: `padded_area_only_outside_pinned_Bangladesh_geometry`.

Request ID: `bgd-padded-national__T2M_MIN__20130101_20131231`. API: `{'version': 'v2.10.3', 'name': 'POWER Daily API'}`. Sources: `['MERRA2', 'POWER']`. Parameter metadata: `{'units': 'C', 'longname': 'Temperature at 2 Meters Minimum'}`. Fill: `-999.0`.

Raw SHA-256: `fb7f7142954a28f5a44720e95634b60d3c76201de5781904194dab5ac6e4888d`.

- Raw: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20130101_20131231.json`
- Request manifest: `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/bgd-padded-national/T2M_MIN/20130101_20131231.manifest.json`
- Normalized: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20130101_20131231.jsonl.gz`
- Monthly: `cache/nasa_power_regional/prepared-v1/bgd-padded-national__T2M_MIN__20130101_20131231.monthly.json`
- Chart: `cache/nasa_power_regional/prepared-v1/chart-89.375-27.0-T2M_MIN.json`
- Daily wide replay: `cache/nasa_power_regional/prepared-v1/2013.wide-replay.jsonl.gz`

Monthly value: 5.381935483870967 C; independent calculation: 5.381935483870968; valid/expected days: 31/31. The matching chart monthly record agrees exactly.

Temporal neighbours (same parameter/unit, LST dates): 2013-12-13: 5.0; 2013-12-14: 4.74; 2013-12-15: -0.93; 2013-12-16: 1.73; 2013-12-17: 2.05.

Spatial neighbours (same parameter/unit/date): (89.375, 26.5): 10.7 at 55.597540 km; (88.75, 27.0): 5.51 at 61.922150 km; (90.0, 27.0): 3.0 at 61.922150 km; (88.75, 26.5): 12.02 at 83.321013 km.

District context: no adopted district mapping uses this location; no district export contains this selected observation.

All observation lineage checks passed.

## Impact, unresolved questions and limits

Step 2 clarification: the unchanged Chapainawabganj registry anchor is
(88.256694, 24.688357), strictly inside its assigned pinned district. Only the
selected API output position (88.125, 24.5) is outside the pinned country
polygons, 24.8185734952679 km away. See the
[current method handoff](CLIMATE_REGIONAL_HANDOFF.md) and
[coordinate-role evidence](../../data/climate/climate_coordinate_role_check.json).
The audit findings below concern the output position, not the original anchor.

No category A processing error was established, so responsible pipeline code and all source/derived climate outputs remain unchanged. Category B means preservation is verified, not that the weather value is physically validated. No thresholds, clipping, zero replacement, interpolation or meteorological certification is introduced.

The outside-country source maxima affect only their regional node monthly/chart/replay data; they do not affect district-context outputs because those coordinates are unused. The seven district-used extrema propagate faithfully into the listed district files; this is existing source influence, not a newly discovered processing defect. Districts sharing one returned point receive the same observations.

Category C: Chapainawabganj context selects (88.125, 24.5), outside the pinned Bangladesh geometry. Its 31.59 C daily minimum on 2012-06-05 is faithfully preserved. The adopted nearest-point method does not constrain returned positions to the pinned country polygons; an outside-polygon position is not independent proof of a surveyed international-border crossing; whether that context is adequate for downstream decisions needs source/spatial review. No mapping or distance rule was changed in this audit. No inference is made about the full source footprint.

Category C: the 965.18 mm/day source rate, other unusual values and their neighbouring values require upstream product/event or independent observation evidence to assess physical accuracy. Temporal/spatial coherence is diagnostic, not independent validation. No additional request is necessary to establish the local lineage result; this audit makes none. Agronomic interpretation remains outside scope.

All 17 negative T2M_MIN values were recounted directly from raw files; other parameters have no negative non-fill values. Negative Celsius is not automatically invalid. This audit checks their source-level temperature ordering through the full-triplet scan and traces the global negative minimum; it does not provide separate full lineage sections for all 17 negative records.

## Reproduction and verification

From repository root; the audit command reads local evidence and writes only its JSON and Markdown reports:

```bash
OFFLINE=1 python3 -B src/acquire/audit_climate_extremes.py
python3 -B -m unittest tests.test_climate_extreme_audit tests.test_nasa_power_regional_acquire tests.test_nasa_power_regional_prepare -v
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/workflow.py render
python3 scripts/workflow.py check
git diff --check
```

Recorded verification for this audit: 95 repository tests and 25 focused audit/acquisition/preparation tests passed. The offline audit command passed. Workflow and whitespace validation results are recorded in `docs/tasks/CLIMATE-EXTREME-AUDIT.json`; independent review remains pending.

Audit additions: `src/acquire/audit_climate_extremes.py`, `tests/test_climate_extreme_audit.py`, `docs/data/CLIMATE_EXTREME_VALUE_AUDIT.md`, `data/climate/climate_extreme_value_audit.json`, `docs/tasks/CLIMATE-EXTREME-AUDIT.json`; the canonical `docs/AI_USE.md` log and generated `docs/PROGRESS.md`/`README.md` also update. All pre-existing work is preserved. No frontend checks are needed because frontend behavior is unchanged. No staging, commit, push, merge or deployment is authorized or performed.
