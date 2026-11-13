#!/usr/bin/env python3
"""Offline representative-point mapping and explicitly adopted context exports."""
import csv
import json
from collections import Counter
from pathlib import Path
import download_nasa_power_regional as r


def diagnostics(config):
    downloader = r.RegionalDownloader(config)
    spec = r.build_preflight_request(config)
    manifest = downloader._cached(spec)
    if manifest is None:
        raise ValueError('Verified national coordinates required')
    coordinates = manifest['validation']['output_coordinates']
    mapping_path = r.ROOT / 'assets/bamis_region_district_mapping.csv'
    regions = {}
    for row in csv.DictReader(mapping_path.read_text(encoding='utf-8-sig').splitlines()):
        regions.setdefault(row['district'], []).append(row['bamis_region'])
    districts = []
    for row in csv.DictReader(r.DEFAULT_REGISTRY.read_text().splitlines()):
        lat, lon = float(row['latitude']), float(row['longitude'])
        ranked = sorted((r.haversine_km(lat, lon, c[1], c[0]), c[1], c[0]) for c in coordinates)
        distance, output_lat, output_lon = ranked[0]
        districts.append(dict(district_id=row['district_id'], district_name=row['district_name_en'],
                              anchor_latitude=lat, anchor_longitude=lon,
                              diagnostic_output_latitude=output_lat, diagnostic_output_longitude=output_lon,
                              distance_km=distance, second_nearest_distance_km=ranked[1][0],
                              exact_distance_ties=sum(i[0] == distance for i in ranked),
                              bamis_regions=regions.get(row['district_name_en'], []),
                              status='user_adopted_representative_point_context'))
    counts = Counter((d['diagnostic_output_longitude'], d['diagnostic_output_latitude']) for d in districts)
    return dict(registry_sha256=config['registry']['sha256'],
                regional_raw_sha256=manifest['response']['sha256'],
                bamis_mapping_sha256=r.sha256(mapping_path.read_bytes()), districts=districts,
                mapped_districts=sum(bool(d['bamis_regions']) for d in districts),
                distance_km_min=min(d['distance_km'] for d in districts),
                distance_km_max=max(d['distance_km'] for d in districts),
                selected_output_locations=len(counts),
                shared_output_locations=sum(v > 1 for v in counts.values()),
                maximum_districts_sharing_output=max(counts.values()),
                tie_break='great-circle distance, returned latitude, returned longitude',
                earth_radius_km=6371.0088, native_cell_ids_assigned=False,
                adoption=dict(by='Saim', basis='Explicit user selection: Adopt representative-point context', date='2026-11-13', independent_scientific_review=False),
                district_weather_produced=False)


def export_context(result, prepared):
    import gzip
    import prepare_nasa_power_regional as preparation
    target = prepared / 'district-context'
    target.mkdir(parents=True, exist_ok=True)
    outputs = []
    inventory = json.loads((prepared / 'inventory.json').read_text())
    for artifact in inventory['wide_artifacts']:
        source = r.ROOT / artifact['path']
        if r.sha256(source.read_bytes()) != artifact['sha256']:
            raise ValueError(f'Wide artifact checksum mismatch: {source}')
        nodes = {}
        with gzip.open(source, 'rt') as file:
            for line in file:
                row = json.loads(line)
                key = (row['output_longitude'], row['output_latitude'])
                nodes.setdefault(key, []).append(row)
        for district in result['districts']:
            key = (district['diagnostic_output_longitude'], district['diagnostic_output_latitude'])
            if key not in nodes:
                raise ValueError(f"Adopted output location absent: {district['district_id']} {source.name}")
            rows = [dict(row, district_id=district['district_id'],
                         spatial_interpretation='representative_point_context',
                         anchor_longitude=district['anchor_longitude'], anchor_latitude=district['anchor_latitude'],
                         distance_km=district['distance_km']) for row in nodes[key]]
            path = target / f"{district['district_id']}-{source.name}"
            preparation.write_jsonl_gzip(path, rows)
            outputs.append(dict(path=r.recorded_path(path), sha256=r.sha256(path.read_bytes()),
                                rows=len(rows), regional_source=r.recorded_path(source),
                                regional_source_sha256=r.sha256(source.read_bytes())))
    receipt = dict(mapping=result, outputs=outputs, district_weather_produced=bool(outputs),
                   limitations='Regional representative-point context; neither district-area average nor field measurement; no Point API equivalence or agronomic validation.')
    r.atomic_write(target / 'manifest.json', r.canonical_json(receipt))
    return len(outputs)


if __name__ == '__main__':
    target = r.ROOT / 'data/climate/regional_district_extraction_diagnostics.json'
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-context', action='store_true')
    parser.add_argument('--prepared', type=Path, default=r.ROOT / 'cache/nasa_power_regional/prepared-v1')
    args = parser.parse_args()
    result = diagnostics(r.load_config())
    r.atomic_write(target, (json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k != 'districts'}, indent=2))

    if args.export_context:
        print(f'Exported {export_context(result, args.prepared)} district-year context partitions')
