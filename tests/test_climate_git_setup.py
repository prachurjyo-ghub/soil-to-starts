"""Repository climate installer guard regressions using small synthetic inputs."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('climate_git_setup',ROOT/'scripts/setup_climate_data.py')
setup=importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class ClimateGitSetupTests(unittest.TestCase):
    def test_modified_helper_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'src/acquire').mkdir(parents=True)
            source=root/'src/acquire/package_climate_data.py'
            source.write_text("raise AssertionError('must not run')")
            with self.assertRaisesRegex(ValueError,'differs from trusted'):
                setup.verified_helper(root,{'bootstrap_sha256':'0'*64})

    def test_no_helper_file_is_not_a_nasa_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'matching Git version'):
                setup.verified_helper(Path(tmp),{'bootstrap_sha256':'0'*64})

    def test_sha256_stream_matches_known_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'synthetic'
            path.write_bytes(b'abc')
            self.assertEqual(setup.sha256(path),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

if __name__=='__main__':unittest.main()
