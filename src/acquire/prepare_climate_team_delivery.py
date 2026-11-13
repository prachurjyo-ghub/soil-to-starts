#!/usr/bin/env python3
"""Assemble existing sealed artifacts; never downloads or rebuilds climate data."""
import argparse
import gzip
import json
import shutil
import subprocess
from pathlib import Path

import package_climate_data as package

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FOLDER = ROOT / 'cache/climate_delivery/Saim_to_Fardin_climate_v1.0.0'
RECEIPT = ROOT / 'data/climate/climate_team_delivery_receipt.json'


def load_json(path):
    return json.loads(path.read_bytes())


def verified_component(path, expected, expected_bytes=None):
    if not path.is_file() or path.is_symlink() or package.digest(path) != expected:
        raise ValueError('Missing or mismatched delivery component: ' + str(path))
    if expected_bytes is not None and path.stat().st_size != expected_bytes:
        raise ValueError('Wrong delivery byte count: ' + str(path))


def selected_example(prepared):
    date, lon, lat = '2001-01-01', 88.125, 24.5
    paths = dict(regional=prepared / '2001.wide-replay.jsonl.gz',
        district_context=prepared / 'district-context/bd-district-chapainawabganj-2001.wide-replay.jsonl.gz')
    example = dict(status='real_local_file_records', date=date, output_longitude=lon, output_latitude=lat)
    for role, path in paths.items():
        with gzip.open(path, 'rt', encoding='utf-8') as file:
            rows = [json.loads(line) for line in file]
        rows = [row for row in rows if row['date'] == date and
                (row['output_longitude'], row['output_latitude']) == (lon, lat)]
        if len(rows) != 1:
            raise ValueError('Missing/duplicate real example record')
        example[role] = dict(path=str(path.relative_to(prepared.parent.parent.parent)), record=rows[0], sha256=package.digest(path))
    if example['regional']['record']['values'] != example['district_context']['record']['values']:
        raise ValueError('Example regional/district values differ')
    monthly_path = prepared / 'bgd-padded-national__PRECTOTCORR__20010101_20011231.monthly.json'
    months = [row for row in load_json(monthly_path) if row['date']=='2001-01' and
              (row['output_longitude'], row['output_latitude'])==(lon,lat)]
    if len(months) != 1:
        raise ValueError('Example monthly record missing or duplicated')
    chart_path = prepared / 'chart-88.125-24.5-PRECTOTCORR.json'
    chart = load_json(chart_path)
    if [row for row in chart['series'] if row['date']=='2001-01'] != months:
        raise ValueError('Example chart/monthly mismatch')
    example['monthly_precipitation'] = dict(path=str(monthly_path.relative_to(prepared.parent.parent.parent)), record=months[0])
    example['chart'] = dict(path=str(chart_path.relative_to(prepared.parent.parent.parent)), period=chart['period'], time_standard=chart['time_standard'], matching_month='2001-01')
    return example


def write_inventory(folder):
    entries = [dict(path=p.name, bytes=p.stat().st_size, sha256=package.digest(p))
               for p in sorted(folder.iterdir()) if p.is_file() and p.name != 'DELIVERY_INVENTORY.json']
    inventory = dict(schema_version='climate-local-delivery-1.0.0', package_id=package.PACKAGE,
        files=entries, file_count=len(entries), payload_bytes=sum(e['bytes'] for e in entries),
        self_hash='Excluded; compare archive/bootstrap/manifest against trusted producer receipt, not this unsigned inventory alone.',
        recipient_received=False, independent_recipient_validation=False, uploaded=False)
    (folder / 'DELIVERY_INVENTORY.json').write_bytes(package.encoded(inventory))
    return inventory


def assemble(root, folder):
    producer_path = root / 'data/climate/climate_data_package_v1_receipt.json'
    producer = load_json(producer_path)
    archive = root / producer['archive_path']
    bootstrap = root / producer['bootstrap_path']
    manifest_path = root / producer['manifest_path']
    verified_component(archive, producer['archive_sha256'], producer['archive_bytes'])
    verified_component(bootstrap, producer['bootstrap_sha256'])
    verified_component(manifest_path, producer['manifest_sha256'])
    sidecar = Path(str(archive) + '.sha256')
    if not sidecar.is_file() or sidecar.read_text().split() != [producer['archive_sha256'], archive.name]:
        raise ValueError('Missing/mismatched archive checksum sidecar')
    manifest = package.validate_manifest(load_json(manifest_path))
    local_entries = [e for e in manifest['files'] if e['role'] != 'documentation_or_terms']
    package.verify_files(root, local_entries)
    # Original documentation snapshot predates measured-result addenda; not an input mismatch.
    for name, expected in producer['source_revision']['source_file_sha256'].items():
        verified_component(root / name, expected)
    if folder.exists():
        raise ValueError('Delivery folder already exists; refuse silent replacement')
    folder.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(folder.parent).free < archive.stat().st_size + 1024**3:
        raise ValueError('Insufficient headroom for delivery copy and isolated tests')
    sources = {
        archive.name: archive, sidecar.name: sidecar,
        'package_climate_data.py': bootstrap, 'PACKAGE_MANIFEST.json': manifest_path,
        'climate_data_package_v1_receipt.json': producer_path,
        'START_HERE.md': root / 'docs/data/CLIMATE_DELIVERY_START_HERE.md',
        'CLIMATE_CONSUMPTION.md': root / 'docs/data/CLIMATE_CONSUMPTION.md',
        'CLIMATE_PARAMETER_COMPATIBILITY.json': root / 'docs/data/CLIMATE_PARAMETER_COMPATIBILITY.json',
        'CLIMATE_DATA_PACKAGE_GUIDE.md': root / 'docs/data/CLIMATE_DATA_PACKAGE_GUIDE.md',
        'CLIMATE_DATA_PACKAGE_TERMS.md': root / 'docs/data/CLIMATE_DATA_PACKAGE_TERMS.md'}
    if any(not path.is_file() or path.is_symlink() for path in sources.values()):
        raise ValueError('Required guide/source missing or linked')
    folder.mkdir()
    for name, source in sources.items():
        shutil.copy2(source, folder / name)
        if package.digest(source) != package.digest(folder / name):
            raise ValueError('Delivery copy changed bytes: ' + name)
    example = selected_example(root / package.PREPARED)
    (folder / 'CLIMATE_DELIVERY_EXAMPLE.json').write_bytes(package.encoded(example))
    inventory = write_inventory(folder)
    result = dict(schema_version='climate-team-delivery-receipt-1.0.0',
        delivery_folder=str(folder.relative_to(root)), package_id=package.PACKAGE,
        archive_name=archive.name, archive_bytes=producer['archive_bytes'], archive_sha256=producer['archive_sha256'],
        manifest_sha256=producer['manifest_sha256'], bootstrap_sha256=producer['bootstrap_sha256'],
        current_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        package_build_baseline=producer['source_revision'],
        local_non_document_payload_files_verified=len(local_entries),
        local_raw_responses=100, local_prepared_files=2387,
        original_producer_receipt_unchanged=True, sealed_package_unchanged=True,
        recipient_received=False, independent_recipient_validation=False, uploaded=False,
        delivery_file_count=inventory['file_count']+1, delivery_inventory_sha256=package.digest(folder / 'DELIVERY_INVENTORY.json'),
        fresh_validation=dict(status='not_run'), fresh_reproduction=dict(status='not_run'),
        public_sharing='Not cleared; preserve existing NASA notification request and unresolved BAMIS mapping rights.',
        small_git_files=['src/acquire/prepare_climate_team_delivery.py','docs/data/CLIMATE_DELIVERY_START_HERE.md',
            'docs/data/CLIMATE_CONSUMPTION.md','docs/data/CLIMATE_PARAMETER_COMPATIBILITY.json',
            'data/climate/climate_team_delivery_receipt.json','docs/data/CLIMATE_TEAM_HANDOFF_REPORT.md'])
    (root / 'data/climate/climate_team_delivery_receipt.json').write_bytes(package.encoded(result))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=DEFAULT_FOLDER)
    args=parser.parse_args()
    assemble(ROOT,args.folder.resolve())
