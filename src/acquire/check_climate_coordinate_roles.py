#!/usr/bin/env python3
"""Check existing anchor/output roles offline; never changes mapping or climate data."""
import argparse
import csv
import json
import math
from pathlib import Path

import build_district_sampling_registry as geometry
import download_nasa_power_regional as r

TARGET = 'bd-district-chapainawabganj'
OUTPUT = r.ROOT / 'data/climate/climate_coordinate_role_check.json'


def containing_ids(coordinate, features):
    return sorted(key for key, shape in features.items() if geometry.point_in_geometry_strict(coordinate, shape))


def check_role(row, diagnostic, features, output_coordinates):
    anchor = (float(row['longitude']), float(row['latitude']))
    output = (diagnostic['diagnostic_output_longitude'], diagnostic['diagnostic_output_latitude'])
    if (diagnostic['anchor_longitude'], diagnostic['anchor_latitude']) != anchor:
        raise ValueError('Diagnostic anchor differs from original registry')
    anchors_inside = containing_ids(anchor, features)
    if anchors_inside != [row['district_id']]:
        raise ValueError('Original anchor is not uniquely inside its assigned pinned district')
    ranked = sorted((r.haversine_km(anchor[1], anchor[0], c[1], c[0]), c[1], c[0]) for c in output_coordinates)
    if (ranked[0][2], ranked[0][1]) != output:
        raise ValueError('Existing selected node differs from deterministic nearest-output ranking')
    if not math.isclose(ranked[0][0], diagnostic['distance_km'], abs_tol=1e-10, rel_tol=1e-12):
        raise ValueError('Recorded sampling distance mismatch')
    if diagnostic['exact_distance_ties'] != sum(item[0] == ranked[0][0] for item in ranked):
        raise ValueError('Recorded exact tie count mismatch')
    output_inside = containing_ids(output, features)
    output_on_boundary = not output_inside and any(geometry.ring_relation(output, ring) == 'boundary'
        for shape in features.values() for polygon in geometry.polygons(shape) for ring in polygon)
    return dict(district_id=row['district_id'], anchor_longitude=anchor[0], anchor_latitude=anchor[1],
                anchor_containing_district_ids=anchors_inside, output_longitude=output[0], output_latitude=output[1],
                output_containing_district_ids=output_inside, output_on_pinned_boundary=output_on_boundary, distance_km=ranked[0][0],
                second_nearest_distance_km=ranked[1][0], exact_distance_ties=diagnostic['exact_distance_ties'])


def check():
    config = r.load_config()
    features, metadata, retrieval, _ = geometry.load_boundary_features()
    registry_raw = r.DEFAULT_REGISTRY.read_bytes()
    if r.sha256(registry_raw) != config['registry']['sha256']:
        raise ValueError('Original registry checksum mismatch')
    diagnostic_path = r.ROOT / 'data/climate/regional_district_extraction_diagnostics.json'
    diagnostic = json.loads(diagnostic_path.read_bytes())
    if diagnostic['registry_sha256'] != r.sha256(registry_raw):
        raise ValueError('Diagnostic registry checksum mismatch')
    spec = r.build_preflight_request(config)
    raw_path, manifest_path = r.RegionalDownloader(config).paths(spec)
    raw = raw_path.read_bytes()
    manifest = json.loads(manifest_path.read_bytes())
    if r.sha256(raw) != diagnostic['regional_raw_sha256'] or r.sha256(raw) != manifest['response']['sha256']:
        raise ValueError('Pinned raw output-coordinate checksum mismatch')
    if manifest['request_fingerprint'] != r.request_fingerprint(config, spec) or manifest['request']['url'] != spec['url']:
        raise ValueError('Pinned raw request identity mismatch')
    validation = r.validate_response_bytes(raw, spec, config)
    coordinates = validation['output_coordinates']
    registry = {row['district_id']: row for row in csv.DictReader(registry_raw.decode().splitlines())}
    mappings = {row['district_id']: row for row in diagnostic['districts']}
    if set(registry) != set(mappings) or len(registry) != 64:
        raise ValueError('Registry/diagnostic district IDs do not match')
    context_path = r.ROOT / 'cache/nasa_power_regional/prepared-v1/district-context/manifest.json'
    context = json.loads(context_path.read_bytes())
    if context['mapping']['districts'] != diagnostic['districts']:
        raise ValueError('Export manifest mapping differs from diagnostic mapping')
    results = [check_role(registry[key], mappings[key], features, coordinates) for key in sorted(registry)]
    target = next(row for row in results if row['district_id'] == TARGET)
    return dict(check_version='climate-coordinate-roles-v1', status='passed', target=target,
        registry_anchors_checked=len(results), anchors_uniquely_inside_assigned_district=len(results),
        selected_outputs_checked=len(results),
        districts_using_outside_country_output=[row['district_id'] for row in results if not row['output_containing_district_ids'] and not row['output_on_pinned_boundary']],
        selected_outputs_on_pinned_boundary=sum(row['output_on_pinned_boundary'] for row in results),
        selected_output_inside_country_count=sum(bool(row['output_containing_district_ids']) for row in results),
        method='Existing strict polygon-with-holes containment against all 64 original pinned ADM2 features; longitude/latitude order. Existing great-circle nearest ranking; tie order distance, latitude, longitude; radius 6371.0088 km.',
        boundary=dict(path=r.recorded_path(r.DEFAULT_BOUNDARY), uncompressed_sha256=config['boundary']['uncompressed_sha256'],
                      source_id=metadata['boundaryID'], version=config['boundary']['source_version'],
                      limitation='Pinned simplified administrative geometry; not a surveyed border or native source-cell footprint.'),
        evidence_sha256={r.recorded_path(path): r.sha256(path.read_bytes()) for path in
            (r.DEFAULT_REGISTRY, diagnostic_path, raw_path, manifest_path, context_path,
             r.ROOT / 'data/admin/bgd-adm2-mapping.json', r.ROOT / 'data/climate/district_sampling_manifest.json')},
        observations_changed=False, mapping_changed=False, network_requests=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = check()
    r.atomic_write(args.output, (json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
    print(json.dumps(result, indent=2))
