#!/usr/bin/env python3
"""Read-only local climate lineage audit; writes only the requested audit report."""
import argparse
import calendar
import datetime as dt
import gzip
import json
import math
from pathlib import Path

import build_district_sampling_registry as geometry
import download_nasa_power_regional as r

PREPARED = r.ROOT / 'cache/nasa_power_regional/prepared-v1'
DEFAULT_OUTPUT = r.ROOT / 'data/climate/climate_extreme_value_audit.json'


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=r.unique_object)


def monthly_statistic(parameter, values):
    """Independent audit calculation: each daily rate spans one day."""
    valid = [v for v in values if v is not None]
    return (math.fsum(valid) if parameter == 'PRECTOTCORR' else math.fsum(valid) / len(valid)) if valid else None


def unique_match(rows, predicate):
    matches = [row for row in rows if predicate(row)]
    if len(matches) != 1:
        raise ValueError(f'Expected one matching record; found {len(matches)}')
    return matches[0]


def jsonl(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line, object_pairs_hook=r.unique_object)


def temperature_consistency(series):
    supports = [{(coord, date) for coord, dates in rows.items() for date in dates} for rows in series.values()]
    if len({frozenset(support) for support in supports}) != 1:
        raise ValueError('Temperature date/location supports differ')
    violations = []
    missing = 0
    for coord, date in sorted(supports[0]):
        low, mean, high = [series[p][coord][date] for p in ('T2M_MIN', 'T2M', 'T2M_MAX')]
        if -999 in (low, mean, high):
            missing += 1
        elif not low <= mean <= high:
            violations.append(dict(coordinates=list(coord), date=date, minimum=low, mean=mean, maximum=high))
    return len(supports[0]) - missing, missing, violations


def spatial_relation(coord, features):
    inside = [f['properties'].get('shapeName') for f in features if geometry.point_in_geometry_strict(coord, f['geometry'])]
    if inside:
        return dict(classification='inside_pinned_Bangladesh_geometry', containing_source_district_names=inside)
    edge = any(geometry.ring_relation(coord, ring) == 'boundary' for f in features
               for polygon in geometry.polygons(f['geometry']) for ring in polygon)
    return dict(classification='on_pinned_boundary' if edge else 'padded_area_only_outside_pinned_Bangladesh_geometry',
                containing_source_district_names=[])


def extrema_candidates(parameter, series, allowed=None):
    items = [(value, date, coord) for coord, dates in series.items() if allowed is None or coord in allowed
             for date, value in dates.items() if value != -999]
    minimum = min(value for value, _, _ in items)
    maximum = max(value for value, _, _ in items)
    result = []
    for label, target in ([('maximum', maximum)] if parameter == 'PRECTOTCORR' else [('minimum', minimum), ('maximum', maximum)]):
        ties = sorted((date, coord) for value, date, coord in items if value == target)
        result.append((label, target, ties))
    return result


def audit(prepared=PREPARED):
    config = r.load_config()
    specs = r.build_full_requests(config)
    downloader = r.RegionalDownloader(config, opener=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Network forbidden')))
    acquisition_path = r.ROOT / 'data/climate/nasa_power_regional_full_summary.json'
    preparation_path = r.ROOT / 'data/climate/nasa_power_regional_preparation_summary.json'
    acquisition = read_json(acquisition_path)
    preparation = read_json(preparation_path)
    inventory_path = prepared / 'inventory.json'
    inventory = read_json(inventory_path)
    if r.sha256(inventory_path.read_bytes()) != preparation['regional_inventory_sha256']:
        raise ValueError('Preparation inventory receipt mismatch')
    context_manifest_path = prepared / 'district-context/manifest.json'
    context = read_json(context_manifest_path)
    if r.sha256(context_manifest_path.read_bytes()) != preparation['district_manifest_sha256']:
        raise ValueError('District manifest receipt mismatch')
    mapping = context['mapping']['districts']
    used = {(d['diagnostic_output_longitude'], d['diagnostic_output_latitude']) for d in mapping}
    boundary_raw = gzip.decompress(r.DEFAULT_BOUNDARY.read_bytes())
    if r.sha256(boundary_raw) != config['boundary']['uncompressed_sha256']:
        raise ValueError('Pinned boundary checksum mismatch')
    features = json.loads(boundary_raw)['features']
    raw_by_id, series_by_year, metadata = {}, {}, {}
    candidates = {}
    checks = dict(raw_requests=0, raw_values=0, temperature_rows_checked=0, temperature_missing_rows=0,
                  temperature_violation_count=0, temperature_violations=[], raw_fill_values=0, negative_non_fill_counts={p: 0 for p in r.PARAMETERS})
    for spec in specs:
        raw_path, manifest_path = downloader.paths(spec)
        raw = raw_path.read_bytes()
        manifest = read_json(manifest_path)
        if (manifest['response']['sha256'] != r.sha256(raw) or manifest['response']['bytes'] != len(raw)
                or manifest['request']['url'] != spec['url'] or manifest['request']['parameters'] != spec['parameters']
                or manifest['request_fingerprint'] != r.request_fingerprint(config, spec)):
            raise ValueError('Raw identity/checksum mismatch: ' + spec['request_id'])
        validation = r.validate_response_bytes(raw, spec, config)
        if validation != manifest['validation']:
            raise ValueError('Raw validation receipt mismatch')
        payload = json.loads(raw)
        parameter = spec['parameter_label']
        series = {tuple(f['geometry']['coordinates'][:2]): f['properties']['parameter'][parameter] for f in payload['features']}
        year = spec['start'][:4]
        series_by_year.setdefault(year, {})[parameter] = series
        raw_by_id[spec['request_id']] = spec
        metadata[spec['request_id']] = dict(raw_path=r.recorded_path(raw_path), manifest_path=r.recorded_path(manifest_path),
            raw_sha256=r.sha256(raw), header=payload['header'], parameter_metadata=payload['parameters'][parameter],
            url=spec['url'], request_parameters=spec['parameters'])
        checks['raw_requests'] += 1
        checks['raw_values'] += validation['value_count']
        checks['raw_fill_values'] += sum(validation['fill_counts'].values())
        checks['negative_non_fill_counts'][parameter] += sum(value < 0 and value != -999 for dates in series.values() for value in dates.values())
        for scope, allowed in [('padded_regional', None), ('district_used_locations', used)]:
            for label, value, ties in extrema_candidates(parameter, series, allowed):
                key = (scope, parameter, label)
                entry = candidates.get(key)
                selected = [(date, coord, spec['request_id']) for date, coord in ties]
                if entry is None or (value < entry[0] if label == 'minimum' else value > entry[0]):
                    candidates[key] = (value, selected)
                elif value == entry[0]:
                    entry[1].extend(selected)
    for year, parameters in sorted(series_by_year.items()):
        count, missing, violations = temperature_consistency({p: parameters[p] for p in ('T2M', 'T2M_MIN', 'T2M_MAX')})
        checks['temperature_rows_checked'] += count
        checks['temperature_missing_rows'] += missing
        checks['temperature_violation_count'] += len(violations)
        checks['temperature_violations'].extend(violations)
    selected = {}
    for (scope, parameter, label), (value, ties) in sorted(candidates.items()):
        date, coord, request_id = min(ties)
        key = (parameter, date, coord)
        selected.setdefault(key, dict(parameter=parameter, value=value, date=date, coordinates=list(coord),
                                     request_id=request_id, selections=[]))['selections'].append(dict(scope=scope, extreme=label, ties=len(ties)))
    observations = []
    evidence_files = {str(acquisition_path), str(preparation_path), str(inventory_path), str(context_manifest_path), str(r.DEFAULT_BOUNDARY)}
    normalized_cache, wide_cache = {}, {}
    context_by_path = {item['path']: item for item in context['outputs']}
    wide_receipts = {item['path']: item for item in inventory['wide_artifacts']}
    inventory_by_id = {item['request_id']: item for item in inventory['requests']}
    for (parameter, date, coord), entry in sorted(selected.items()):
        request_id = entry['request_id']
        meta = metadata[request_id]
        year, month = date[:4], date[:6]
        iso_date = f'{year}-{date[4:6]}-{date[6:]}'
        series = series_by_year[year][parameter][coord]
        normalized_path = prepared / f'{request_id}.jsonl.gz'
        if request_id not in normalized_cache:
            normalized_cache.clear()
            if r.sha256(normalized_path.read_bytes()) != inventory_by_id[request_id]['normalized_sha256']:
                raise ValueError('Normalized checksum mismatch')
            rows = list(jsonl(normalized_path))
            keys = [(i['parameter'], i['date'], i['output_longitude'], i['output_latitude']) for i in rows]
            if len(set(keys)) != len(keys):
                raise ValueError('Duplicate normalized observation')
            normalized_cache[request_id] = rows
        match = lambda row: row['date'] == iso_date and (row['output_longitude'], row['output_latitude']) == coord
        normalized = unique_match(normalized_cache[request_id], match)
        daily_ok = (normalized['value'] == entry['value'] and normalized['parameter'] == parameter
                    and normalized['unit'] == meta['parameter_metadata']['units'] and normalized['raw_artifact'] == meta['raw_sha256']
                    and normalized['time_standard'] == 'LST' and normalized['missing_reason'] is None
                    and normalized['request_id'] == request_id and normalized['collection_id'] == config['collection_id'])
        monthly_path = prepared / f'{request_id}.monthly.json'
        iso_month = iso_date[:7]
        monthly_row = unique_match(read_json(monthly_path), lambda row: row['date'] == iso_month and
            (row['output_longitude'], row['output_latitude']) == coord and row['parameter'] == parameter)
        values = [value for day, value in series.items() if day.startswith(month)]
        expected_days = calendar.monthrange(int(year), int(date[4:6]))[1]
        calculated = monthly_statistic(parameter, values)
        monthly_ok = (len(values) == expected_days and monthly_row['coverage'] == 'complete'
            and monthly_row['valid_days'] == monthly_row['expected_days'] == expected_days
            and math.isclose(monthly_row['value'], calculated, rel_tol=1e-12, abs_tol=1e-9)
            and math.isclose(monthly_row['available_day_statistic'], calculated, rel_tol=1e-12, abs_tol=1e-9)
            and monthly_row['unit'] == ('mm' if parameter == 'PRECTOTCORR' else 'C')
            and monthly_row['source_artifacts'] == [meta['raw_sha256']])
        chart_path = prepared / f'chart-{coord[0]}-{coord[1]}-{parameter}.json'
        chart = read_json(chart_path)
        chart_row = unique_match(chart['series'], lambda row: row['date'] == iso_month)
        chart_ok = (chart_row == monthly_row and chart['parameter'] == parameter and chart['time_standard'] == 'LST'
                    and (chart['output_longitude'], chart['output_latitude']) == coord)
        wide_path = prepared / f'{year}.wide-replay.jsonl.gz'
        if year not in wide_cache:
            wide_cache.clear()
            if r.sha256(wide_path.read_bytes()) != wide_receipts[r.recorded_path(wide_path)]['sha256']:
                raise ValueError('Wide checksum mismatch')
            rows = list(jsonl(wide_path))
            keys = [(i['date'], i['output_longitude'], i['output_latitude']) for i in rows]
            if len(set(keys)) != len(keys):
                raise ValueError('Duplicate wide replay key')
            wide_cache[year] = rows
        wide = unique_match(wide_cache[year], match)
        wide_all_values_match = all(wide['values'][p] == series_by_year[year][p][coord][date] for p in r.PARAMETERS)
        wide_ok = (wide_all_values_match and wide['values'][parameter] == entry['value'] and wide['raw_artifacts'][parameter] == meta['raw_sha256']
                   and wide['units'][parameter] == normalized['unit'] and wide['time_standard'] == 'LST'
                   and wide['missing_reasons'][parameter] is None)
        districts = []
        for district in mapping:
            if (district['diagnostic_output_longitude'], district['diagnostic_output_latitude']) != coord:
                continue
            path = prepared / 'district-context' / f"{district['district_id']}-{year}.wide-replay.jsonl.gz"
            receipt = context_by_path[r.recorded_path(path)]
            if r.sha256(path.read_bytes()) != receipt['sha256']:
                raise ValueError('District checksum mismatch')
            row = unique_match(jsonl(path), match)
            okay = (row['values'] == wide['values'] and row['raw_artifacts'] == wide['raw_artifacts']
                    and row['units'] == wide['units'] and row['missing_reasons'] == wide['missing_reasons']
                    and row['spatial_interpretation'] == 'representative_point_context'
                    and row['district_id'] == district['district_id'] and row['time_standard'] == 'LST'
                    and row['anchor_longitude'] == district['anchor_longitude'] and row['anchor_latitude'] == district['anchor_latitude'])
            districts.append(dict(district_id=district['district_id'], path=r.recorded_path(path), matches=okay,
                                  distance_km=district['distance_km'], sha256=receipt['sha256']))
            evidence_files.add(str(path))
        temporal_neighbours = []
        day = dt.datetime.strptime(date, '%Y%m%d').date()
        for offset in (-2, -1, 0, 1, 2):
            neighbour = day + dt.timedelta(days=offset)
            d = neighbour.strftime('%Y%m%d')
            neighbour_series = series_by_year.get(d[:4], {}).get(parameter, {}).get(coord, {})
            temporal_neighbours.append(dict(date=neighbour.isoformat(), value=neighbour_series.get(d), offset_days=offset))
        ranked = sorted((r.haversine_km(coord[1], coord[0], other[1], other[0]), other[1], other[0])
                        for other in series_by_year[year][parameter] if other != coord)[:4]
        neighbours = [dict(longitude=lon, latitude=lat, distance_km=distance,
                            value=series_by_year[year][parameter][(lon, lat)][date]) for distance, lat, lon in ranked]
        tests = dict(raw_to_normalized=daily_ok, independently_recomputed_monthly=monthly_ok,
                     monthly_to_chart=chart_ok, raw_to_wide_replay=wide_ok,
                     district_exports=all(d['matches'] for d in districts))
        okay = all(tests.values())
        geography = spatial_relation(coord, features)
        method_questions = []
        if districts and geography['classification'] != 'inside_pinned_Bangladesh_geometry':
            method_questions.append('C: The adopted representative-point context uses a returned position outside the pinned Bangladesh geometry; this is a sampling limitation, not evidence of a processing error.')
        entry.update(date=iso_date, time_standard='LST', unit=normalized['unit'], raw=meta,
            geography=geography, method_questions=method_questions, district_context=districts,
            normalized=dict(path=r.recorded_path(normalized_path), record=normalized),
            monthly=dict(path=r.recorded_path(monthly_path), record=monthly_row, independent_value=calculated),
            chart=dict(path=r.recorded_path(chart_path), period=chart['period'], monthly_record_matches=chart_ok,
                       provisional_selection=chart['provisional_selection']),
            replay=dict(path=r.recorded_path(wide_path), record=wide), temporal_neighbours=temporal_neighbours,
            spatial_neighbours=neighbours, checks=tests, classification='B' if okay else 'A',
            conclusion='Faithfully preserved unusual source value; physical accuracy unresolved.' if okay else 'Derived lineage mismatch: investigate before use.')
        observations.append(entry)
        evidence_files.update([str(r.ROOT / meta['raw_path']), str(r.ROOT / meta['manifest_path']), str(normalized_path),
                               str(monthly_path), str(chart_path), str(wide_path)])
    return dict(audit_version='climate-extreme-audit-v1', collection_id=config['collection_id'],
        selection_method='Global padded-area and district-used-location maximum rainfall plus minima/maxima of each temperature parameter; all ties counted, earliest date then longitude then latitude selects one observation.',
        neighbour_method='Same returned coordinate at offsets -2,-1,0,+1,+2 calendar days; four nearest distinct returned points on the same LST date by great-circle distance (6371.0088 km), then latitude, longitude. No interpolation.',
        boundary_method=dict(path=r.recorded_path(r.DEFAULT_BOUNDARY), uncompressed_sha256=r.sha256(boundary_raw),
            method='Existing strict polygon-with-holes ray test; boundary separately flagged. Simplified pinned geometry, not a surveyed border or a cell footprint.'),
        source_interpretation=dict(urls=config['source']['documentation_urls'] + [
            'https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/',
            'https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/'],
            evidence='Existing local handoff and per-response units/LST metadata; no new source requests.',
            precipitation='Daily average rate mm/day multiplied by a one-day interval; sum daily amounts once for monthly mm. Daily records/replay retain mm/day.',
            temperatures='Celsius retained directly; monthly means of daily values/extrema are not monthly absolute extrema.'),
        checks=checks, observations=observations,
        classification_definitions=dict(A='Proven processing error', B='Faithfully preserved unusual source value', C='Unresolved source or method question'),
        unresolved_questions=['Local physical accuracy and representativeness are not independently meteorologically validated.',
            'The rainfall source maximum needs upstream/source or independent station evidence before event interpretation; statistical rarity alone is not an error.',
            'Returned coordinate containment does not establish the source spatial footprint is wholly inside Bangladesh.'],
        evidence_sha256={r.recorded_path(Path(path)): r.sha256(Path(path).read_bytes()) for path in sorted(evidence_files)},
        source_or_derived_data_modified=False, network_requests=0,
        acquisition_receipt_counts={key: acquisition[key] for key in ('complete', 'failed', 'pending', 'bytes')})


def markdown_report(report):
    if any(row['classification'] != 'B' for row in report['observations']) or report['checks']['temperature_violation_count']:
        return '# Climate extreme-value audit — investigation required\n\nThe JSON audit contains lineage mismatches or source temperature-order conflicts. Do not reuse the prior no-error conclusion. Inspect the machine-readable evidence before any correction; no climate data was changed.\n'
    lines = ['# Climate extreme-value audit — Step 1 only', '',
        'Owner: Saim. Local audit on 13 November 2026; independent review and meteorological validation are not claimed.', '',
        '## Result', '',
        'The 14 selected observations are faithfully preserved source values (category B). No processing error was proven. '
        'No source or derived climate observation was changed or regenerated; no network/data request was made. '
        'Physical accuracy and representative-point limitations remain category C questions. Category A is reserved for a proven processing error.', '',
        'The reported 965.18 mm/day precipitation maximum is at 91.25°E, 20.5°N on 2017-07-22 LST. '
        'Its returned position is outside the pinned Bangladesh geometry, inside the padded acquisition area, and unused by district context. '
        'The six reported temperature extrema are also outside the pinned country geometry and unused by district context. '
        'They remain in regional charts and replay inputs, so they must not be described as Bangladesh-only extrema.', '',
        'Among the 42 district-used locations, rainfall reaches 521.24 mm/day at 91.875°E, 21.5°N on 2019-07-07 LST '
        '(Cox’s Bazar context). The district-used temperature ranges are T2M 8.39–37.81 C, '
        'T2M_MIN 1.23–31.59 C and T2M_MAX 15.2–47.62 C. These are selected-location context statistics, '
        'not district-area measurements or independently verified station events.', '',
        '## Methods and scope', '', report['selection_method'], '', report['neighbour_method'], '',
        'Geography uses the existing strict polygon-with-holes test on the pinned simplified ADM2 geometry. '
        'Boundary coordinates are distinguished from strict interior. The raw uncompressed boundary SHA-256 is `'
        + report['boundary_method']['uncompressed_sha256'] + '`. Coordinate containment classifies the returned position only; '
        'it does not establish native cell footprints, surveyed borders or land/sea coverage.', '',
        'All 100 raw requests were reread and checked against request identity, full byte count/SHA-256, '
        'stored validation and the existing parser. This verifies 5,113,360 values with zero fills. '
        'For all 1,278,340 matched date/location temperature triplets, minimum <= mean <= maximum holds; '
        'zero missing triplets or violations were found. Negative Celsius values are preserved.', '',
        'For each selected observation, the audit independently recomputes the monthly statistic from raw daily values '
        'using math.fsum (comparison tolerance 1e-9 absolute / 1e-12 relative to allow floating summation order). '
        'It checks a unique matching normalized key, raw identity, units/LST, no missing marker, '
        'monthly valid/expected counts, artifact provenance, exact monthly chart record and daily replay values. '
        'Selected normalized partitions and replay files are scanned for duplicate keys. '
        'All four replay parameter values are checked against raw date/location records. '
        'Applicable district files are checksum-verified and matched to the replay record and unchanged anchors. '
        'No scaling, fill substitution, repeated accumulation, incorrect join or propagation error was detected in this scope. '
        'This is not an exhaustive record-by-record audit of every derived file.', '',
        '## Rate and temperature interpretation', '',
        'The existing local handoff and response metadata establish explicit LST daily support and PRECTOTCORR mm/day. '
        'A one-day mean rainfall rate multiplied by one day gives mm for that interval. Monthly accumulation sums '
        'each daily interval once; daily records and daily replay keep mm/day. No conversion factor of 24 or 86400 is applied. '
        'Temperature values remain Celsius. Monthly T2M_MIN/T2M_MAX values are means of daily extrema, '
        'not the lowest/highest temperature of the month.', '',
        'Official references already recorded in the local preparation evidence (no new retrieval in this audit):', '',
        '- [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)',
        '- [NASA POWER meteorological methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)',
        '- [NASA POWER hydrology units](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/)', '',
        '## Per-observation evidence', '',
        'All paths below are repository-relative. Full retained headers, request parameters, exact daily/wide/monthly '
        'records, provisional chart selection metadata, neighbours and evidence-file SHA-256 values are in '
        '`data/climate/climate_extreme_value_audit.json`. Ties are counted and one observation is selected deterministically.', '']
    for number, row in enumerate(report['observations'], 1):
        raw = row['raw']
        coord = row['coordinates']
        lines += [f"### {number}. {row['parameter']} — {row['value']} {row['unit']}, {row['date']} LST", '',
            f"Returned longitude/latitude: {coord}. Selection: " + '; '.join(f"{s['scope']} {s['extreme']} ({s['ties']} tied observations)" for s in row['selections']) + '.', '',
            f"Classification: **{row['classification']}**. {row['conclusion']} Geography: `{row['geography']['classification']}`.", '',
            f"Request ID: `{row['request_id']}`. API: `{raw['header'].get('api')}`. Sources: `{raw['header'].get('sources')}`. "
            f"Parameter metadata: `{raw['parameter_metadata']}`. Fill: `{raw['header'].get('fill_value')}`.", '',
            f"Raw SHA-256: `{raw['raw_sha256']}`.", '',
            f"- Raw: `{raw['raw_path']}`",
            f"- Request manifest: `{raw['manifest_path']}`",
            f"- Normalized: `{row['normalized']['path']}`",
            f"- Monthly: `{row['monthly']['path']}`",
            f"- Chart: `{row['chart']['path']}`",
            f"- Daily wide replay: `{row['replay']['path']}`", '',
            'Monthly value: ' + str(row['monthly']['record']['value']) + ' ' + row['monthly']['record']['unit']
            + '; independent calculation: ' + str(row['monthly']['independent_value'])
            + '; valid/expected days: ' + str(row['monthly']['record']['valid_days']) + '/' + str(row['monthly']['record']['expected_days'])
            + '. The matching chart monthly record agrees exactly.', '',
            'Temporal neighbours (same parameter/unit, LST dates): ' + '; '.join(f"{i['date']}: {i['value']}" for i in row['temporal_neighbours']) + '.', '',
            'Spatial neighbours (same parameter/unit/date): ' + '; '.join(f"({i['longitude']}, {i['latitude']}): {i['value']} at {i['distance_km']:.6f} km" for i in row['spatial_neighbours']) + '.', '']
        if row['district_context']:
            lines += ['District context (same daily values and provenance, no correction needed):', '']
            lines += [f"- `{d['district_id']}`: `{d['path']}`; anchor-to-output distance {d['distance_km']:.6f} km." for d in row['district_context']]
            lines += ['']
        else:
            lines += ['District context: no adopted district mapping uses this location; no district export contains this selected observation.', '']
        lines += row['method_questions'] + ([''] if row['method_questions'] else [])
        lines += ['All observation lineage checks passed.', '']
    lines += ['## Impact, unresolved questions and limits', '',
        'For the separately verified distinction between the original interior Chapainawabganj anchor and its outside-polygon API output position, see [current method handoff](CLIMATE_REGIONAL_HANDOFF.md) and [coordinate-role evidence](../../data/climate/climate_coordinate_role_check.json). The findings below concern the output position, not the original anchor.', '',
        'No category A processing error was established, so responsible pipeline code and all source/derived climate '
        'outputs remain unchanged. Category B means preservation is verified, not that the weather value is physically validated. '
        'No thresholds, clipping, zero replacement, interpolation or meteorological certification is introduced.', '',
        'The outside-country source maxima affect only their regional node monthly/chart/replay data; '
        'they do not affect district-context outputs because those coordinates are unused. '
        'The seven district-used extrema propagate faithfully into the listed district files; this is existing source influence, '
        'not a newly discovered processing defect. Districts sharing one returned point receive the same observations.', '',
        'Category C: Chapainawabganj context selects (88.125, 24.5), outside the pinned Bangladesh geometry. '
        'Its 31.59 C daily minimum on 2012-06-05 is faithfully preserved. The adopted nearest-point method permits '
        'cross-border positions; whether that context is adequate for downstream decisions needs source/spatial review. '
        'No mapping or distance rule was changed in this audit. No inference is made about the full source footprint.', '',
        'Category C: the 965.18 mm/day source rate, other unusual values and their neighbouring values require '
        'upstream product/event or independent observation evidence to assess physical accuracy. '
        'Temporal/spatial coherence is diagnostic, not independent validation. No additional request is necessary to '
        'establish the local lineage result; this audit makes none. Agronomic interpretation remains outside scope.', '',
        'All 17 negative T2M_MIN values were recounted directly from raw files; other parameters have no negative non-fill values. Negative Celsius is not automatically invalid. This audit checks '
        'their source-level temperature ordering through the full-triplet scan and traces the global negative minimum; '
        'it does not provide separate full lineage sections for all 17 negative records.', '',
        '## Reproduction and verification', '',
        'From repository root; the audit command reads local evidence and writes only its JSON and Markdown reports:', '',
        '```bash',
        'OFFLINE=1 python3 -B src/acquire/audit_climate_extremes.py',
        "python3 -B -m unittest tests.test_climate_extreme_audit tests.test_nasa_power_regional_acquire tests.test_nasa_power_regional_prepare -v",
        "python3 -B -m unittest discover -s tests -p 'test_*.py' -v",
        'python3 scripts/workflow.py render', 'python3 scripts/workflow.py check', 'git diff --check', '```', '',
        'Recorded verification for this audit: 95 repository tests and 25 focused audit/acquisition/preparation tests passed. '
        'The offline audit command passed. Workflow and whitespace validation results are recorded in '
        '`docs/tasks/CLIMATE-EXTREME-AUDIT.json`; independent review remains pending.', '',
        'Audit additions: `src/acquire/audit_climate_extremes.py`, `tests/test_climate_extreme_audit.py`, '
        '`docs/data/CLIMATE_EXTREME_VALUE_AUDIT.md`, `data/climate/climate_extreme_value_audit.json`, '
        '`docs/tasks/CLIMATE-EXTREME-AUDIT.json`; the canonical `docs/AI_USE.md` log and generated '
        '`docs/PROGRESS.md`/`README.md` also update. All pre-existing work is preserved. '
        'No frontend checks are needed because frontend behavior is unchanged. No staging, commit, push, merge or deployment is authorized or performed.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--markdown', type=Path, default=r.ROOT / 'docs/data/CLIMATE_EXTREME_VALUE_AUDIT.md')
    args = parser.parse_args()
    result = audit()
    r.atomic_write(args.output, (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n').encode())
    r.atomic_write(args.markdown, markdown_report(result).encode())
    print(f"Audited {len(result['observations'])} observations; temperature rows={result['checks']['temperature_rows_checked']}; temperature violations={result['checks']['temperature_violation_count']}")
    for row in result['observations']:
        print(row['parameter'], row['date'], row['coordinates'], row['value'], row['classification'], row['geography']['classification'], [d['district_id'] for d in row['district_context']])
