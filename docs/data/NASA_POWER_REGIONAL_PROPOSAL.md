# NASA POWER Daily Regional acquisition proposal

## Recommendation

The Daily Regional API is a technically suitable acquisition alternative worth
advancing to a national-extent preflight, but it is not yet approved as a
replacement scientific sampling method. Step 3B therefore stops before the
full 2001–2025 collection.

The regional route removes the need to invent a pre-request point-to-cell
equivalence mapping: POWER returns a set of output coordinates for an explicit
area. In the bounded smoke test, all four parameters returned the same 12
coordinate pairs and three dates, so they can be joined by exact returned
longitude, latitude and date for that smoke result. This does not establish
that the coordinates are unique native source cells, that all parameters have
identical upstream support, or that the Regional result is equivalent to the
Point API.

The blocked Point API finding in
[NASA_POWER_REDUNDANCY_REVIEW](NASA_POWER_REDUNDANCY_REVIEW.md) remains valid.
Its execution gate was not changed or bypassed.

## Current official and observed contract

Official sources were accessed on 13 November 2026:

- [Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
  documents daily Regional requests, a lower-left/upper-right bounding box,
  one parameter per Regional submission, JSON/CSV/ASCII/NetCDF formats, and
  explicit `LST` or `UTC`.
- [Temporal API overview](https://power.larc.nasa.gov/docs/services/api/temporal/)
  describes Regional output as time series for a bounding box.
- [Daily OpenAPI v2.10.3](https://power.larc.nasa.gov/api/temporal/daily/openapi.json)
  accepts latitude in `[-90, 90]`, longitude in `[-180, 180]`, dates beginning
  at 1981-01-01, formats JSON/CSV/ASCII/NetCDF/XARRAY and recommends NetCDF for
  large regions.
- [Official request tutorial](https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/)
  says not to request more finely than current resolution and not to submit
  excessive synchronous traffic. It describes meteorology as 0.5° latitude by
  0.625° longitude.

The reviewed Daily documentation and OpenAPI schema publish no numeric maximum
bounding-box span, date-span limit, response-value limit or requests-per-second
quota for Regional requests. Absence of a published limit is not evidence of
unlimited service capacity.

Live behaviour added two restrictions/evidence points not expressed as numeric
constraints in the OpenAPI schema:

- A four-parameter request returned HTTP 422 with “maximum of 1” parameter.
  The preserved error-body SHA-256 is
  `886e416a9e0efb3a80af2c69ff892a5fce32ab366699a5e2c1d6aaa3b626ca5b`.
- The original 0.7° × 0.8° smoke box returned HTTP 422 requiring at least a 2°
  latitude range and 2° longitude range. The single-parameter error-body
  SHA-256 is
  `d8037dee0c7db87edb52d9d2de75091422b6ca0eeb8a7d35c287b3e4b229b6f7`.

Both raw error bodies and request records remain in ignored cache storage. No
422 response was retried as though it were transient.

## Proposed national coverage

The pinned ADM2 geometry extent is:

```text
longitude 88.00862798600008 to 92.68025738200004
latitude  20.590609348000044 to 26.634513010000035
```

The proposal uses one non-overlapping national request area rather than tiles.
One officially documented meteorological spacing is added on every side so the
request can return an output coordinate beyond each administrative edge without
assuming grid origin or snapping:

```text
longitude 87.383628 to 93.305257
latitude  20.090609 to 27.134513
```

Using one area avoids duplicated tile boundaries and undocumented inclusive
edge behaviour. The padding is an acquisition edge-coverage rule, not a claim
about native cell polygons. A future national-extent preflight must confirm the
actual returned coordinate extent before historical execution.

The proposed historical plan remains 2001-01-01 through 2025-12-31, explicit
LST, AG metric units, one calendar year per request and one parameter per
request:

```text
1 area × 25 annual chunks × 4 parameters = 100 requests
```

This is a proposal count, not completed coverage. No full Regional request was
made in Step 3B.

## Bounded smoke test

The accepted test box was the minimum live-supported 2° × 2° central Bangladesh
area: longitude 89.5–91.5 and latitude 22.75–24.75. The period was 1–3 January
2001. Requests were sequential and limited to four successful responses.

All four responses passed structural validation:

- `PRECTOTCORR`: 12 output coordinates × 3 dates, `mm/day`, zero `-999` values,
  raw SHA-256
  `19d17a863eacedfb5b82952dcb8616c562c1cd15d5c5b19cec6c44b86ffc484e`.
- `T2M`: 12 × 3, `C`, zero `-999` values, raw SHA-256
  `3d710761bea93dfd4ed1401d628b32414242c7be07b4feb7e605f817e7e7b6b0`.
- `T2M_MIN`: 12 × 3, `C`, zero `-999` values, raw SHA-256
  `02e2f4dfe313d1441bd2bfae7c22c210ffcabf8612c974257f4376e3734a82b9`.
- `T2M_MAX`: 12 × 3, `C`, zero `-999` values, raw SHA-256
  `68d67e5c89c646b1d3ebe66b1f71f2b9dd7f229183959e46446ede5c3a8b88ba`.

Every response reported POWER Daily API v2.10.3 and LST. Returned coordinates
were longitude/latitude pairs from 90.0–91.25 and 23.0–24.5, with exact
coordinate-set SHA-256
`64c847cd7324769e960e33615e2b3daad0308c0228077e0f1190bc3beda8095a`
for all four responses. `PRECTOTCORR` and `T2M` listed source `MERRA2`;
`T2M_MIN` and `T2M_MAX` listed `MERRA2` and `POWER`. That metadata difference
is retained and is one reason not to infer identical native support.

The smoke configuration uses JSON, so no additional parser dependency was
needed. NASA recommends NetCDF for large regions; a later national-extent
preflight should measure the annual JSON response before choosing a different
format and adding a minimal NetCDF dependency.

## Combining parameters and district extraction

Combination is permitted only after each parameter response passes all of
these checks for the same area and dates:

1. exact returned longitude/latitude coordinate set;
2. exact date set and LST;
3. expected parameter name and units;
4. explicit fill convention and independently retained source metadata.

The join key is `(returned_longitude, returned_latitude, date)`. It is an
output-coordinate join, not a NASA native-cell ID.

The reproducible district extraction proposal is nearest returned output point
to each unchanged registry coordinate using WGS84 great-circle distance.
Ties are ordered by distance, returned latitude and returned longitude. Each
mapping must retain district ID, original coordinate, returned coordinate,
distance, request ID, parameter/date coverage and raw checksum.

For the 24 registry points located inside the smoke request box, diagnostic
nearest-node distances ranged from 13.231669 km to 50.510907 km; Dhaka was
36.483397 km from its nearest returned node. No acceptable-distance threshold
is invented. National edge extraction must fail closed if the padded response
does not provide adequate surrounding output coordinates.

This method changes the original sampling contract: the Step 1 point stays
unchanged as the district anchor, but observations would come from a recorded
nearby Regional output coordinate instead of a Point API request at that
anchor. Independent scientific review is required before adoption.

## Storage, commands and resume

Checked-in configuration and evidence:

```text
data/climate/nasa_power_daily_regional_v1.json
data/climate/nasa_power_regional_smoke_test_manifest.json
```

Ignored raw layout:

```text
cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/
  raw/{area_id}/{parameter}/{start}_{end}.json
  raw/{area_id}/{parameter}/{start}_{end}.manifest.json
  errors/{area_id}/{request_id}.{attempt}.{timestamp}.{body|partial|json}
```

Dry run and configuration check:

```bash
python3 src/acquire/download_nasa_power_regional.py --check-config --plan smoke --probe-multi-parameter
```

The executed smoke command was:

```bash
python3 src/acquire/download_nasa_power_regional.py --check-config --plan smoke --execute-smoke --probe-multi-parameter
```

Resume validates the request fingerprint, raw byte count, SHA-256 and response
structure before accepting a cached response. Corrupt evidence is quarantined;
partial and API-error bodies are preserved. `OFFLINE=1` blocks live execution.
The module intentionally provides no full-execution flag in Step 3B.

## Remaining blockers

Before full historical acquisition:

1. independently review and explicitly adopt or reject nearest-output-node
   extraction as a change to the district sampling contract;
2. run a separately authorized national-bbox, one-parameter, one-year preflight
   to verify actual edge coordinates, response bytes, latency and JSON/NetCDF
   choice;
3. require exact coordinate/date alignment again for all four parameters at
   national extent and preserve differing source metadata;
4. define a reviewed distance/edge acceptance policy without relabeling output
   nodes as unique native cells.

G0 was not advanced or accepted. No crop suitability, frontend, model,
normalization or full historical acquisition work was performed.
