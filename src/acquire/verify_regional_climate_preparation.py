#!/usr/bin/env python3
"""Snapshot or compare deterministic local artifacts and verify preparation receipts."""
import argparse
import json
from pathlib import Path
import download_nasa_power_regional as r


def hashes(root):
    return {str(p.relative_to(root)): r.sha256(p.read_bytes()) for p in sorted(root.glob('*')) if p.is_file()}


def verify(root, snapshot):
    current = hashes(root)
    previous = json.loads(snapshot.read_text())
    if previous != current:
        raise ValueError('Offline preparation changed artifact paths or SHA-256 values')
    inventory = json.loads((root / 'inventory.json').read_text())
    context_path = root / 'district-context/manifest.json'
    context = json.loads(context_path.read_text())
    for artifact in context['outputs'] + inventory['wide_artifacts']:
        if r.sha256((r.ROOT / artifact['path']).read_bytes()) != artifact['sha256']:
            raise ValueError(f"Artifact checksum mismatch: {artifact['path']}")
    monthly = [json.loads(p.read_text()) for p in sorted(root.glob('*.monthly.json'))]
    return dict(processing_version=inventory['processing_version'], normalized_partitions=len(inventory['requests']),
        observations=sum(x['observations'] for x in inventory['requests']), missing=sum(x['missing'] for x in inventory['requests']),
        monthly_partitions=len(monthly), monthly_rows=sum(map(len, monthly)),
        complete_monthly_rows=sum(row['coverage'] == 'complete' for partition in monthly for row in partition),
        wide_partitions=len(inventory['wide_artifacts']), wide_rows=sum(x['rows'] for x in inventory['wide_artifacts']),
        charts=len(list(root.glob('chart-*.json'))), district_year_partitions=len(context['outputs']),
        district_date_rows=sum(x['rows'] for x in context['outputs']),
        reproducibility=dict(status='passed', network='forbidden by normalization opener', runs=2,
            identical_files=len(current), artifact_set_sha256=r.sha256(r.canonical_json(current))),
        regional_inventory_sha256=r.sha256((root / 'inventory.json').read_bytes()),
        district_manifest_sha256=r.sha256(context_path.read_bytes()), output_root=r.recorded_path(root),
        replay_selection='configurable provisional descriptive extrema; no agronomic trigger or engine replay',
        independent_review=False, frontend_integrated=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=r.ROOT / 'cache/nasa_power_regional/prepared-v1')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--snapshot', type=Path)
    group.add_argument('--compare', type=Path)
    parser.add_argument('--summary', type=Path, default=r.ROOT / 'data/climate/nasa_power_regional_preparation_summary.json')
    args = parser.parse_args()
    if args.snapshot:
        r.atomic_write(args.snapshot, r.canonical_json(hashes(args.root)))
        print('Saved local preparation SHA-256 snapshot')
    else:
        result = verify(args.root, args.compare)
        r.atomic_write(args.summary, (json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
        print(f"PASS identical regional files={result['reproducibility']['identical_files']}; district and wide checksums verified")
