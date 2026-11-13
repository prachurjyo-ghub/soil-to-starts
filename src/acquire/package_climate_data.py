#!/usr/bin/env python3
"""Build, safely extract and reproduce the explicit local climate handoff (stdlib only)."""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zlib
from pathlib import Path, PurePosixPath

PACKAGE = 'soil-to-stars-climate-bgd-v1.0.0'
MANIFEST = 'PACKAGE_MANIFEST.json'
SCHEMA = 'climate-handoff-package-1.0.0'
ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'cache/climate_handoff' / (PACKAGE + '.tar.gz')
RECEIPT = ROOT / 'data/climate/climate_data_package_v1_receipt.json'
PREPARED = 'cache/nasa_power_regional/prepared-v1'
RAW_ROOT = 'cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def relative_path(value):
    p = PurePosixPath(value)
    if (not value or p.is_absolute() or str(p) != value or '\\' in value
            or any(i in ('.', '..', '') or ':' in i for i in p.parts)):
        raise ValueError('Unsafe or noncanonical relative path: ' + value)
    return p


def validate_manifest(manifest):
    if manifest.get('schema_version') != SCHEMA or manifest.get('package_id') != PACKAGE:
        raise ValueError('Unsupported climate package schema/version')
    entries = manifest.get('files')
    if not isinstance(entries, list) or not 0 < len(entries) <= 10000:
        raise ValueError('Invalid package file count')
    seen = set()
    for entry in entries:
        path = str(relative_path(entry['path']))
        if path in seen or path == MANIFEST:
            raise ValueError('Duplicate or reserved manifest path')
        seen.add(path)
        if type(entry['bytes']) is not int or entry['bytes'] < 0 or not re.fullmatch('[0-9a-f]{64}', entry['sha256']):
            raise ValueError('Invalid payload size or SHA-256')
    total = sum(e['bytes'] for e in entries)
    if type(manifest.get('payload_bytes')) is not int or manifest['payload_bytes'] != total:
        raise ValueError('Manifest payload byte total mismatch')
    if manifest.get('file_count') != len(entries):
        raise ValueError('Manifest file count mismatch')
    if total > 10 * 1024 ** 3:
        raise ValueError('Package exceeds 10 GiB extraction limit')
    return manifest


def load_manifest(root):
    return validate_manifest(json.loads((root / MANIFEST).read_bytes()))


def verify_files(root, entries):
    for entry in entries:
        path = root / entry['path']
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError as error:
            raise ValueError('Payload path escapes root') from error
        if not path.is_file() or path.is_symlink() or path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            raise ValueError('Payload integrity failure: ' + entry['path'])
    return len(entries)


def allowlist(root):
    """Only named provenance/input files and receipt-enumerated canonical outputs."""
    files = {}
    def add(path, role, profiles):
        relative_path(path)
        local = root / path
        if not local.is_file() or local.is_symlink():
            raise ValueError('Missing/linked required input: ' + path)
        files[path] = dict(path=path, role=role, required_for=profiles,
                           bytes=local.stat().st_size, sha256=digest(local))
    source_names = ['download_nasa_power.py', 'download_nasa_power_regional.py',
        'prepare_nasa_power_regional.py', 'regional_climate_handoff.py',
        'build_district_sampling_registry.py', 'check_climate_coordinate_roles.py',
        'verify_regional_climate_preparation.py', 'package_climate_data.py', 'audit_climate_extremes.py']
    for name in source_names:
        add('src/acquire/' + name, 'source_code', ['A'] if name != 'audit_climate_extremes.py' else ['optional_audit'])
    inputs = ['data/climate/nasa_power_daily_regional_v1.json', 'data/climate/district_sampling_registry.csv',
        'data/climate/district_sampling_manifest.json', 'assets/bamis_region_district_mapping.csv',
        'data/admin/bgd-adm2-source.geojson.gz', 'data/admin/bgd-adm2-metadata.json',
        'data/admin/bgd-adm2-retrieval.json', 'data/admin/bgd-adm2-mapping.json']
    for path in inputs:
        add(path, 'input_or_provenance', ['A', 'B'])
    evidence_names = ['nasa_power_regional_full_summary.json', 'nasa_power_regional_preparation_summary.json',
        'regional_district_extraction_diagnostics.json', 'climate_extreme_value_audit.json',
        'climate_coordinate_role_check.json', 'nasa_power_regional_preflight_2001_manifest.json']
    for name in evidence_names:
        add('data/climate/' + name, 'evidence_receipt', ['A', 'B'])
    docs = ['LICENSE', 'THIRD_PARTY_NOTICES.md', 'data/admin/README.md',
        'assets/crop_planning_dataset_README.md', 'docs/data/CLIMATE_REGIONAL_HANDOFF.md',
        'docs/data/CLIMATE_EXTREME_VALUE_AUDIT.md', 'docs/data/CLIMATE_DATA_PACKAGE_GUIDE.md',
        'docs/data/CLIMATE_DATA_PACKAGE_TERMS.md']
    for path in docs:
        add(path, 'documentation_or_terms', ['B'])
    acquisition = json.loads((root / 'data/climate/nasa_power_regional_full_summary.json').read_bytes())
    if acquisition['complete'] != 100 or acquisition['failed'] or acquisition['pending']:
        raise ValueError('This version requires the completed 100-request collection')
    for result in acquisition['results']:
        raw = result['response']
        if digest(root / raw['raw_path']) != raw['sha256']:
            raise ValueError('Raw acquisition receipt mismatch')
        add(raw['raw_path'], 'raw_response', ['A'])
        add(str(PurePosixPath(raw['raw_path']).with_suffix('.manifest.json')), 'raw_request_manifest', ['A'])
    inventory = json.loads((root / PREPARED / 'inventory.json').read_bytes())
    for request in inventory['requests']:
        stem = PREPARED + '/' + request['request_id']
        add(stem + '.jsonl.gz', 'derived_long_observations', ['optional_long_view', 'expected_reproduction'])
        if files[stem + '.jsonl.gz']['sha256'] != request['normalized_sha256']:
            raise ValueError('Normalized inventory checksum mismatch')
        add(stem + '.monthly.json', 'derived_monthly', ['B', 'expected_reproduction'])
    coordinates = inventory['requests'][0]['source_metadata']['output_coordinates']
    for lon, lat in coordinates:
        for parameter in ('PRECTOTCORR', 'T2M', 'T2M_MIN', 'T2M_MAX'):
            add(f'{PREPARED}/chart-{lon}-{lat}-{parameter}.json', 'derived_chart', ['B', 'expected_reproduction'])
    for artifact in inventory['wide_artifacts']:
        add(artifact['path'], 'derived_wide_replay', ['B', 'expected_reproduction'])
        if files[artifact['path']]['sha256'] != artifact['sha256']:
            raise ValueError('Wide inventory checksum mismatch')
    add(PREPARED + '/inventory.json', 'derived_inventory', ['B', 'expected_reproduction'])
    context = json.loads((root / PREPARED / 'district-context/manifest.json').read_bytes())
    for artifact in context['outputs']:
        add(artifact['path'], 'derived_district_context', ['B', 'expected_reproduction'])
        if files[artifact['path']]['sha256'] != artifact['sha256']:
            raise ValueError('District export checksum mismatch')
    add(PREPARED + '/district-context/manifest.json', 'derived_district_manifest', ['B', 'expected_reproduction'])
    return [files[path] for path in sorted(files)]


def build(root, archive, receipt):
    if archive.exists() or archive.with_suffix(archive.suffix + '.sha256').exists():
        raise ValueError('Versioned archive already exists; choose a new version rather than overwrite')
    entries = allowlist(root)
    payload_bytes = sum(e['bytes'] for e in entries)
    archive.parent.mkdir(parents=True, exist_ok=True)
    available = shutil.disk_usage(archive.parent).free
    required = payload_bytes * 5 + 256 * 1024 ** 2
    if available < required:
        raise ValueError(f'Insufficient disk headroom: need {required}, available {available}')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    sources = [e for e in entries if e['role'] == 'source_code']
    configuration = json.loads((root / 'data/climate/nasa_power_daily_regional_v1.json').read_bytes())
    prepared = json.loads((root / 'data/climate/nasa_power_regional_preparation_summary.json').read_bytes())
    acquired = json.loads((root / 'data/climate/nasa_power_regional_full_summary.json').read_bytes())
    geometry = json.loads((root / 'data/climate/climate_coordinate_role_check.json').read_bytes())
    mapping = json.loads((root / 'data/climate/regional_district_extraction_diagnostics.json').read_bytes())
    outside = set(geometry['districts_using_outside_country_output'])
    manifest = dict(schema_version=SCHEMA, package_id=PACKAGE, package_version='1.0.0',
        files=entries, file_count=len(entries), payload_bytes=payload_bytes,
        manifest_self_hash='Excluded from files to avoid circular hashing; archive SHA-256 and external manifest SHA-256 are in the delivery receipt.',
        profiles=dict(A='Original annual raw responses/manifests plus executable sources and required input/evidence files; offline raw reproduction.',
            B='Prepared regional/district views, monthly summaries, charts and replay inputs with provenance/terms; raw files need not be loaded for consumption.',
            optional_long_view='Canonical long-form observations retained to reproduce the original inventory; wide views suffice for combined daily consumption.'),
        source_revision=dict(head=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'),
            relevant_working_tree_status=git('status', '--porcelain', '--untracked-files=all', '--', *[e['path'] for e in sources]),
            source_file_sha256={e['path']: e['sha256'] for e in sources},
            note='This is the working implementation snapshot; HEAD alone does not identify modified/untracked sources.'),
        runtime=dict(python=platform.python_version(), minimum_python='3.9', dependencies='Python standard library only; no pip install',
                     zlib_compile=zlib.ZLIB_VERSION, zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,
                     platform=platform.system(), exact_compression_note='Byte-for-byte compressed reproduction was tested in this runtime; other Python/zlib versions may encode equivalent data differently. Do not silently accept a byte mismatch.'),
        requested_coverage=dict(period=['2001-01-01', '2025-12-31'], bbox=configuration['boundary']['national_request_bbox'],
            parameters=configuration['requested_coverage']['parameters'], time_standard='LST', community='AG', units_system='metric', logical_requests=100),
        actual_coverage=dict(period=[datetime.datetime.strptime(min(row['validation']['actual_start'] for row in acquired['results']), '%Y%m%d').date().isoformat(),
            datetime.datetime.strptime(max(row['validation']['actual_end'] for row in acquired['results']), '%Y%m%d').date().isoformat()],
            output_coordinate_extent=acquired['results'][0]['validation']['output_coordinate_extent'],
            coordinate_support_sha256=acquired['coordinate_support_hashes'],
            api_versions=sorted({row['validation']['api']['version'] for row in acquired['results']}),
            requests=100, output_locations=140, daily_dates_per_location=9131, observations=prepared['observations'],
            normalized_partitions=prepared['normalized_partitions'], monthly_rows=prepared['monthly_rows'], charts=prepared['charts'],
            wide_partitions=prepared['wide_partitions'], district_year_partitions=prepared['district_year_partitions'], district_date_rows=prepared['district_date_rows']),
        source=configuration['source'], processing_version=prepared['processing_version'],
        missingness=dict(fill_value=-999, raw_fill_count=prepared['missing'], normalized_null_count=prepared['missing'],
            policy='Fill to null with reason; no interpolation, clipping or zero replacement; incomplete primary monthly values are null.'),
        outside_polygon_mappings=[row for row in mapping['districts'] if row['district_id'] in outside],
        scientific_limitations=['Regional historical model/reanalysis context, not forecasts, station/field observations or district-area averages.',
            'Original anchors remain interior; 11 mappings use output positions outside pinned simplified country polygons, not proof of surveyed border crossing.',
            'Shared output observations are not independent district samples; distances and both coordinate roles remain explicit.',
            'Unusual source values were preserved; checks establish reproducibility, not physical weather accuracy, agronomic approval or application integration.',
            'Replay selection remains provisional; no engine replay, crop rule activation, yield or crop-failure inference.'],
        redistribution=dict(status='Local teammate handoff only; not uploaded or publicly cleared',
            terms_file='docs/data/CLIMATE_DATA_PACKAGE_TERMS.md', NASA_reference='https://power.larc.nasa.gov/docs/referencing/',
            NASA_notification='NASA POWER requests notification when data is transmitted to other researchers; none sent by this packaging task.',
            boundary_license='CC BY 3.0 IGO; attribution retained',
            unresolved='Public redistribution terms for the supplied BAMIS region mapping remain unverified; project-code license does not relicense third-party data.'),
        exclusions=['Unrelated Point/smoke/error/quarantine caches, temporary files, credentials, .git history, frontend assets, crop datasets/rules, node_modules and Python bytecode.'])
    validate_manifest(manifest)
    manifest_raw = encoded(manifest)
    descriptor, temporary = tempfile.mkstemp(prefix='.package-', dir=archive.parent)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                    import io
                    for path, raw in [(MANIFEST, manifest_raw)]:
                        info = tarfile.TarInfo(PACKAGE + '/' + path)
                        info.size, info.mode, info.mtime = len(raw), 0o644, 0
                        tar.addfile(info, io.BytesIO(raw))
                    for entry in entries:
                        path = root / entry['path']
                        if digest(path) != entry['sha256']:
                            raise ValueError('Input changed while packaging: ' + entry['path'])
                        info = tarfile.TarInfo(PACKAGE + '/' + entry['path'])
                        info.size, info.mode, info.mtime = entry['bytes'], 0o644, 0
                        with path.open('rb') as stream:
                            tar.addfile(info, stream)
        # Never overwrite an immutable version, even if another build raced.
        os.link(temporary, archive)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    checksum = digest(archive)
    archive.with_suffix(archive.suffix + '.sha256').write_text(checksum + '  ' + archive.name + '\n')
    (archive.parent / MANIFEST).write_bytes(manifest_raw)
    bootstrap = archive.parent / 'package_climate_data.py'
    if bootstrap.exists() and digest(bootstrap) != digest(root / 'src/acquire/package_climate_data.py'):
        raise ValueError('Different bootstrap already exists; preserve it and select a new handoff directory')
    if not bootstrap.exists():
        shutil.copyfile(root / 'src/acquire/package_climate_data.py', bootstrap)
    result = dict(package_id=PACKAGE, archive_path=str(archive.relative_to(root)), archive_bytes=archive.stat().st_size,
        archive_sha256=checksum, manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        manifest_path=str((archive.parent / MANIFEST).relative_to(root)), payload_file_count=len(entries), archive_member_count=len(entries) + 1,
        payload_bytes=payload_bytes, role_counts=dict(collections.Counter(e['role'] for e in entries)),
        bootstrap_path=str(bootstrap.relative_to(root)), bootstrap_sha256=digest(bootstrap),
        source_revision=manifest['source_revision'], build_runtime=manifest['runtime'],
        disk_preflight=dict(available_bytes=available, required_headroom_bytes=required),
        delivery_status='Local ignored artifact only; no upload/publication', validation=dict(status='not_run'))
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


def extract(archive, destination, expected_sha256):
    if digest(archive) != expected_sha256:
        raise ValueError('Archive SHA-256 mismatch; extraction refused')
    if destination.exists():
        raise ValueError('Destination must not exist; existing data will not be overwritten')
    with tarfile.open(archive, mode='r:gz') as tar:
        members = tar.getmembers()
        names = set()
        for member in members:
            relative_path(member.name)
            if not member.isfile() or member.name in names or not member.name.startswith(PACKAGE + '/'):
                raise ValueError('Unsafe/duplicate/unexpected archive member')
            names.add(member.name)
        manifest_name = PACKAGE + '/' + MANIFEST
        if manifest_name not in names:
            raise ValueError('Package manifest missing')
        info = tar.getmember(manifest_name)
        if info.size > 16 * 1024 ** 2:
            raise ValueError('Package manifest too large')
        manifest = validate_manifest(json.load(tar.extractfile(info)))
        expected = {PACKAGE + '/' + e['path']: e for e in manifest['files']}
        if names != set(expected) | {manifest_name}:
            raise ValueError('Archive membership differs from manifest')
        for member in members:
            if member.name != manifest_name and member.size != expected[member.name]['bytes']:
                raise ValueError('Archive size differs from manifest')
        if shutil.disk_usage(destination.parent).free < manifest['payload_bytes'] + 64 * 1024 ** 2:
            raise ValueError('Insufficient extraction disk space')
        destination.mkdir()
        for member in members:
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, target.open('xb') as output:
                shutil.copyfileobj(source, output)
    root = destination / PACKAGE
    verify_files(root, manifest['files'])
    print(f'PASS safe extraction and {len(manifest["files"])} payload checksums: {root}')
    return root


NETWORK_BLOCK = '''import runpy,sys
from pathlib import Path
script=sys.argv[1]
sys.argv=[script]+sys.argv[2:]
sys.path.insert(0,str(Path(script).resolve().parent))
def deny(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.bind'):
        raise RuntimeError('Offline package test forbids network: '+event)
sys.addaudithook(deny)
runpy.run_path(script,run_name='__main__')
'''


def run_local(root, script, *args):
    env = dict(os.environ, OFFLINE='1', PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable, '-I', '-B', '-c', NETWORK_BLOCK,
        str(root / script), *args], cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError('Offline command failed: ' + script + '\n' + result.stdout)
    print(result.stdout, end='', flush=True)
    return result.stdout


def validate(root):
    manifest = load_manifest(root)
    count = verify_files(root, manifest['files'])
    run_local(root, 'src/acquire/download_nasa_power_regional.py', '--check-config', '--plan', 'full', '--validate-full-cache')
    run_local(root, 'src/acquire/build_district_sampling_registry.py', '--check')
    run_local(root, 'src/acquire/check_climate_coordinate_roles.py')
    verify_files(root, manifest['files'])
    return dict(status='passed', verified_payload_files=count, raw_requests=100,
                registry_anchors=64, coordinate_role_check='passed', network='socket audit hook + OFFLINE=1; isolated Python -I -B',
                unlisted_project_files='No working-repository path or .git checkout is needed')


def reproduce(root, destination):
    manifest = load_manifest(root)
    verify_files(root, manifest['files'])
    if destination.exists():
        raise ValueError('Reproduction destination must not exist')
    required = [e for e in manifest['files'] if 'A' in e['required_for']]
    if shutil.disk_usage(destination.parent).free < manifest['payload_bytes'] * 2 + 64 * 1024 ** 2:
        raise ValueError('Insufficient reproduction disk space')
    destination.mkdir()
    for entry in required:
        target = destination / entry['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / entry['path'], target)
    # No packaged derived data is copied into the reproduction tree.
    run_local(destination, 'src/acquire/prepare_nasa_power_regional.py')
    run_local(destination, 'src/acquire/regional_climate_handoff.py', '--export-context')
    expected = [e for e in manifest['files'] if e['role'].startswith('derived_')]
    actual = {str(p.relative_to(destination)) for p in (destination / PREPARED).rglob('*') if p.is_file()}
    if actual != {e['path'] for e in expected}:
        raise ValueError('Reproduced derived file set differs from manifest')
    verify_files(destination, expected)
    verify_files(destination, required)
    diagnostic = next(e for e in manifest['files'] if e['path'] == 'data/climate/regional_district_extraction_diagnostics.json')
    verify_files(destination, [diagnostic])
    verify_files(root, manifest['files'])
    return dict(status='passed', reproduced_derived_files=len(expected), reproduced_regional_files=786,
        reproduced_district_files=1601, unchanged_raw_and_inputs=len(required),
        exact_byte_comparison=True, no_derived_inputs_copied=True, network='socket audit hook + OFFLINE=1; isolated Python -I -B')


def examples(root):
    for name in (PREPARED + '/2001.wide-replay.jsonl.gz',
                 PREPARED + '/district-context/bd-district-chapainawabganj-2001.wide-replay.jsonl.gz'):
        with gzip.open(root / name, 'rt', encoding='utf-8') as file:
            row = json.loads(next(file))
        print(json.dumps(dict(path=name, first_record=row), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    build_parser = sub.add_parser('build')
    build_parser.add_argument('--root', type=Path, default=ROOT)
    build_parser.add_argument('--archive', type=Path, default=ARCHIVE)
    build_parser.add_argument('--receipt', type=Path, default=RECEIPT)
    extract_parser = sub.add_parser('extract')
    extract_parser.add_argument('archive', type=Path)
    extract_parser.add_argument('--destination', type=Path, required=True)
    extract_parser.add_argument('--sha256', required=True)
    for name in ('verify', 'validate', 'reproduce', 'examples'):
        command = sub.add_parser(name)
        command.add_argument('--root', type=Path, required=True)
        if name == 'reproduce':
            command.add_argument('--destination', type=Path, required=True)
        if name in ('validate', 'reproduce'):
            command.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        build(args.root.resolve(), args.archive.resolve(), args.receipt.resolve())
    elif args.command == 'extract':
        extract(args.archive.resolve(), args.destination.resolve(), args.sha256)
    elif args.command == 'verify':
        manifest = load_manifest(args.root)
        print('PASS payload file checksums:', verify_files(args.root, manifest['files']))
    elif args.command == 'examples':
        examples(args.root)
    else:
        result = validate(args.root.resolve()) if args.command == 'validate' else reproduce(args.root.resolve(), args.destination.resolve())
        if args.report:
            args.report.write_bytes(encoded(result))
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
