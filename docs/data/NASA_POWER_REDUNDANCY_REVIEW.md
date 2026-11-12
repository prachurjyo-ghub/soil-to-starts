# NASA POWER request-reuse review

## Decision

Step 3 stopped before the full historical acquisition. No defensible
pre-request equivalence key was found for mapping the 64 district sampling
points onto shared POWER responses for all four requested parameters. The
full-download command is therefore guarded and makes no network request while
the checked-in decision has status
`blocked_no_authoritative_equivalence_key`.

This is not a finding that every district needs a distinct POWER request. It
means the available evidence is insufficient to prove which district points
are equivalent without guessing. No sampling point was moved, rounded for
grouping, or assigned an invented NASA grid-cell ID.

## Official evidence reviewed

The following official NASA POWER sources were accessed on 13 November 2026:

- [Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
  warns that the 0.5° × 0.5° global catalog needs one request per cell and that
  repeated requests for the same relative location may be blocked. It does not
  define the grid origin, edge convention, point-snapping algorithm or a
  returned cell identifier.
- [POWER methodology](https://power.larc.nasa.gov/docs/methodology/) states
  that meteorological products have the resolution of their input data and
  documents ½° latitude × ⅝° longitude for the meteorological source. This is
  not the same grid description as the Daily API warning.
- [Meteorological sources](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)
  identifies MERRA-2/GEOS as the meteorological source family and describes
  gridded precipitation and two-metre temperature. A common source family and
  nominal resolution do not by themselves define the POWER point endpoint's
  cell lookup.
- [Daily OpenAPI v2.10.3](https://power.larc.nasa.gov/api/temporal/daily/openapi.json)
  defines `Geometry.coordinates` only as a generic array. It documents no
  cell ID, grid index, snapping method or equivalence field.

The four preserved smoke responses all report POWER Daily API v2.10.3 and
sources `MERRA2` and `POWER`. Their response geometry contains a three-number
coordinate array: submitted longitude and latitude rounded to three decimals,
plus elevation. Because neither the schema nor API documentation identifies
this array as a cell centre or equivalence key, it is retained only as response
metadata. Equal observed values, coordinate proximity and local rounding were
not used as deduplication evidence.

The machine-readable decision is
`data/climate/nasa_power_request_reuse_v1.json`. It is bound to the unchanged
collection configuration SHA-256
`0cc5fdbcbca4b3965b81de4d90a8f53eea35a06ec2627921dca1adbb59b63d8e`
and registry SHA-256
`0b31748796de714f73de135ee3e0ec77c2e44813985d790b44f2d62e18c62dfa`.

## Dry-run plan and current acquisition state

Generate and verify the Step 3 artifacts without network access:

```bash
python3 src/acquire/download_nasa_power.py --check-config --scope full --write-reuse-decision --write-full-plan
```

`data/climate/nasa_power_full_acquisition_plan.json` contains:

- all 64 original registry points and 25 annual logical request identities per
  district;
- requested dates 2001-01-01 through 2025-12-31, parameters
  `PRECTOTCORR`, `T2M`, `T2M_MIN`, `T2M_MAX`, and explicit `LST`;
- 1,600 logical district-year chunks, zero safely reused responses, and an
  unresolved authoritative unique-network-request count;
- 9,131 expected dates per district, 584,384 expected district-day records and
  2,337,536 parameter values before any returned fill values;
- the ignored raw/error storage layout, sequential network policy, retry,
  timeout and checksum-aware resume behavior;
- a district-to-logical-request provenance mapping. Every shared-response
  mapping remains `null` rather than guessed.

`data/climate/nasa_power_full_acquisition_summary.json` records the honest
pre-acquisition state: zero full requests complete, zero failed, 1,600 pending,
zero districts with full verified coverage and missingness not assessed. It
references the four pre-existing smoke responses separately; those one-month
responses are not annual full-collection chunks and are not counted as full
coverage.

The exact attempted full command was:

```bash
python3 src/acquire/download_nasa_power.py --config data/climate/nasa_power_daily_v1.json --scope full --execute --confirm-full-collection
```

It exited at the reuse gate before opening a network request. The same command
is the resume command after the decision artifact is replaced by an
independently reviewed, checksum-bound, parameter-complete authoritative
mapping. Re-running it while the current blocker remains will continue to stop
safely.

## Storage and preservation

No full-history raw response was created. The ignored cache still contains only
the four Step 2 smoke response byte streams and their four request manifests.
Their checksums remain verified. The existing downloader continues to validate
request identity, HTTP/API shape, exact dates, parameter names, units, LST,
fill convention and raw SHA-256 before accepting cached work. Partial, failed
or corrupt evidence is retained under the configured error layout rather than
silently overwritten.

## Resolution required

Before full acquisition, obtain official POWER evidence for a point-to-cell
mapping or response-equivalence key that explicitly covers all four requested
parameters. The evidence must resolve the differing grid descriptions, define
edge/snap behavior, and support a reproducible district-to-request mapping.
Independent review of that mapping is still required. This documentation does
not advance G0, claim agronomic approval or claim teammate acceptance.
