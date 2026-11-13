#!/usr/bin/env python3
"""Verify/install the Git-hosted sealed climate package without NASA access."""
import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = 'soil-to-stars-climate-bgd-v1.0.0'
DEFAULT_INSTALL = ROOT / 'cache/climate_repository/v1.0.0'


def sha256(path):
    result=hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda:file.read(1024*1024),b''):
            result.update(block)
    return result.hexdigest()


def verified_helper(root, receipt):
    source=root/'src/acquire/package_climate_data.py'
    if not source.is_file() or sha256(source)!=receipt['bootstrap_sha256']:
        raise ValueError('Package helper differs from trusted producer receipt; restore the matching Git version')
    spec=importlib.util.spec_from_file_location('sealed_climate_package_helper',source)
    helper=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def install(root, destination, verify_only=False):
    receipt=json.loads((root/'data/climate/climate_data_package_v1_receipt.json').read_text())
    helper=verified_helper(root,receipt)
    packaged=root/'data/climate/packages/v1.0.0'
    archive=packaged/receipt['archive_path'].split('/')[-1]
    manifest_path=packaged/'PACKAGE_MANIFEST.json'
    for path,expected in ((archive,receipt['archive_sha256']),(manifest_path,receipt['manifest_sha256'])):
        if not path.is_file() or sha256(path)!=expected:
            raise ValueError('Missing/corrupt Git package file: '+str(path)+'. Fetch/restore main2; do not fall back to NASA.')
    if archive.stat().st_size!=receipt['archive_bytes']:
        raise ValueError('Archive byte count differs from producer receipt')
    if (packaged/(archive.name+'.sha256')).read_text().split()!=[receipt['archive_sha256'],archive.name]:
        raise ValueError('Git checksum sidecar differs from producer receipt')
    manifest=helper.validate_manifest(json.loads(manifest_path.read_bytes()))
    if manifest['package_id']!=PACKAGE_ID:
        raise ValueError('Unexpected package version')
    extracted=destination/'extracted'
    data_root=extracted/PACKAGE_ID
    if verify_only and not data_root.is_dir():
        raise ValueError('Climate data is not installed; run setup without --verify-only first')
    destination.mkdir(parents=True,exist_ok=True)
    lock=destination/'.setup-lock'
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ValueError('A climate setup lock exists; inspect the active setup before retrying') from error
    try:
        if not extracted.exists():
            helper.extract(archive,extracted,receipt['archive_sha256'])
        elif not data_root.is_dir():
            raise ValueError('Extraction destination already exists but is incomplete; inspect it or choose a fresh --install-dir. Nothing was overwritten.')
        # Never overwrite modified installed payload or silently refresh it.
        helper.verify_files(data_root,manifest['files'])
        if sha256(data_root/'PACKAGE_MANIFEST.json')!=receipt['manifest_sha256']:
            raise ValueError('Installed package manifest checksum mismatch')
        validation=helper.validate(data_root)
        report=dict(schema_version='climate-repository-install-1.0.0',package_id=PACKAGE_ID,
            archive_sha256=receipt['archive_sha256'],verified_payload_files=manifest['file_count'],
            climate_data_root=str(data_root),prepared_root=str(data_root/helper.PREPARED),
            validation=validation,network='No NASA requests; validator uses OFFLINE=1 plus socket audit hook',
            application_integration=False,scientific_approval=False)
        temporary=destination/'.installed.json.tmp'
        temporary.write_bytes(helper.encoded(report))
        os.replace(temporary,destination/'installed.json')
    finally:
        lock.rmdir()
    print('\nClimate package is installed and verified.')
    print('CLIMATE_DATA_ROOT='+shlex.quote(str(data_root)))
    print('CLIMATE_PREPARED_ROOT='+shlex.quote(report['prepared_root']))
    print('The frontend/backend is not automatically integrated by this setup.')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install-dir',type=Path,default=DEFAULT_INSTALL)
    parser.add_argument('--verify-only',action='store_true')
    args=parser.parse_args()
    try:
        install(ROOT,args.install_dir.resolve(),args.verify_only)
    except (ValueError,OSError) as error:
        raise SystemExit('Climate setup stopped: '+str(error))
