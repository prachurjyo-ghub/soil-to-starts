"""Synthetic-only tests for the NASA POWER Daily Regional acquisition client."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/acquire"))
import download_nasa_power_regional as regional  # noqa: E402


def synthetic_response(request_spec, config, *, coordinates=None, fill_first=False, time_standard="LST"):
    coordinates = coordinates or [[90.0, 23.5], [90.625, 23.5], [90.0, 24.0], [90.625, 24.0]]
    dates = regional.expected_dates(request_spec["start"], request_spec["end"])
    features = []
    for feature_index, coordinate in enumerate(coordinates):
        series = {}
        for name in request_spec["parameter_names"]:
            series[name] = {
                day: (-999 if fill_first and feature_index == 0 and date_index == 0 else float(feature_index + date_index))
                for date_index, day in enumerate(dates)
            }
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": coordinate},
                "properties": {"parameter": series},
            }
        )
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": features,
            "header": {
                "title": "SYNTHETIC POWER regional-shaped test response; not observations",
                "api": {"name": "POWER Daily API", "version": "synthetic-test"},
                "fill_value": -999,
                "time_standard": time_standard,
                "start": request_spec["start"],
                "end": request_spec["end"],
                "sources": ["SYNTHETIC_TEST_ONLY"],
            },
            "parameters": {
                name: {"units": regional.PARAMETERS[name]["units"], "longname": regional.PARAMETERS[name]["name"]}
                for name in request_spec["parameter_names"]
            },
            "messages": [],
            "times": {"data": 0.0},
        },
        separators=(",", ":"),
    ).encode()


class FakeResponse:
    def __init__(self, raw, status=200):
        self.raw = raw
        self.offset = 0
        self.status = status
        self.headers = {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        if size < 0:
            size = len(self.raw) - self.offset
        chunk = self.raw[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk


class RegionalAcquireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = regional.build_config()
        cls.requests = regional.build_smoke_requests(cls.config)
        cls.request = cls.requests[0]

    def downloader(self, temporary, opener, config=None):
        return regional.RegionalDownloader(
            config or self.config,
            cache_root=Path(temporary) / "regional-cache",
            opener=opener,
            sleeper=lambda _: None,
            random_source=lambda: 0.0,
            now=lambda: "2026-11-13T00:00:00Z",
        )

    def test_config_is_boundary_derived_and_full_plan_is_one_hundred_requests(self):
        self.assertEqual(self.config["registry"]["sha256"], regional.sha256(regional.DEFAULT_REGISTRY.read_bytes()))
        self.assertEqual(len(self.requests), 4)
        self.assertTrue(all(len(item["parameter_names"]) == 1 for item in self.requests))
        self.assertEqual(self.config["full_proposal"]["configured_request_count"], 100)
        smoke = self.config["smoke_test"]["bbox"]
        self.assertEqual(smoke["latitude_max"] - smoke["latitude_min"], 2.0)
        self.assertEqual(smoke["longitude_max"] - smoke["longitude_min"], 2.0)
        extent = self.config["boundary"]["geometry_extent"]
        bbox = self.config["boundary"]["national_request_bbox"]
        self.assertLess(bbox["longitude_min"], extent["longitude_min"])
        self.assertGreater(bbox["longitude_max"], extent["longitude_max"])
        self.assertFalse(self.config["identity_and_extraction"].get("native_grid_identity_claimed", False))

    def test_parser_validates_coordinates_dates_units_lst_and_missing_values(self):
        result = regional.validate_response_bytes(
            synthetic_response(self.request, self.config, fill_first=True), self.request, self.config
        )
        self.assertEqual(result["feature_count"], 4)
        self.assertEqual(result["date_count"], 3)
        self.assertEqual(result["value_count"], 12)
        self.assertEqual(result["fill_counts"]["PRECTOTCORR"], 1)
        self.assertEqual(result["units"]["PRECTOTCORR"], "mm/day")
        self.assertEqual(result["time_standard"], "LST")
        self.assertEqual(result["output_coordinate_extent"]["longitude_max"], 90.625)

    def test_parser_rejects_wrong_time_parameter_dates_and_spatial_coverage(self):
        with self.assertRaises(regional.ResponseValidationError):
            regional.validate_response_bytes(
                synthetic_response(self.request, self.config, time_standard="UTC"), self.request, self.config
            )
        wrong_parameter = json.loads(synthetic_response(self.request, self.config))
        wrong_parameter["parameters"] = {"T2M": {"units": "C"}}
        with self.assertRaises(regional.ResponseValidationError):
            regional.validate_response_bytes(json.dumps(wrong_parameter).encode(), self.request, self.config)
        wrong_dates = json.loads(synthetic_response(self.request, self.config))
        values = wrong_dates["features"][0]["properties"]["parameter"]["PRECTOTCORR"]
        values.pop(next(iter(values)))
        with self.assertRaises(regional.ResponseValidationError):
            regional.validate_response_bytes(json.dumps(wrong_dates).encode(), self.request, self.config)
        with self.assertRaises(regional.ResponseValidationError):
            regional.validate_response_bytes(
                synthetic_response(self.request, self.config, coordinates=[[89.4, 23.5]]), self.request, self.config
            )

    def test_checksum_resume_skips_valid_cache_and_quarantines_corruption(self):
        calls = []
        raw = synthetic_response(self.request, self.config)

        def opener(url, timeout):
            calls.append((url, timeout))
            return FakeResponse(raw)

        with tempfile.TemporaryDirectory() as temporary:
            downloader = self.downloader(temporary, opener)
            first = downloader.download(self.request)
            second = downloader.download(self.request)
            self.assertEqual(first["acquisition_status"], "downloaded_verified")
            self.assertEqual(second["resume_status"], "cached_verified")
            self.assertEqual(len(calls), 1)
            raw_path, _ = downloader.paths(self.request)
            raw_path.write_bytes(raw_path.read_bytes() + b"corrupt")
            downloader.download(self.request)
            self.assertEqual(len(calls), 2)
            self.assertTrue(list((downloader.cache_root / "errors").rglob("*.corrupt.*")))

    def test_cross_parameter_alignment_requires_exact_returned_coordinate_sets(self):
        manifests = []
        for request_spec in self.requests:
            validation = regional.validate_response_bytes(synthetic_response(request_spec, self.config), request_spec, self.config)
            manifests.append({"validation": validation})
        aligned = regional.smoke_alignment(self.config, manifests)
        self.assertTrue(aligned["coordinate_sets_identical"])
        self.assertTrue(aligned["date_sets_identical"])
        self.assertFalse(aligned["native_grid_identity_claimed"])
        self.assertTrue(aligned["district_mapping_diagnostics"])
        changed = copy.deepcopy(manifests)
        changed[-1]["validation"]["coordinate_set_sha256"] = "0" * 64
        rejected = regional.smoke_alignment(self.config, changed)
        self.assertFalse(rejected["coordinate_sets_identical"])
        self.assertEqual(rejected["combination_status"], "not_safe_to_combine")


if __name__ == "__main__":
    unittest.main()
