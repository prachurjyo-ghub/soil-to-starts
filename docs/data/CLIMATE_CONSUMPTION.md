# Local climate consumption contract — Fardin / Maruf

This documents the existing v1.0.0 files; it does not implement or approve a
backend, crop engine or frontend integration. Use the verified extracted package
root as a configurable data root. Its `cache/nasa_power_regional/prepared-v1/`
directory is called `P` below. No request-serving path should call NASA: validate
and index local prepared files during deliberate setup, then read those files
while serving requests. NASA belongs only to a separately intentional acquisition
or refresh operation. Preserve `OFFLINE=1` and the tested socket-blocked verifier.
The climate package does not make the website offline: application dependencies,
backend deployment, browser assets/fonts/maps and their rights need separate work.

## Files and selection

- Regional daily values: `P/YYYY.wide-replay.jsonl.gz`. Each gzip JSONL line is
  one exact returned longitude/latitude and LST date, containing all four parameters.
  Select by the recorded `(output_longitude, output_latitude, date)` key, not a
  fabricated grid-cell ID. The padded area includes positions outside Bangladesh.
- District context: `P/district-context/bd-district-NAME-YYYY.wide-replay.jsonl.gz`.
  Choose a stable `district_id` from the original registry/mapping; the export
  already applies the adopted representative-point method. Do not remap a node
  per request or replace it with a field pin. Check file/row identity and select date.
- Optional long view: `P/bgd-padded-national__PARAMETER__YYYY0101_YYYY1231.jsonl.gz`.
  One parameter/date/output-position observation per line. The optional view is
  not a second independent observation source.
- Monthly aggregates: the corresponding parameter-year `.monthly.json` file.
  Its top level is a list. Select `parameter`, `date` (`YYYY-MM`) and exact output
  longitude/latitude. PRECTOTCORR is mm; temperatures are C.
- Chart arrays: `P/chart-LONGITUDE-LATITUDE-PARAMETER.json`. The envelope carries
  parameter/location, period, time_standard, source_urls and processing_version;
  `series` contains monthly records. `provisional_selection` contains descriptive
  configurable period extrema, not an agreed stress label or crop-engine replay.
- Provenance/index: `P/inventory.json` and `P/district-context/manifest.json`.
  Verify them and their referenced artifacts at setup; keep source versions and
  artifact hashes in any future backend result/receipt. The package manifest
  verifies files before loading. No runtime upstream fallback is authorized.

Daily wide records contain `date` (`YYYY-MM-DD`), `output_longitude`,
`output_latitude`, `values`, `units`, `missing_reasons`, `raw_artifacts`,
`time_standard` and `processing_version`. Parameter dictionaries are keyed by
`PRECTOTCORR`, `T2M`, `T2M_MIN`, `T2M_MAX`. District rows additionally contain
`district_id`, `anchor_longitude`, `anchor_latitude`, `distance_km` and
`spatial_interpretation: representative_point_context`. Both coordinate roles
must remain visible; an original interior anchor is not the returned position.

Long rows contain `collection_id`, `request_id`, `parameter`, `date`,
`output_longitude`, `output_latitude`, `value`, `unit`, `time_standard`,
`missing_reason` and `raw_artifact`. Resolve daily `raw_artifacts` hashes or
monthly `source_artifacts` through `inventory.requests[*].raw_artifact` to the
raw path, byte count, SHA-256, request manifest and parameter-specific metadata.
Do not substitute a generic source name for exact artifact provenance.

Monthly records contain `value`, `available_day_statistic`, `statistic`, `unit`,
`valid_days`, `expected_days`, `coverage`, `source_artifacts`, location, parameter,
month and processing version. Keep nulls and coverage. No missingness threshold
is implied. T2M_MIN/T2M_MAX monthly values are means of daily extrema, not absolute
monthly extrema; daily rainfall rate integrated once per one-day interval gives
monthly mm. LST is local solar time, not Bangladesh civil time or UTC. Matching
calendar strings alone does not establish equivalence to a civil-time station record.

## Real example and minimal loader

`CLIMATE_DELIVERY_EXAMPLE.json` is loaded from the freshly extracted delivery
by this task. The matching regional and Chapainawabganj rows on 2001-01-01 LST
use output position (88.125, 24.5). Values are PRECTOTCORR 0.04 mm/day, T2M
17.48 C, T2M_MIN 12.05 C and T2M_MAX 24.65 C. The original Chapainawabganj anchor
is (88.256694, 24.688357), 24.8185734952679 km away. Only the output position is
outside the pinned Bangladesh polygons. It is nearby regional context, not a
district-contained measurement. The example retains raw artifact hashes and
matching monthly/chart records, not an invented sample.

From an extracted package root (use an actual path for `CLIMATE_ROOT`):

```bash
export CLIMATE_ROOT=/tmp/soil-climate-fardin/extracted/soil-to-stars-climate-bgd-v1.0.0
python3 - <<'PY'
import gzip, json, os
from pathlib import Path
p = Path(os.environ['CLIMATE_ROOT']) / 'cache/nasa_power_regional/prepared-v1'
def exact_row(path, date, lon, lat):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        matches = [json.loads(line) for line in stream]
    matches = [r for r in matches if r['date'] == date and
               (r['output_longitude'], r['output_latitude']) == (lon, lat)]
    if len(matches) != 1:
        raise ValueError('Missing or duplicate local date/location key')
    return matches[0]
regional = exact_row(p/'2001.wide-replay.jsonl.gz', '2001-01-01', 88.125, 24.5)
district = exact_row(p/'district-context/bd-district-chapainawabganj-2001.wide-replay.jsonl.gz',
                     '2001-01-01', 88.125, 24.5)
assert district['district_id'] == 'bd-district-chapainawabganj'
assert district['values'] == regional['values']
print(json.dumps({'regional': regional, 'district_context': district}, indent=2))
PY
```

This is a teaching loader for one annual partition. A future backend can index
verified local keys once, rather than scanning a gzip file for every request.
Missing coverage or invalid evidence should be explicit, not replaced by mock
values or a live NASA request. That backend behavior is Fardin's integration work,
not completed by this documentation.

## Scientific and agronomy boundaries

The 64 anchors use 42 returned positions; 17 positions are shared and up to four
districts share one. Eleven mappings use positions outside pinned country polygons.
An outside-polygon result is not proof of a surveyed international-border crossing.
These are historical representative-location model/reanalysis context, not field
measurements, district averages or forecasts. No region has automatic priority.

The extreme audit confirmed faithful preservation for its 14 selected lineages;
no processing error was proved there. The 965.18 mm/day padded-area maximum and
six padded-area temperature extrema are outside the pinned country polygons and
unused by district exports. They must not be described as Bangladesh-only extrema.
The district-used rainfall maximum is 521.24 mm/day at Cox's Bazar context.
Temperature ordering holds for 1,278,340 matched raw triplets; 17 negative minimum
Celsius values were retained. Neither those checks nor byte-identical reproduction
establish physical weather accuracy. Do not clip, interpolate or replace unusual
values without evidence and a separately documented versioned change.

The compatibility dictionary documents each variable's statistic/units/support,
not crop rules. Maruf/Fardin must match crop stage, actual dates, period, units and
applicable location before comparing source-backed evidence. BAMIS climate normals
are not crop tolerance thresholds; humidity, wind and sunshine remain unsupported
by this core package. Unresolved calendar conventions, rainfall triggers, irrigation
semantics and scientific applicability require decisions, not invented limits,
weights, soil facts, probabilities or automatic rankings.
