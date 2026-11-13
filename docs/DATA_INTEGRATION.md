> Recent-weather extension: `make backend` additionally imports the checksum-pinned `data/climate/recent/` snapshot (2026-01-01–2026-11-12; complete across all four parameters through November 10). Annual history remains 2001–2025. `data/rules/exposure_references.json` is a source-scoped warning transcription, not an activated rotation rule. See [QA audit](QA_AUDIT.md).

# Local data integration and output generation

The website, API and reports run on **http://localhost:3000**. SQLite is a local file, not a cloud service. No account, NASA key, model API or additional backend port is required.

## Run

From the repository root:

```bash
make backend
cd prototype
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3000 --webpack
```

`make backend` verifies the existing evidence and sealed NASA archive, builds the local SQLite indexes, and verifies daily/annual agreement. It is offline and idempotent. First indexing takes longer than subsequent startup. Dependency installation requires a package cache or network; map tiles/fonts and whole-browser offline operation are separate concerns.

Default private database: `cache/application/soil-to-stars.sqlite3` (gitignored, file mode 0600). Python 3.9+ and the locked Node/npm dependencies are sufficient. Optional `STS_PYTHON` and `STS_DB_PATH` environment overrides select a Python executable or private database path. Preserve the SQLite file when retaining results; it is not included in Git. A fresh clone rebuilds evidence, but cannot recover a previous device's submissions without that database.

## One input, two explicit evidence paths

```text
farmer-intake.v2
  ├─ district_id → district_memberships → BAMIS region_id
  │                                     ↓
  │   intake crop_id → crop_aliases → original source crop_id
  │                                     ↓
  │                  region_id + crop_id → source calendars/entries
  │                                     ↓
  │                  printed normals, stages, source IDs, missing definitions
  │
  └─ district_id → preserved representative-point mapping → NASA grid_id
                                                       ↓
                             daily observations / exact historical windows
                             annual summaries / descriptive period comparison
```

A farm pin is checked against local district geometry. Weather currently uses the adopted **district-anchor representative point**, not the exact farm pin, a district average or field-level resolution. The report states the actual grid coordinates and anchor distance. BAMIS region membership is source-derived context, not proof of agronomic applicability.

## Maruf's crop data

Original evidence is preserved in `data/catalog/normalized/` and verified against its existing receipt. We do not overwrite values, merge distinct regional calendars or reinterpret printed weeks as ISO dates.

- `crops` retains the 29 original crop IDs/labels.
- `crop_aliases` maps 30 stable intake identities to source crop IDs using `data/integration/crop_aliases.json`. Existing rice/maize/lentil/mustard/mungbean/sesame/jute IDs are retained. Sesame remains available for input but has no collected crop-calendar counterpart.
- `regions` and `districts` preserve all 14 source regions and 64 memberships.
- `calendars` retains all 366 source-table identities, including season/system labels and unresolved variety/event definitions.
- `calendar_entries` preserves 7,834 entries and their column/stage/week lineage.
- `crop_observations` stores 54,838 numeric or explicitly missing printed observations, with canonical metric, unit, source and definition IDs. All have `usable_as_threshold=0`.
- `rule_candidates` retains 14 candidate evidence records as inactive. The executable `rules` registry is separate and currently empty.

Crop label identity is not a variety, rice production system, botanical-family approval or recommendation. Generic rice does not select Aman/Boro/Aus automatically. A printed life span is not assigned to sowing→maturity or harvest→clearance without evidence for those events.

## Saim's NASA data

The sealed archive stays unchanged. Its checksum is verified before daily indexing. Prepared grid/date values are read sequentially from the archive without downloading NASA data or extracting arbitrary paths.

- `weather_grids`: 42 distinct mapped points shared by the 64 district selections.
- `weather_daily`: 383,502 date/point rows, each preserving T2M, T2M_MIN, T2M_MAX and PRECTOTCORR, including real zeros and missingness.
- `weather_raw_sources` and `weather_daily_partitions`: original artifact hashes, source units, LST, partition hashes and archive identity.
- `weather_annual`: 2,100 temperature/rainfall summaries.

Daily precipitation remains **mm/day**. Summing it over explicit one-day steps gives an amount in **mm** for the named window. Temperature source `C` represents degrees Celsius (`degC`) with no value scaling. Mean temperature, absolute minimum and absolute maximum remain different statistics. Daily/annual parity is checked against all 2,100 existing annual summaries with absolute tolerance 0.001 in the respective units.

Dates outside 2001–2025 return unavailable. Historical data is not silently shifted into the future. An optional reported sowing date can define a descriptive historical occupancy window ending at field availability, but does not establish a crop stage or a tolerance assessment.

## Joining metrics does not create thresholds

| Preserved crop field | NASA counterpart | Required agreement before a numerical comparison |
| --- | --- | --- |
| `rainfall_mm` | `PRECTOTCORR` | Accumulation days, period, normal statistic and spatial method |
| `temp_mean_c` | `T2M` | Averaging convention, days and reference/spatial context |
| `temp_min_c` | `T2M_MIN` | Absolute minimum versus mean daily minima and matching days |
| `temp_max_c` | `T2M_MAX` | Absolute maximum versus mean daily maxima and matching days |
| Humidity, sunshine duration, wind | None in this archive | Acquire appropriate data and define compatible metrics; no substitutes |

`metric_contract.py` standardizes metric/unit labels while preserving unresolved definitions. It does not rescale temperature/rainfall into a common 0–1 scale, infer missing values, or convert historical normals into crop tolerance limits.

Thresholds belong in `data/rules/registry.json`, addressed by an immutable rule ID/version, exact crop/region/system/variety/stage applicability, metric/statistic, unit, inclusive/exclusive interval, source IDs/locator, missingness policy and explicit review record. Preparation, growth, harvest/collection and clearance require separate event-defined duration evidence. The current empty registry is intentional: zero reviewed executable rules were supplied.

`rule_engine.py` contains tested indicator, threshold, operation-duration and score primitives. Inactive rules return unknown; missing essential checks block scores; essential failures cannot be rescued by weights. These helpers are not an activated three-crop scheduling/ranking engine.

## Farmer inputs and output

The server reuses the actual intake validator. It rejects invalid dates, missing core answers, contradictory absence states, unsupported crop identities, hidden farm coordinates in district mode and map/district disagreements. Client-supplied planning markers, scores and thresholds are not trusted as scientific output.

A valid request:

1. Resolves crop, district, source-region and NASA point identities.
2. Loads preserved calendar evidence, canonical observations and local weather.
3. Reports supported historical context and the exact missing scientific definitions.
4. Saves immutable input/result rows with UUIDs and canonical fingerprints.
5. Returns a genuine `local_evidence` report to the workspace; JSON export retains its sources and limitations.
6. Restores the same saved report after reload when the original inputs match. Restored reports are labelled and can be regenerated.

`report_status: complete` means the evidence report was generated. `status: incomplete` / `comparison_status: incomplete` mean crop planning remains unsupported. Zero alternatives, null scores and unknown vulnerability are not replaced by examples.

The fingerprint covers canonical inputs and the evidence report, including source identity and method version. Random delivery IDs and generation time are kept outside that fingerprint. Original inputs remain unchanged by what-if requests; each scenario is a separate saved submission.

## Local endpoints

| Endpoint | Behavior |
| --- | --- |
| `GET /api/health` | Local setup/counts, without submitted field contents |
| `POST /api/plan` | Validate, join evidence, save and return a report |
| `POST /api/climate` | Local weather context for a valid intake |
| `POST /api/current-crop` | Same report's current-crop unknown/assessment state |
| `GET /api/results/{uuid}` | Retrieve one result and its original input |
| `GET /api/submissions/{uuid}` | Retrieve one submission's result |

The service accepts localhost hosts and same-origin requests, caps request/response sizes and worker duration, uses parameterized SQL and exposes no submission-listing endpoint. IDs are unguessable local retrieval capabilities, not account authentication. Anyone with local filesystem access or a shared capability URL can access that data. Do not deploy this personal local service publicly without designing authentication, privacy and hosting separately.

## Regression and the remaining work

The imported packages contain weather/context, calendars and candidate agronomic statements. They do **not** contain measured field outcomes or calibrated suitability-score labels for supervised crop recommendation. Training on invented scores would reproduce invented assumptions. High tuning is therefore not enabled.

Next: resolve the report's missing source definitions; record applicable reviewed crop/stage/window and operation rules; implement common-period three-crop scheduling and baseline assessment; validate results against independent examples/outcomes. A future regression model needs a declared target, relevant outcome labels and a held-out temporal/location evaluation against a simple baseline before it affects recommendations.

## Verification — 13 November 2026

Passed 94 Python tests, 60 existing UI tests, 11 local API integration tests, frontend lint and production build. The actual project's offline daily index was built and checked against all 2,100 annual summaries. The database's foreign-key check returned no violations.

Browser verification generated a genuine report from valid field answers, restored its original result ID after reload, exported a non-fixture JSON receipt, evaluated a separate irrigation/priority scenario with explicit seasonal-limit answers, and confirmed the original field answers stayed unchanged. EN/BN report headings and a no-overflow check at 605px passed. Physical phone/touch, final print output and complete disconnected-browser operation remain separate checks. These results establish software/data integration, not agronomic field accuracy.
