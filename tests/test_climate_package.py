"""Meaningful archive safety/integrity/offline tests using tiny synthetic data."""
import hashlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/acquire'))
import package_climate_data as package


class ClimatePackageTests(unittest.TestCase):
    def archive(self, root, extra=None, payload=b'synthetic', expected=b'synthetic'):
        entry = dict(path='data/test.json', bytes=len(expected), sha256=hashlib.sha256(expected).hexdigest())
        manifest = dict(schema_version=package.SCHEMA, package_id=package.PACKAGE, files=[entry],
                        file_count=1, payload_bytes=len(expected))
        path = root / 'test.tar.gz'
        with tarfile.open(path, 'w:gz') as tar:
            for name, raw in [(package.MANIFEST, json.dumps(manifest).encode()), ('data/test.json', payload)]:
                member = tarfile.TarInfo(package.PACKAGE + '/' + name)
                member.size = len(raw)
                tar.addfile(member, io.BytesIO(raw))
            if extra is not None:
                tar.addfile(extra, io.BytesIO(b''))
        return path

    def test_safe_extract_and_every_payload_checksum(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.archive(root)
            extracted = package.extract(archive, root / 'fresh', package.digest(archive))
            self.assertEqual((extracted / 'data/test.json').read_bytes(), b'synthetic')
            self.assertEqual(package.verify_files(extracted, package.load_manifest(extracted)['files']), 1)

    def test_wrong_archive_hash_and_existing_destination_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.archive(root)
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                package.extract(archive, root / 'fresh', '0' * 64)
            self.assertFalse((root / 'fresh').exists())
            (root / 'existing').mkdir()
            (root / 'existing/keep').write_bytes(b'keep')
            with self.assertRaisesRegex(ValueError, 'must not exist'):
                package.extract(archive, root / 'existing', package.digest(archive))
            self.assertEqual((root / 'existing/keep').read_bytes(), b'keep')

    def test_traversal_absolute_symlink_duplicate_and_unlisted_members_rejected(self):
        for name, kind in [('../escape', tarfile.REGTYPE), ('/absolute', tarfile.REGTYPE),
            (package.PACKAGE + '/link', tarfile.SYMTYPE),
            (package.PACKAGE + '/data/test.json', tarfile.REGTYPE),
            (package.PACKAGE + '/unlisted', tarfile.REGTYPE)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                extra = tarfile.TarInfo(name)
                extra.type = kind
                extra.linkname = '/tmp/should-never-be-followed'
                archive = self.archive(root, extra)
                with self.assertRaises(ValueError):
                    package.extract(archive, root / 'fresh', package.digest(archive))
                self.assertFalse((root / 'fresh').exists())

    def test_corrupt_payload_fails_manifest_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.archive(root, payload=b'corrupted', expected=b'synthetic')
            with self.assertRaisesRegex(ValueError, 'integrity failure'):
                package.extract(archive, root / 'fresh', package.digest(archive))

    def test_manifest_totals_and_unsafe_paths_are_rejected(self):
        for name in ('a/../b', 'a//b', 'a\\b', 'C:/b', '/b'):
            with self.assertRaises(ValueError):
                package.relative_path(name)
        manifest = dict(schema_version=package.SCHEMA, package_id=package.PACKAGE,
            files=[dict(path='safe', bytes=10, sha256='0' * 64)], file_count=1, payload_bytes=0)
        with self.assertRaisesRegex(ValueError, 'byte total'):
            package.validate_manifest(manifest)

    def test_network_is_rejected_before_connection_or_dns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'network.py').write_text("import socket\nsocket.getaddrinfo('127.0.0.1',443)\n")
            with self.assertRaisesRegex(RuntimeError, 'forbids network'):
                package.run_local(root, 'network.py')

if __name__ == '__main__':
    unittest.main()
