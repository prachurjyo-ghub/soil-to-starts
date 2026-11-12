"""Synthetic-only tests for the NASA POWER acquisition client."""

import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/acquire"))
import download_nasa_power as power  # noqa: E402


def synthetic_response(request_spec, config, *, extra_parameter=False, time_standard="LST"):
    dates = power.expected_dates(request_spec["start"], request_spec["end"])
    series = {
        name: {day: (-999 if index == 0 and name == "PRECTOTCORR" else float(index)) for index, day in enumerate(dates)}
        for name in power.PARAMETERS
    }
    metadata = {name: {"units": details["units"], "longname": details["name"]} for name, details in power.PARAMETERS.items()}
    if extra_parameter:
        series["UNEXPECTED"] = {day: 1.0 for day in dates}
        metadata["UNEXPECTED"] = {"units": "unknown"}
    return json.dumps(
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [90.0, 23.0, 10.0]},
            "properties": {"parameter": series},
            "header": {
                "title": "SYNTHETIC NASA POWER-shaped test response; not observations",
                "api": {"name": "POWER Daily API", "version": "synthetic-test"},
                "fill_value": config["requested_coverage"]["fill_value"],
                "time_standard": time_standard,
                "start": request_spec["start"],
                "end": request_spec["end"],
                "sources": ["SYNTHETIC_TEST_ONLY"],
            },
            "parameters": metadata,
            "messages": [],
        },
        separators=(",", ":"),
    ).encode()


class FakeResponse:
    def __init__(self, raw, *, status=200, headers=None):
        self.raw = raw
        self.offset = 0
        self.status = status
        self.headers = headers or {"Content-Type": "application/json"}

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


class InterruptedResponse(FakeResponse):
    def __init__(self, raw):
        super().__init__(raw)
        self.calls = 0

    def read(self, size=-1):
        self.calls += 1
        if self.calls == 1:
            chunk = self.raw[:40]
            self.offset = 40
            return chunk
        raise OSError("synthetic interrupted stream")


class PowerAcquireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = power.build_config()
        cls.reuse_decision = power.build_reuse_decision()
        cls.smoke_request = power.build_requests(cls.config, "smoke")[0]

    def downloader(self, temporary, opener, config=None, sleeps=None):
        return power.PowerDownloader(
            config or self.config,
            cache_root=Path(temporary) / "cache",
            opener=opener,
            sleeper=(sleeps.append if sleeps is not None else lambda _: None),
            random_source=lambda: 0.0,
            now=lambda: "2026-11-13T00:00:00Z",
        )

    def test_configuration_contains_all_points_and_bounded_request_scopes(self):
        self.assertEqual(self.config["registry"]["sha256"], power.sha256(power.DEFAULT_REGISTRY.read_bytes()))
        self.assertEqual(len(self.config["points"]), 64)
        self.assertEqual(len(power.build_requests(self.config, "smoke")), 4)
        self.assertEqual(len(power.build_requests(self.config, "full")), 1600)
        self.assertEqual(self.config["source"]["time_standard"], "LST")
        self.assertEqual(set(self.config["requested_coverage"]["parameters"]), set(power.PARAMETERS))

    def test_full_plan_preserves_all_district_points_and_stays_blocked(self):
        plan = power.build_full_plan(self.config, self.reuse_decision)
        self.assertEqual(plan["status"], "blocked_before_network_execution")
        self.assertEqual(plan["requested_scope"]["district_count"], 64)
        self.assertEqual(plan["requested_scope"]["logical_request_count"], 1600)
        self.assertEqual(plan["requested_scope"]["expected_days_per_district"], 9131)
        self.assertEqual(plan["requested_scope"]["expected_district_daily_records"], 584384)
        self.assertIsNone(plan["request_reuse"]["authoritative_unique_network_requests"])
        self.assertEqual(plan["request_reuse"]["safely_reused_logical_requests"], 0)
        mappings = plan["district_to_request_provenance"]
        self.assertEqual(len(mappings), 64)
        self.assertTrue(all(len(item["logical_request_ids"]) == 25 for item in mappings))
        self.assertTrue(all(item["shared_response_mapping"] is None for item in mappings))

    def test_reuse_decision_is_checksum_bound_and_blocks_full_execution(self):
        validated = power.validate_reuse_decision(self.reuse_decision, self.config)
        self.assertEqual(validated["configuration"]["sha256"], power.sha256(power.DEFAULT_CONFIG.read_bytes()))
        with self.assertRaisesRegex(power.ConfigurationError, "no authoritative"):
            power.require_full_execution_ready(validated)
        tampered = copy.deepcopy(validated)
        tampered["configuration"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(power.ConfigurationError, "checksum"):
            power.validate_reuse_decision(tampered, self.config)

    def test_blocked_summary_records_every_pending_district_year(self):
        plan = power.build_full_plan(self.config, self.reuse_decision)
        summary = power.build_blocked_full_summary(self.config, plan)
        coverage = summary["coverage"]["district_year"]
        self.assertEqual(len(coverage), 1600)
        self.assertEqual(sum(item["expected_daily_records"] for item in coverage), 584384)
        self.assertTrue(all(item["returned_daily_records"] == 0 for item in coverage))
        self.assertTrue(all(item["status"] == "pending_not_requested" for item in coverage))
        self.assertTrue(all(item["shared_response_request_id"] is None for item in coverage))
        self.assertEqual(summary["missingness"]["status"], "not_assessed_no_full_responses")
        self.assertTrue(all(not any(item["fill_counts"].values()) for item in summary["preexisting_smoke_evidence"]))

    def test_response_validation_checks_dates_parameters_units_time_and_fill(self):
        raw = synthetic_response(self.smoke_request, self.config)
        result = power.validate_response_bytes(raw, self.smoke_request, self.config)
        self.assertEqual(result["date_count"], 31)
        self.assertEqual(result["time_standard"], "LST")
        self.assertEqual(result["fill_value"], -999)
        self.assertEqual(result["fill_counts"]["PRECTOTCORR"], 1)
        self.assertEqual(result["units"]["PRECTOTCORR"], "mm/day")

    def test_response_validation_rejects_api_errors_and_unexpected_content(self):
        with self.assertRaises(power.ResponseValidationError):
            power.validate_response_bytes(b'{"header":"failed","messages":["bad request"]}', self.smoke_request, self.config)
        with self.assertRaises(power.ResponseValidationError):
            power.validate_response_bytes(synthetic_response(self.smoke_request, self.config, extra_parameter=True), self.smoke_request, self.config)
        with self.assertRaises(power.ResponseValidationError):
            power.validate_response_bytes(synthetic_response(self.smoke_request, self.config, time_standard="UTC"), self.smoke_request, self.config)
        wrong_range = json.loads(synthetic_response(self.smoke_request, self.config))
        wrong_range["header"]["end"] = "20010201"
        with self.assertRaises(power.ResponseValidationError):
            power.validate_response_bytes(json.dumps(wrong_range).encode(), self.smoke_request, self.config)

    def test_permanent_http_error_stops_without_retry_and_preserves_body(self):
        calls = []

        def opener(url, timeout):
            calls.append((url, timeout))
            raise urllib.error.HTTPError(url, 422, "validation", {}, io.BytesIO(b'{"messages":["synthetic 422"]}'))

        with tempfile.TemporaryDirectory() as temporary:
            downloader = self.downloader(temporary, opener)
            with self.assertRaises(power.DownloadError):
                downloader.download(self.smoke_request)
            self.assertEqual(len(calls), 1)
            bodies = list((downloader.cache_root / "errors").rglob("*.body"))
            self.assertEqual(len(bodies), 1)
            self.assertIn(b"synthetic 422", bodies[0].read_bytes())

    def test_retry_after_is_honored_before_success(self):
        calls = []
        sleeps = []
        good = synthetic_response(self.smoke_request, self.config)

        def opener(url, timeout):
            calls.append(url)
            if len(calls) == 1:
                raise urllib.error.HTTPError(url, 429, "rate", {"Retry-After": "3"}, io.BytesIO(b'{"message":"synthetic 429"}'))
            return FakeResponse(good)

        with tempfile.TemporaryDirectory() as temporary:
            result = self.downloader(temporary, opener, sleeps=sleeps).download(self.smoke_request)
            self.assertEqual(result["acquisition_status"], "downloaded_verified")
            self.assertEqual(len(calls), 2)
            self.assertEqual(sleeps, [3.0])

    def test_checksum_aware_resume_skips_valid_and_replaces_corrupt_cache(self):
        calls = []
        good = synthetic_response(self.smoke_request, self.config)

        def opener(url, timeout):
            calls.append(url)
            return FakeResponse(good)

        with tempfile.TemporaryDirectory() as temporary:
            downloader = self.downloader(temporary, opener)
            first = downloader.download(self.smoke_request)
            second = downloader.download(self.smoke_request)
            self.assertEqual(first["acquisition_status"], "downloaded_verified")
            self.assertEqual(second["acquisition_status"], "downloaded_verified")
            self.assertEqual(second["resume_status"], "cached_verified")
            self.assertEqual(len(calls), 1)
            raw_path, _ = downloader.paths(self.smoke_request)
            raw_path.write_bytes(raw_path.read_bytes() + b"corrupt")
            third = downloader.download(self.smoke_request)
            self.assertEqual(third["acquisition_status"], "downloaded_verified")
            self.assertEqual(len(calls), 2)
            self.assertTrue(list((downloader.cache_root / "errors").rglob("*.corrupt.*")))

    def test_interrupted_download_never_becomes_successful_cache(self):
        local_config = copy.deepcopy(self.config)
        local_config["network_policy"]["max_attempts"] = 1
        raw = synthetic_response(self.smoke_request, local_config)

        with tempfile.TemporaryDirectory() as temporary:
            downloader = self.downloader(temporary, lambda url, timeout: InterruptedResponse(raw), config=local_config)
            with self.assertRaises(power.DownloadError):
                downloader.download(self.smoke_request)
            raw_path, manifest_path = downloader.paths(self.smoke_request)
            self.assertFalse(raw_path.exists())
            self.assertFalse(manifest_path.exists())
            self.assertTrue(list((downloader.cache_root / "errors").rglob("*.partial")))


if __name__ == "__main__":
    unittest.main()
