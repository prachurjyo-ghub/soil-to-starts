# NASA POWER Regional national-extent preflight — PRECTOTCORR 2001

## Result and recommendation

One annual national-area JSON request is operationally practical based on this
bounded observation. Continue to propose one national area, one parameter and
one calendar year per request, executed sequentially with checksum-aware
resume. Do not start the 100-request historical plan until the remaining
parameter-alignment and extraction decisions are separately reviewed and
authorized.

This preflight validates raw Regional coverage only. It does not generate
district weather series, approve nearest-node sampling, choose a distance
threshold, interpolate, aggregate districts, or identify native NASA cells.
The Point API reuse blocker remains unchanged.

## Format choice

JSON was selected before execution. The existing Regional implementation
already preserves exact JSON bytes and validates its coordinates, dates,
parameter metadata, units, LST and fill convention with the Python standard
library. The [Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
supports both JSON and NetCDF for Regional requests, while the current OpenAPI
description recommends NetCDF for large regions. This preflight measured the
actual annual national JSON result before adding a NetCDF dependency. No second
format was downloaded for comparison.

The result does not justify a format change: 823,232 bytes (approximately
0.785 MiB) parsed and validated successfully. Retain annual JSON chunks unless
later parameters or years produce materially different observed behaviour.

## Exact request

The request used the unchanged padded national bounding box from
`data/climate/nasa_power_daily_regional_v1.json`:

```text
longitude 87.383628 to 93.305257
latitude  20.090609 to 27.134513
parameter PRECTOTCORR
period    2001-01-01 to 2001-12-31
community AG
time      LST
units     metric
format    JSON
```

That box reproduces the pinned administrative geometry extent plus one
documented meteorological spacing on each side: 0.625° longitude and 0.5°
latitude. No grid origin, snapping rule or cell ID is inferred.

Executed command:

```bash
python3 src/acquire/download_nasa_power_regional.py --check-config --plan preflight --execute-preflight
```

Exactly one successful data request was made. No other year, parameter or
format was requested.

## Response and QA

- HTTP status: 200.
- Retrieval time: 2026-11-12T21:20:42Z.
- Observed elapsed time: 2.865375 seconds.
- Exact raw bytes: 823,232.
- Raw SHA-256:
  `f6e7f87c045323d9e22e168688c22ce77ac947d00e1e66c014d6da90b29235ab`.
- Content type: `application/json`; the recorded `Content-Length` was 823,232.
- API: POWER Daily API v2.10.3.
- Title: `NASA/POWER Source Native Resolution Daily Data`.
- Source metadata: `MERRA2`.
- Unit: `mm/day`; time standard: `LST`; fill value: `-999`.

The response contained 140 output coordinates. All 140 longitude/latitude
pairs were unique within the response. These are API-returned output
coordinates, not asserted native cell identifiers.

Every output coordinate contained all 365 expected ordered dates. Expected and
returned values both equal:

```text
140 coordinates × 365 dates = 51,100 values
```

Value QA, with no correction or substitution:

- Fill values: 0.
- Non-fill values: 51,100.
- Minimum: 0.0 mm/day.
- Maximum: 161.68 mm/day.
- Negative non-fill values: 0.
- Non-finite values: 0.
- Boolean values: 0.

## Spatial and edge behaviour

Returned coordinate extent:

```text
longitude 87.5 to 93.125
latitude  20.5 to 27.0
```

The service returned coordinate centres inset from the requested edges:

- west 0.116372°, east 0.180257°;
- south 0.409391°, north 0.134513°.

Despite that inset, the returned extent extended beyond the pinned Bangladesh
boundary on every side:

- west 0.508628°, east 0.444743°;
- south 0.090609°, north 0.365487°.

All 64 unchanged district sampling points lie within the returned coordinate
extent. This proves extent containment only. It does not prove that every
district has an acceptable output node, select a node for any district, or
establish district-derived coverage.

## Cached validation and resume

The raw response and request manifest are stored under ignored cache storage:

```text
cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/
  raw/bgd-padded-national/PRECTOTCORR/20010101_20011231.json
  raw/bgd-padded-national/PRECTOTCORR/20010101_20011231.manifest.json
```

This command validates the request fingerprint, byte count, SHA-256 and full
response structure while installing a network-forbidden opener:

```bash
python3 src/acquire/download_nasa_power_regional.py --check-config --plan preflight --validate-preflight-cache
```

It passed without another successful download. A corrupt or incomplete cache
would be quarantined rather than accepted or silently overwritten.

## Revised full-acquisition proposal

The request plan remains:

```text
1 national area × 25 calendar years × 4 one-parameter requests = 100 requests
```

Observed evidence is limited to one PRECTOTCORR year:

- 823,232 bytes;
- 2.865375 seconds;
- 140 coordinates and 51,100 values.

Simple arithmetic extrapolation from that one observation gives approximately
82,323,200 raw bytes (78.51 MiB) and 286.5375 seconds (4.78 minutes) for 100
requests. These are estimates, not measured full-collection storage or
duration. Other parameters, years, metadata, service load, retries and response
compression may differ.

Recommended execution remains sequential, one parameter-year per request, with
the existing 90-second timeout, at most three attempts for transient failures,
bounded exponential backoff, `Retry-After`, permanent-error stop, exact raw
bytes, per-request manifests and checksum-aware resume.

Annual JSON chunks are practical based on this observation; there is no current
reason to change format or chunk size. Reconsider NetCDF only if later observed
JSON sizes or parsing costs become impractical and only after implementing and
testing a provenance-preserving NetCDF parser.

## Remaining separation and blockers

Raw Regional coverage and district-derived coverage remain different products:

- Raw Regional coverage: validated for national-area PRECTOTCORR in 2001.
- District-derived coverage: not produced and still unresolved.

Before any full collection, separately review cross-parameter national
coordinate/date alignment and choose an extraction method. This preflight does
not approve nearest-node extraction. No independent review or scientific
acceptance is claimed, and G0 was not changed.
