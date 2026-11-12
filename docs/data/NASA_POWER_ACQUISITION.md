# NASA POWER daily acquisition

## Scope and status

Step 2 configured nationwide acquisition and verified the client with a
four-request smoke test. It does not run the full 64-district, 2001–2025
collection, calculate indicators, integrate scientific API responses, or
advance G0. `CLIMATE-POWER-ACQUIRE` is independent preparation with no G0
dependency.

Step 3's required request-reuse review found no documented, parameter-complete
pre-request equivalence key. The full acquisition therefore remains unstarted
and is now blocked by an explicit execution gate. See
[NASA_POWER_REDUNDANCY_REVIEW](NASA_POWER_REDUNDANCY_REVIEW.md) and the
machine-readable full plan/summary for the evidence and exact counts.

The checked-in evidence consists of:

- `data/climate/nasa_power_daily_v1.json`: versioned collection configuration
  containing all 64 registry points.
- `data/climate/nasa_power_smoke_test_manifest.json`: four live request results,
  returned metadata and raw-response checksums.
- `src/acquire/download_nasa_power.py`: standard-library configuration builder,
  dry-run planner, validator and resumable downloader.
- `tests/test_nasa_power_acquire.py`: synthetic-only unit tests. Synthetic
  values are explicitly labelled and are never presented as NASA observations.

Original HTTP response bytes and per-request manifests are retained under the
ignored `cache/nasa_power/` tree. They are not committed data assets.

## Official API contract

Official NASA POWER sources were accessed on 13 November 2026:

- [Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [API overview and errors](https://power.larc.nasa.gov/docs/services/api/)
- [Official data-request tutorial](https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/)
- [Daily OpenAPI schema](https://power.larc.nasa.gov/api/temporal/daily/openapi.json)
- [Manager parameter endpoint](https://power.larc.nasa.gov/api/system/manager/parameters)
- [Temporal processing](https://power.larc.nasa.gov/docs/methodology/data/processing/)

The configured endpoint is the Daily Point API with community `AG`
(Agroclimatology), JSON format and metric community units. The current OpenAPI
schema identified itself as POWER Daily API `v2.10.3` during verification and
in every smoke response.

| Parameter | Official daily AG meaning | Unit |
| --- | --- | --- |
| `PRECTOTCORR` | Bias-corrected total precipitation at the surface | `mm/day` |
| `T2M` | Mean air temperature at 2 metres | `C` |
| `T2M_MIN` | Minimum hourly air temperature at 2 metres in the daily period | `C` |
| `T2M_MAX` | Maximum hourly air temperature at 2 metres in the daily period | `C` |

Daily UTC and Local Solar Time are documented from 1 January 1981 to near real
time. The configuration sends `time-standard=LST` explicitly. LST matches the
documented daily solar-day aggregation and avoids relying on the API default.
The API documents `-999` as the missing/fill value; the validator reads and
checks the returned header instead of replacing it.

Official restrictions and the local policy are kept distinct:

- A single-point request accepts at most 20 parameters; this configuration
  requests four.
- The official multipoint tutorial says not to exceed five concurrent
  requests. General guidance warns that excessive synchronous access or
  repeated requests for the same relative grid location may be blocked.
- The API documents HTTP 429 for excessive requests and 422 for permanent
  validation failures. The reviewed documentation does not publish a numeric
  requests-per-second quota.
- The downloader is deliberately sequential (`concurrency=1`) with a one-second
  inter-request delay, 60-second timeout and at most four total attempts.
  Transient 408/429/5xx responses use bounded exponential backoff and honor a
  valid `Retry-After`; other 4xx responses stop immediately.

NASA does not publish a smaller mandatory date-span limit for this
four-parameter daily point request. The project uses one calendar year per
request to bound response size and make resume/checksum evidence granular.

## Requested and verified coverage

Requested full coverage is all 64 registry points from 1 January 2001 through
31 December 2025 for the four parameters above. With 25 calendar-year chunks
per point, the configured maximum is:

```text
64 points × 25 annual chunks = 1,600 requests
```

This requested coverage is configuration intent. Actual verified coverage is
recorded only after structural response validation. Step 2 verifies four
one-month slices, not the full period:

| District | Selection reason | Periods | Result |
| --- | --- | --- | --- |
| Bagerhat | Southwestern coastal point, geographically contrasting with the hill point | January 2001 and January 2025 | Both passed |
| Rangamati | Southeastern hill point and distant coordinate | January 2001 and January 2025 | Both passed |

Each response returned HTTP 200, 31 ordered dates, the exact four parameters,
the expected units, `LST`, fill value `-999`, sources `MERRA2` and `POWER`, and
POWER Daily API `v2.10.3`. All four parameter series had zero fill values in
these four slices. Returned response geometry was preserved as metadata; no
NASA grid-cell ID was created. The exact raw SHA-256 values and byte counts are
in `data/climate/nasa_power_smoke_test_manifest.json`.

## Commands

Run from the repository root with Python 3; no third-party Python dependency or
API key is required.

Regenerate and verify the configuration, then show the four smoke requests
without network access:

```bash
python3 src/acquire/download_nasa_power.py --write-config --check-config --scope smoke
```

Write the full request-reuse decision, dry-run plan and current blocked summary
without downloading data:

```bash
python3 src/acquire/download_nasa_power.py --check-config --scope full --write-reuse-decision --write-full-plan
```

Execute only the smoke test:

```bash
python3 src/acquire/download_nasa_power.py --config data/climate/nasa_power_daily_v1.json --scope smoke --execute
```

Run the synthetic acquisition tests:

```bash
python3 -B -m unittest tests.test_nasa_power_acquire -v
```

The full-download/resume command was attempted in Step 3. The reuse guard
stopped it before any network request and will continue to do so until a
verified authoritative mapping replaces the blocked decision:

```bash
python3 src/acquire/download_nasa_power.py --config data/climate/nasa_power_daily_v1.json --scope full --execute --confirm-full-collection
```

`OFFLINE=1` blocks either live execution scope.

## Storage, validation and resume

Raw layout:

```text
cache/nasa_power/nasa-power-daily-bgd-64-v1/
  raw/{district_id}/{YYYYMMDD}_{YYYYMMDD}.json
  raw/{district_id}/{YYYYMMDD}_{YYYYMMDD}.manifest.json
  errors/{district_id}/{request_id}.{attempt}.{timestamp}.{body|partial|json}
```

The raw JSON file is the exact HTTP response body. It is streamed to a temporary
file, structurally validated, flushed, and atomically moved to its final path.
A valid request manifest records collection/configuration identity, registry
checksum, district and coordinates, request URL and parameters, attempt,
request/retrieval timestamps, HTTP status, content type, byte count, SHA-256,
returned dates, parameters, units, time standard, fill value/counts, API/source
metadata and response geometry.

Resume accepts a cached response only when its request fingerprint, raw
checksum, byte count and fresh structural validation all match. Missing,
incomplete, corrupt or mismatched files are never reported as successes.
Corrupt pairs are moved to ignored error storage before a new attempt;
interrupted partial bytes and HTTP/API error bodies are retained with failure
metadata.

Validation rejects HTTP success with an API error shape, invalid JSON, missing
metadata, unexpected/missing/reordered dates, substituted or extra parameters,
wrong units, wrong time standard, wrong fill value, or a response range that
does not exactly match the request.

## Remaining blockers before full collection

- Independent human review of the parameter/source contract and acquisition
  method is still pending.
- Only four month-point combinations are verified. The rest of 2001–2025 and
  the other 62 districts remain unrequested.
- POWER warns against repeatedly requesting the same relative grid location,
  but the reviewed official documentation and v2.10.3 schema do not provide a
  cell ID or point-to-cell mapping. The Daily API's 0.5° × 0.5° wording also
  differs from the documented ½° × ⅝° meteorological source resolution. This
  must be resolved with official, parameter-complete evidence; no grid-cell ID
  or local snapping rule may be guessed.
- API schema/version and live availability should be rechecked immediately
  before the long run. Any error or unavailable coverage must stay explicit.
- Storage/time estimates should be based on a reviewed dry-run and smoke bytes,
  not treated as guaranteed service behavior.

## AI-assisted work

Saim defined the nationwide period, variables, smoke scope and operational
constraints. Codex inspected Step 1, verified official NASA documentation and
live parameter metadata, implemented the configuration/downloader/tests, ran
the four-request smoke test and recorded checksums and limitations. The
canonical contribution record is `docs/AI_USE.md`; AI assistance does not count
as independent scientific approval.
