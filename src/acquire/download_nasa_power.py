#!/usr/bin/env python3
"""Build, inspect, and safely execute NASA POWER daily point requests."""

import argparse
import csv
import email.utils
import hashlib
import json
import os
import random
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "data/climate/nasa_power_daily_v1.json"
DEFAULT_REGISTRY = ROOT / "data/climate/district_sampling_registry.csv"
DEFAULT_REGISTRY_MANIFEST = ROOT / "data/climate/district_sampling_manifest.json"
DEFAULT_CACHE = ROOT / "cache/nasa_power"
DEFAULT_SMOKE_MANIFEST = ROOT / "data/climate/nasa_power_smoke_test_manifest.json"
DEFAULT_REUSE_DECISION = ROOT / "data/climate/nasa_power_request_reuse_v1.json"
DEFAULT_FULL_PLAN = ROOT / "data/climate/nasa_power_full_acquisition_plan.json"
DEFAULT_FULL_SUMMARY = ROOT / "data/climate/nasa_power_full_acquisition_summary.json"

PARAMETERS = {
    "PRECTOTCORR": {
        "name": "Precipitation Corrected",
        "units": "mm/day",
        "definition": "Average MERRA-2 bias-corrected total precipitation at the surface.",
    },
    "T2M": {
        "name": "Temperature at 2 Meters",
        "units": "C",
        "definition": "Average air temperature at 2 meters.",
    },
    "T2M_MIN": {
        "name": "Temperature at 2 Meters Minimum",
        "units": "C",
        "definition": "Minimum hourly air temperature at 2 meters in the daily period.",
    },
    "T2M_MAX": {
        "name": "Temperature at 2 Meters Maximum",
        "units": "C",
        "definition": "Maximum hourly air temperature at 2 meters in the daily period.",
    },
}

TRANSIENT_HTTP_STATUS = {408, 429, 500, 502, 503, 504}


class ConfigurationError(ValueError):
    pass


class ResponseValidationError(ValueError):
    pass


class DownloadError(RuntimeError):
    def __init__(self, message, status=None, retry_after=None, body=b"", headers=None):
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after
        self.body = body
        self.headers = headers or {}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def atomic_write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".partial-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def recorded_path(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_yyyymmdd(value):
    try:
        return datetime.strptime(str(value), "%Y%m%d").date()
    except ValueError as error:
        raise ConfigurationError(f"Invalid YYYYMMDD date: {value}") from error


def expected_dates(start, end):
    first = parse_yyyymmdd(start)
    last = parse_yyyymmdd(end)
    if last < first:
        raise ConfigurationError(f"End precedes start: {start}..{end}")
    count = (last - first).days + 1
    return [(first + timedelta(days=offset)).strftime("%Y%m%d") for offset in range(count)]


def build_config(registry_path=DEFAULT_REGISTRY, manifest_path=DEFAULT_REGISTRY_MANIFEST):
    registry_raw = registry_path.read_bytes()
    registry_manifest = json.loads(manifest_path.read_text())
    registry_hash = sha256(registry_raw)
    if registry_hash != registry_manifest["registry_sha256"]:
        raise ConfigurationError("Registry checksum does not match its manifest")
    rows = list(csv.DictReader(registry_raw.decode("utf-8").splitlines()))
    if len(rows) != 64 or len({row["district_id"] for row in rows}) != 64:
        raise ConfigurationError("Registry must contain exactly 64 unique district IDs")
    points = [
        {
            "district_id": row["district_id"],
            "district_name_en": row["district_name_en"],
            "district_name_bn": row["district_name_bn"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
        }
        for row in rows
    ]
    years = 2025 - 2001 + 1
    return {
        "schema_version": "1.0.0",
        "collection_id": "nasa-power-daily-bgd-64-v1",
        "status": "configuration_verified",
        "accessed_on": "2026-11-13",
        "source": {
            "name": "NASA POWER Daily Point API",
            "endpoint": "https://power.larc.nasa.gov/api/temporal/daily/point",
            "community": "AG",
            "format": "JSON",
            "time_standard": "LST",
            "units_system": "metric",
            "openapi_version": "v2.10.3",
            "documentation_urls": [
                "https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
                "https://power.larc.nasa.gov/docs/services/api/",
                "https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/",
                "https://power.larc.nasa.gov/api/temporal/daily/openapi.json",
                "https://power.larc.nasa.gov/api/system/manager/parameters",
            ],
        },
        "registry": {
            "path": str(registry_path.relative_to(ROOT)),
            "manifest_path": str(manifest_path.relative_to(ROOT)),
            "sha256": registry_hash,
            "row_count": 64,
            "coordinate_use": "Named latitude and longitude request parameters; no NASA grid-cell IDs assigned.",
        },
        "requested_coverage": {
            "start": "20010101",
            "end": "20251231",
            "start_iso": "2001-01-01",
            "end_iso": "2025-12-31",
            "temporal": "daily",
            "parameters": PARAMETERS,
            "fill_value": -999,
            "availability_evidence": "Daily UTC and LST are documented from 1981-01-01 to near real time; parameter-specific response availability remains subject to validation.",
        },
        "verified_actual_coverage": {
            "status": "recorded_separately_after_acquisition",
            "manifest_path": "data/climate/nasa_power_smoke_test_manifest.json",
            "note": "Requested coverage is configuration intent. Only successful response manifests establish actual coverage; the smoke manifest does not verify full coverage.",
        },
        "chunking": {
            "strategy": "calendar_year_per_point",
            "reason": "A project-defined bounded response size; NASA publishes no smaller required date-span limit for this four-parameter point request.",
            "years_per_point": years,
            "parameters_per_request": 4,
            "official_single_point_parameter_maximum": 20,
            "configured_full_request_count": len(points) * years,
        },
        "network_policy": {
            "concurrency": 1,
            "inter_request_delay_seconds": 1.0,
            "timeout_seconds": 60.0,
            "max_attempts": 4,
            "backoff_initial_seconds": 2.0,
            "backoff_max_seconds": 60.0,
            "backoff_jitter_seconds": 0.5,
            "retry_http_status": sorted(TRANSIENT_HTTP_STATUS),
            "permanent_http_status": "Other 4xx responses, including documented 422, stop without retry.",
            "retry_after": "Honor Retry-After delta-seconds or HTTP-date when present.",
            "official_concurrency_guidance_maximum": 5,
            "official_requests_per_second_limit": None,
            "official_guidance": "The official multipoint tutorial says not to exceed five concurrent requests; general guidance warns against too many synchronous requests or repeatedly requesting the same relative grid location. No requests-per-second quota is published there.",
        },
        "storage": {
            "root": "cache/nasa_power/nasa-power-daily-bgd-64-v1",
            "raw_layout": "raw/{district_id}/{start}_{end}.json",
            "request_manifest_layout": "raw/{district_id}/{start}_{end}.manifest.json",
            "error_layout": "errors/{district_id}/{request_id}.{attempt}.{timestamp}.{body|partial|json}",
            "raw_policy": "Original HTTP response bytes are moved atomically into ignored cache storage only after structural validation.",
        },
        "points": points,
        "smoke_test": {
            "districts": [
                {
                    "district_id": "bd-district-bagerhat",
                    "reason": "Southwestern coastal district; contrasts geographically with the southeastern hill district.",
                },
                {
                    "district_id": "bd-district-rangamati",
                    "reason": "Southeastern hill district; provides a distant coordinate and geographic contrast.",
                },
            ],
            "periods": [
                {"start": "20010101", "end": "20010131", "label": "January 2001"},
                {"start": "20250101", "end": "20250131", "label": "January 2025"},
            ],
            "expected_request_count": 4,
        },
        "limitations": [
            "One point represents regional gridded context, not a district average, station or farm measurement.",
            "Nearby district points may resolve to the same POWER grid cell; the configuration does not invent grid-cell IDs.",
            "The configured full request count is 1,600 before any future evidence-based same-cell deduplication review.",
            "The official tutorial says not to exceed five concurrent requests but publishes no requests-per-second quota there; this configuration is conservatively sequential.",
        ],
    }


def validate_config(config, registry_path=DEFAULT_REGISTRY):
    required = {"schema_version", "collection_id", "source", "registry", "requested_coverage", "chunking", "network_policy", "points", "smoke_test"}
    if not required.issubset(config):
        raise ConfigurationError(f"Missing configuration keys: {sorted(required - set(config))}")
    registry_hash = sha256(registry_path.read_bytes())
    if config["registry"]["sha256"] != registry_hash:
        raise ConfigurationError("Configured registry checksum does not match current registry bytes")
    if len(config["points"]) != 64 or len({point["district_id"] for point in config["points"]}) != 64:
        raise ConfigurationError("Configuration must contain 64 unique district points")
    if config["source"]["community"] != "AG" or config["source"]["time_standard"] != "LST":
        raise ConfigurationError("POWER community must be AG and time standard must be explicit LST")
    if set(config["requested_coverage"]["parameters"]) != set(PARAMETERS):
        raise ConfigurationError("Configured POWER parameter set is not the approved four-parameter set")
    for name, details in PARAMETERS.items():
        if config["requested_coverage"]["parameters"][name]["units"] != details["units"]:
            raise ConfigurationError(f"Unexpected configured units for {name}")
    if config["requested_coverage"]["start"] != "20010101" or config["requested_coverage"]["end"] != "20251231":
        raise ConfigurationError("Requested coverage must remain 2001-01-01 through 2025-12-31")
    if config["chunking"]["configured_full_request_count"] != 1600:
        raise ConfigurationError("Full request count must be 64 points × 25 calendar years = 1,600")
    if config["network_policy"]["concurrency"] != 1:
        raise ConfigurationError("This version supports only conservative sequential acquisition")
    if config["smoke_test"]["expected_request_count"] != 4:
        raise ConfigurationError("Smoke scope must remain exactly four requests")
    return config


def load_config(path=DEFAULT_CONFIG):
    return validate_config(json.loads(path.read_text()))


def build_reuse_decision(config_path=DEFAULT_CONFIG):
    config_raw = config_path.read_bytes()
    config = validate_config(json.loads(config_raw))
    return {
        "schema_version": "1.0.0",
        "decision_id": "nasa-power-bgd-request-reuse-v1",
        "recorded_on": "2026-11-13",
        "status": "blocked_no_authoritative_equivalence_key",
        "full_execution_allowed": False,
        "collection_id": config["collection_id"],
        "configuration": {
            "path": recorded_path(config_path),
            "sha256": sha256(config_raw),
            "registry_sha256": config["registry"]["sha256"],
        },
        "requested_parameters": sorted(PARAMETERS),
        "decision": (
            "Do not deduplicate and do not start the full collection. The reviewed official POWER materials "
            "do not expose an authoritative pre-request grid-cell identifier, grid origin/indexing rule, or "
            "parameter-complete point-to-cell mapping for these four parameters."
        ),
        "evidence": [
            {
                "source": "https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
                "finding": (
                    "The Daily API warns that a 0.5 degree by 0.5 degree catalog needs one request per cell, "
                    "but it does not define a point-to-cell snapping/indexing algorithm or return a cell ID."
                ),
            },
            {
                "source": "https://power.larc.nasa.gov/docs/methodology/",
                "finding": (
                    "POWER says Release 9 meteorological inputs use 0.5 degree latitude by 0.625 degree "
                    "longitude spatial resolution and that products retain input-data resolutions."
                ),
            },
            {
                "source": "https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/",
                "finding": (
                    "The four requested variables are meteorological products associated with MERRA-2/GEOS, "
                    "but common source family/resolution alone does not establish the API's point-to-cell mapping."
                ),
            },
            {
                "source": "https://power.larc.nasa.gov/api/temporal/daily/openapi.json",
                "finding": (
                    "POWER Daily API v2.10.3 defines Geometry.coordinates as a generic array and documents no "
                    "grid-cell identifier, grid index, coordinate meaning, or equivalence field."
                ),
            },
            {
                "source": recorded_path(DEFAULT_SMOKE_MANIFEST),
                "finding": (
                    "All four smoke responses identify API v2.10.3 and sources MERRA2/POWER. Their geometry "
                    "coordinates are rounded forms of the submitted district points plus elevation; this field "
                    "is preserved as response metadata and is not treated as a documented grid key."
                ),
            },
        ],
        "prohibited_inferences": [
            "Do not group points by proximity or locally rounded latitude/longitude.",
            "Do not group responses because observed weather values happen to match.",
            "Do not construct or label a NASA grid-cell ID.",
            "Do not assume all parameters share a request-equivalence mapping from resolution alone.",
        ],
        "resolution_condition": (
            "Full execution may proceed only after official POWER evidence supplies an authoritative mapping or "
            "equivalence key covering PRECTOTCORR, T2M, T2M_MIN and T2M_MAX, and the checked-in decision and "
            "district-to-request mapping are independently reviewed and updated."
        ),
    }


def validate_reuse_decision(decision, config, config_path=DEFAULT_CONFIG):
    required = {"schema_version", "status", "full_execution_allowed", "collection_id", "configuration", "requested_parameters"}
    if not required.issubset(decision):
        raise ConfigurationError(f"Missing reuse-decision keys: {sorted(required - set(decision))}")
    if decision["collection_id"] != config["collection_id"]:
        raise ConfigurationError("Reuse decision belongs to another collection")
    if decision["configuration"]["sha256"] != sha256(config_path.read_bytes()):
        raise ConfigurationError("Reuse decision configuration checksum does not match current configuration")
    if decision["configuration"]["registry_sha256"] != config["registry"]["sha256"]:
        raise ConfigurationError("Reuse decision registry checksum does not match current configuration")
    if set(decision["requested_parameters"]) != set(PARAMETERS):
        raise ConfigurationError("Reuse decision does not cover the complete requested parameter set")
    return decision


def load_reuse_decision(path, config, config_path=DEFAULT_CONFIG):
    return validate_reuse_decision(json.loads(path.read_text()), config, config_path)


def require_full_execution_ready(decision):
    if decision["status"] != "verified_parameter_complete_equivalence_mapping" or not decision["full_execution_allowed"]:
        raise ConfigurationError(
            "Full acquisition blocked: no authoritative parameter-complete pre-request equivalence mapping is available; "
            "see data/climate/nasa_power_request_reuse_v1.json"
        )


def year_chunks(start, end):
    first = parse_yyyymmdd(start)
    last = parse_yyyymmdd(end)
    chunks = []
    for year in range(first.year, last.year + 1):
        chunk_start = max(first, date(year, 1, 1))
        chunk_end = min(last, date(year, 12, 31))
        chunks.append((chunk_start.strftime("%Y%m%d"), chunk_end.strftime("%Y%m%d")))
    return chunks


def build_requests(config, scope):
    points = {point["district_id"]: point for point in config["points"]}
    if scope == "smoke":
        selected = [points[item["district_id"]] for item in config["smoke_test"]["districts"]]
        periods = [(item["start"], item["end"]) for item in config["smoke_test"]["periods"]]
    elif scope == "full":
        selected = list(config["points"])
        periods = year_chunks(config["requested_coverage"]["start"], config["requested_coverage"]["end"])
    else:
        raise ConfigurationError(f"Unsupported scope: {scope}")
    requests = []
    for point in selected:
        for start, end in periods:
            params = {
                "parameters": ",".join(PARAMETERS),
                "community": config["source"]["community"],
                "longitude": f"{point['longitude']:.6f}",
                "latitude": f"{point['latitude']:.6f}",
                "start": start,
                "end": end,
                "format": config["source"]["format"],
                "time-standard": config["source"]["time_standard"],
                "units": config["source"]["units_system"],
            }
            requests.append(
                {
                    "request_id": f"{point['district_id']}__{start}_{end}",
                    "district": point,
                    "start": start,
                    "end": end,
                    "parameters": params,
                    "url": config["source"]["endpoint"] + "?" + urllib.parse.urlencode(params),
                }
            )
    return requests


def request_fingerprint(config, request_spec):
    return sha256(
        canonical_json(
            {
                "collection_id": config["collection_id"],
                "registry_sha256": config["registry"]["sha256"],
                "request_id": request_spec["request_id"],
                "parameters": request_spec["parameters"],
            }
        )
    )


def validate_response_bytes(raw, request_spec, config):
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ResponseValidationError("Response is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise ResponseValidationError("Response root is not an object")
    if payload.get("type") != "Feature" or not isinstance(payload.get("properties"), dict):
        detail = payload.get("messages") or payload.get("message") or payload.get("header")
        raise ResponseValidationError(f"POWER error or unexpected payload: {detail!r}")
    header = payload.get("header")
    if not isinstance(header, dict):
        raise ResponseValidationError("Successful payload has no header object")
    if str(header.get("start")) != request_spec["start"] or str(header.get("end")) != request_spec["end"]:
        raise ResponseValidationError("Response date range differs from request")
    if header.get("fill_value") != config["requested_coverage"]["fill_value"]:
        raise ResponseValidationError("Unexpected or missing fill-value convention")
    response_time_standard = str(header.get("time_standard", "")).upper()
    if response_time_standard != config["source"]["time_standard"]:
        raise ResponseValidationError(f"Unexpected response time standard: {response_time_standard!r}")
    series = payload["properties"].get("parameter")
    if not isinstance(series, dict) or set(series) != set(PARAMETERS):
        raise ResponseValidationError(f"Unexpected response parameters: {sorted(series or {})}")
    metadata = payload.get("parameters")
    if not isinstance(metadata, dict) or set(metadata) != set(PARAMETERS):
        raise ResponseValidationError("Parameter metadata is missing or unexpected")
    dates = expected_dates(request_spec["start"], request_spec["end"])
    fill_value = header["fill_value"]
    fill_counts = {}
    for name, expected in PARAMETERS.items():
        values = series[name]
        if not isinstance(values, dict) or list(values) != dates:
            raise ResponseValidationError(f"{name} dates are missing, duplicated, reordered or unexpected")
        if metadata[name].get("units") != expected["units"]:
            raise ResponseValidationError(f"Unexpected units for {name}: {metadata[name].get('units')!r}")
        if any(not isinstance(value, (int, float)) for value in values.values()):
            raise ResponseValidationError(f"{name} contains a non-numeric value")
        fill_counts[name] = sum(value == fill_value for value in values.values())
    geometry = payload.get("geometry")
    if not isinstance(geometry, dict) or geometry.get("type") != "Point" or not isinstance(geometry.get("coordinates"), list):
        raise ResponseValidationError("Response geometry metadata is missing")
    api = header.get("api") if isinstance(header.get("api"), dict) else {}
    return {
        "status": "valid",
        "actual_start": str(header["start"]),
        "actual_end": str(header["end"]),
        "date_count": len(dates),
        "parameter_names": sorted(series),
        "units": {name: metadata[name]["units"] for name in sorted(metadata)},
        "time_standard": response_time_standard,
        "fill_value": fill_value,
        "fill_counts": fill_counts,
        "response_geometry": geometry,
        "api": api,
        "title": header.get("title"),
        "sources": header.get("sources"),
    }


def retry_after_seconds(value, now=None):
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            parsed = email.utils.parsedate_to_datetime(value)
            reference = now or datetime.now(timezone.utc)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return max(0.0, (parsed - reference).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def default_opener(url, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": "soil-to-stars-climate-acquire/1.0"})
    return urllib.request.urlopen(request, timeout=timeout)


class PowerDownloader:
    def __init__(self, config, cache_root=DEFAULT_CACHE, opener=default_opener, sleeper=time.sleep, random_source=random.random, now=utc_now):
        self.config = config
        self.cache_root = Path(cache_root) / config["collection_id"]
        self.opener = opener
        self.sleeper = sleeper
        self.random_source = random_source
        self.now = now

    def paths(self, request_spec):
        district = request_spec["district"]["district_id"]
        stem = f"{request_spec['start']}_{request_spec['end']}"
        raw = self.cache_root / "raw" / district / f"{stem}.json"
        return raw, raw.with_suffix(".manifest.json")

    def _quarantine(self, request_spec, paths, reason):
        timestamp = self.now().replace(":", "").replace("-", "")
        error_dir = self.cache_root / "errors" / request_spec["district"]["district_id"]
        error_dir.mkdir(parents=True, exist_ok=True)
        for path in paths:
            if path.exists():
                destination = error_dir / f"{request_spec['request_id']}.corrupt.{timestamp}.{path.name}"
                shutil.move(str(path), destination)
        atomic_write(
            error_dir / f"{request_spec['request_id']}.corrupt.{timestamp}.json",
            (json.dumps({"status": "quarantined", "reason": reason, "recorded_at_utc": self.now()}, indent=2) + "\n").encode(),
        )

    def _cached(self, request_spec):
        raw_path, manifest_path = self.paths(request_spec)
        if not raw_path.exists() and not manifest_path.exists():
            return None
        try:
            manifest = json.loads(manifest_path.read_text())
            raw = raw_path.read_bytes()
            if manifest["request_fingerprint"] != request_fingerprint(self.config, request_spec):
                raise ValueError("request fingerprint mismatch")
            if manifest["response"]["sha256"] != sha256(raw) or manifest["response"]["bytes"] != len(raw):
                raise ValueError("raw checksum or byte count mismatch")
            validation = validate_response_bytes(raw, request_spec, self.config)
            if manifest["validation"] != validation:
                raise ValueError("cached validation metadata mismatch")
            return {**manifest, "resume_status": "cached_verified"}
        except (OSError, KeyError, ValueError, json.JSONDecodeError, ResponseValidationError) as error:
            self._quarantine(request_spec, (raw_path, manifest_path), str(error))
            return None

    def _save_failure(self, request_spec, attempt, kind, body, details):
        timestamp = self.now().replace(":", "").replace("-", "")
        directory = self.cache_root / "errors" / request_spec["district"]["district_id"]
        directory.mkdir(parents=True, exist_ok=True)
        stem = f"{request_spec['request_id']}.attempt-{attempt}.{timestamp}"
        if body:
            atomic_write(directory / f"{stem}.{kind}", body)
        record = {
            "schema_version": "1.0.0",
            "status": "failed_attempt",
            "kind": kind,
            "attempt": attempt,
            "recorded_at_utc": self.now(),
            "request_id": request_spec["request_id"],
            "url": request_spec["url"],
            **details,
        }
        atomic_write(directory / f"{stem}.json", (json.dumps(record, indent=2, sort_keys=True) + "\n").encode())

    def _stream_once(self, request_spec, attempt):
        raw_path, _ = self.paths(request_spec)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".partial-", dir=raw_path.parent)
        keep_temporary = False
        try:
            try:
                response = self.opener(request_spec["url"], self.config["network_policy"]["timeout_seconds"])
                with response:
                    status = getattr(response, "status", None)
                    if status is None:
                        status = response.getcode()
                    headers = dict(response.headers.items())
                    if status != 200:
                        body = response.read()
                        raise DownloadError(f"HTTP {status}", status=status, retry_after=headers.get("Retry-After"), body=body, headers=headers)
                    with os.fdopen(descriptor, "wb") as output:
                        descriptor = None
                        while True:
                            chunk = response.read(64 * 1024)
                            if not chunk:
                                break
                            output.write(chunk)
                        output.flush()
                        os.fsync(output.fileno())
                raw = Path(temporary).read_bytes()
                validation = validate_response_bytes(raw, request_spec, self.config)
                keep_temporary = True
                return temporary, raw, headers, validation
            except urllib.error.HTTPError as error:
                body = error.read()
                headers = dict(error.headers.items()) if error.headers else {}
                raise DownloadError(
                    f"HTTP {error.code}",
                    status=error.code,
                    retry_after=headers.get("Retry-After"),
                    body=body,
                    headers=headers,
                ) from error
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                partial = Path(temporary).read_bytes() if Path(temporary).exists() else b""
                self._save_failure(request_spec, attempt, "partial", partial, {"error": repr(error)})
                raise DownloadError(f"Network or interrupted download: {error}") from error
            except ResponseValidationError as error:
                body = Path(temporary).read_bytes() if Path(temporary).exists() else b""
                self._save_failure(request_spec, attempt, "body", body, {"error": str(error), "http_status": 200})
                raise
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if not keep_temporary and "temporary" in locals() and os.path.exists(temporary):
                os.unlink(temporary)

    def download(self, request_spec):
        cached = self._cached(request_spec)
        if cached:
            return cached
        policy = self.config["network_policy"]
        for attempt in range(1, policy["max_attempts"] + 1):
            try:
                temporary, raw, headers, validation = self._stream_once(request_spec, attempt)
                raw_path, manifest_path = self.paths(request_spec)
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temporary, raw_path)
                manifest = {
                    "schema_version": "1.0.0",
                    "collection_id": self.config["collection_id"],
                    "configuration_fingerprint": sha256(canonical_json(self.config)),
                    "registry_sha256": self.config["registry"]["sha256"],
                    "request_id": request_spec["request_id"],
                    "request_fingerprint": request_fingerprint(self.config, request_spec),
                    "district": request_spec["district"],
                    "request": {
                        "url": request_spec["url"],
                        "parameters": request_spec["parameters"],
                        "requested_at_utc": self.now(),
                        "attempt": attempt,
                    },
                    "response": {
                        "http_status": 200,
                        "retrieved_at_utc": self.now(),
                        "sha256": sha256(raw),
                        "bytes": len(raw),
                        "content_type": headers.get("Content-Type") or headers.get("content-type"),
                        "raw_path": recorded_path(raw_path),
                    },
                    "validation": validation,
                    "acquisition_status": "downloaded_verified",
                }
                atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
                return manifest
            except ResponseValidationError:
                raise
            except DownloadError as error:
                self._save_failure(
                    request_spec,
                    attempt,
                    "body",
                    error.body,
                    {"error": str(error), "http_status": error.status, "retry_after": error.retry_after},
                )
                retryable = error.status is None or error.status in TRANSIENT_HTTP_STATUS
                if not retryable or attempt == policy["max_attempts"]:
                    raise
                retry_after = retry_after_seconds(error.retry_after)
                exponential = min(policy["backoff_max_seconds"], policy["backoff_initial_seconds"] * (2 ** (attempt - 1)))
                delay = retry_after if retry_after is not None else exponential + self.random_source() * policy["backoff_jitter_seconds"]
                self.sleeper(min(policy["backoff_max_seconds"], delay))
        raise AssertionError("unreachable")


def smoke_summary(config, results):
    successful = [result for result in results if result.get("status") in {"downloaded_verified", "cached_verified"}]
    failed = [result for result in results if result.get("status") == "failed"]
    return {
        "schema_version": "1.0.0",
        "collection_id": config["collection_id"],
        "recorded_at_utc": utc_now(),
        "scope": "Exactly two configured districts × January 2001 and January 2025; four requests maximum.",
        "requested_full_coverage": config["requested_coverage"],
        "verified_actual_coverage": {
            "status": "smoke_test_only",
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "periods": sorted({(result["start"], result["end"]) for result in successful}),
            "district_ids": sorted({result["district_id"] for result in successful}),
        },
        "registry_sha256": config["registry"]["sha256"],
        "configuration_fingerprint": sha256(canonical_json(config)),
        "results": results,
        "limitations": [
            "Smoke success does not verify all 64 districts or the complete 2001-2025 period.",
            "Raw responses remain in ignored cache storage and are referenced by checksum/path.",
            "No NASA grid-cell IDs are created; response geometry is preserved as returned metadata.",
        ],
    }


def build_full_plan(config, reuse_decision):
    requests = build_requests(config, "full")
    by_district = {}
    for request_spec in requests:
        district_id = request_spec["district"]["district_id"]
        entry = by_district.setdefault(
            district_id,
            {
                "district_id": district_id,
                "district_name_en": request_spec["district"]["district_name_en"],
                "district_name_bn": request_spec["district"]["district_name_bn"],
                "original_sampling_point": {
                    "latitude": request_spec["district"]["latitude"],
                    "longitude": request_spec["district"]["longitude"],
                    "coordinate_reference_system": "EPSG:4326",
                },
                "logical_request_ids": [],
                "shared_response_mapping": None,
                "reuse_status": "not_established",
            },
        )
        entry["logical_request_ids"].append(request_spec["request_id"])
    expected_days_per_district = len(expected_dates(config["requested_coverage"]["start"], config["requested_coverage"]["end"]))
    return {
        "schema_version": "1.0.0",
        "plan_id": "nasa-power-daily-bgd-64-full-plan-v1",
        "recorded_on": "2026-11-13",
        "collection_id": config["collection_id"],
        "status": "blocked_before_network_execution",
        "execution_gate": {
            "reuse_decision_status": reuse_decision["status"],
            "full_execution_allowed": reuse_decision["full_execution_allowed"],
            "reason": reuse_decision["decision"],
        },
        "configuration_fingerprint": sha256(canonical_json(config)),
        "registry_sha256": config["registry"]["sha256"],
        "requested_scope": {
            "district_count": 64,
            "start": config["requested_coverage"]["start_iso"],
            "end": config["requested_coverage"]["end_iso"],
            "parameters": sorted(PARAMETERS),
            "time_standard": config["source"]["time_standard"],
            "logical_request_count": len(requests),
            "expected_days_per_district": expected_days_per_district,
            "expected_district_daily_records": expected_days_per_district * len(by_district),
            "expected_parameter_values_before_missingness": expected_days_per_district * len(by_district) * len(PARAMETERS),
        },
        "request_reuse": {
            "authoritative_unique_network_requests": None,
            "safely_reused_logical_requests": 0,
            "pending_logical_requests": len(requests),
            "note": (
                "The 1,600 district-year request identities are preserved, but their safe many-to-one network "
                "mapping is unresolved. Treating all 1,600 as executable would ignore POWER's repeated-cell warning."
            ),
        },
        "storage": config["storage"],
        "network_policy": config["network_policy"],
        "resume_behavior": (
            "For an authorized request, accept cache only after request fingerprint, byte count, SHA-256 and fresh "
            "structural validation match; quarantine corrupt evidence and never overwrite it silently."
        ),
        "district_to_request_provenance": list(by_district.values()),
        "commands": {
            "dry_run": "python3 src/acquire/download_nasa_power.py --check-config --scope full --write-full-plan",
            "full_or_resume_when_gate_is_resolved": (
                "python3 src/acquire/download_nasa_power.py --config data/climate/nasa_power_daily_v1.json "
                "--scope full --execute --confirm-full-collection"
            ),
        },
    }


def build_blocked_full_summary(config, plan, smoke_manifest_path=DEFAULT_SMOKE_MANIFEST):
    smoke = json.loads(smoke_manifest_path.read_text())
    smoke_evidence = [
        {
            "request_id": item["request_id"],
            "status": item["status"],
            "retrieved_at_utc": item["retrieved_at_utc"],
            "api": item["validation"]["api"],
            "raw_sha256": item["raw_sha256"],
            "actual_start": item["validation"]["actual_start"],
            "actual_end": item["validation"]["actual_end"],
            "fill_counts": item["validation"]["fill_counts"],
        }
        for item in smoke["results"]
    ]
    expected = plan["requested_scope"]
    district_year_coverage = []
    for district in plan["district_to_request_provenance"]:
        for request_id in district["logical_request_ids"]:
            start, end = request_id.rsplit("__", 1)[1].split("_")
            district_year_coverage.append(
                {
                    "district_id": district["district_id"],
                    "start": start,
                    "end": end,
                    "expected_daily_records": len(expected_dates(start, end)),
                    "returned_daily_records": 0,
                    "status": "pending_not_requested",
                    "shared_response_request_id": None,
                }
            )
    return {
        "schema_version": "1.0.0",
        "collection_id": config["collection_id"],
        "recorded_on": "2026-11-13",
        "status": "blocked_before_full_acquisition",
        "counts": {
            "logical_requests_expected": expected["logical_request_count"],
            "full_requests_complete": 0,
            "full_requests_failed": 0,
            "full_requests_pending": expected["logical_request_count"],
            "shared_response_reuses_verified": 0,
            "preexisting_smoke_requests_not_counted_as_full": len(smoke_evidence),
        },
        "coverage": {
            "districts_requested": 64,
            "districts_with_full_verified_coverage": 0,
            "requested_start": expected["start"],
            "requested_end": expected["end"],
            "expected_district_daily_records": expected["expected_district_daily_records"],
            "returned_full_daily_records": 0,
            "district_year": district_year_coverage,
        },
        "missingness": {
            "status": "not_assessed_no_full_responses",
            "by_district_year_parameter": [],
            "note": "Pending acquisition is not counted as fill/missing observations or usable scientific coverage.",
        },
        "failures": [],
        "blockers": [plan["execution_gate"]["reason"]],
        "unexpected_metadata_or_source_inconsistencies": [
            (
                "The Daily API page describes a 0.5 degree by 0.5 degree catalog grid, while POWER methodology "
                "documents 0.5 degree latitude by 0.625 degree longitude native meteorological resolution; neither "
                "source supplies a point-to-cell equivalence mapping."
            )
        ],
        "preexisting_smoke_evidence": smoke_evidence,
        "plan_path": recorded_path(DEFAULT_FULL_PLAN),
    }


def execute(config, scope, cache_dir, smoke_manifest_path):
    requests = build_requests(config, scope)
    downloader = PowerDownloader(config, cache_dir)
    results = []
    for index, request_spec in enumerate(requests):
        try:
            manifest = downloader.download(request_spec)
            validation = manifest["validation"]
            results.append(
                {
                    "status": manifest["acquisition_status"],
                    "resume_status": manifest.get("resume_status"),
                    "district_id": request_spec["district"]["district_id"],
                    "start": request_spec["start"],
                    "end": request_spec["end"],
                    "request_id": request_spec["request_id"],
                    "request_parameters": request_spec["parameters"],
                    "raw_path": manifest["response"]["raw_path"],
                    "raw_sha256": manifest["response"]["sha256"],
                    "raw_bytes": manifest["response"]["bytes"],
                    "retrieved_at_utc": manifest["response"]["retrieved_at_utc"],
                    "http_status": manifest["response"]["http_status"],
                    "validation": validation,
                }
            )
            print(f"PASS {request_spec['request_id']}: {validation['date_count']} dates, {manifest['response']['sha256']}")
        except (DownloadError, ResponseValidationError) as error:
            results.append(
                {
                    "status": "failed",
                    "district_id": request_spec["district"]["district_id"],
                    "start": request_spec["start"],
                    "end": request_spec["end"],
                    "request_id": request_spec["request_id"],
                    "error": str(error),
                    "http_status": getattr(error, "status", None),
                }
            )
            print(f"FAIL {request_spec['request_id']}: {error}", file=sys.stderr)
        if index + 1 < len(requests):
            time.sleep(config["network_policy"]["inter_request_delay_seconds"])
    if scope == "smoke":
        summary = smoke_summary(config, results)
        atomic_write(smoke_manifest_path, (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    if any(result["status"] == "failed" for result in results):
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write-config", action="store_true")
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--scope", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--execute", action="store_true", help="perform network requests; otherwise print a dry run")
    parser.add_argument("--confirm-full-collection", action="store_true", help="required safeguard for full execution")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--smoke-manifest", type=Path, default=DEFAULT_SMOKE_MANIFEST)
    parser.add_argument("--reuse-decision", type=Path, default=DEFAULT_REUSE_DECISION)
    parser.add_argument("--write-reuse-decision", action="store_true")
    parser.add_argument("--write-full-plan", action="store_true", help="write the machine-readable full dry-run plan and current acquisition summary")
    parser.add_argument("--full-plan", type=Path, default=DEFAULT_FULL_PLAN)
    parser.add_argument("--full-summary", type=Path, default=DEFAULT_FULL_SUMMARY)
    args = parser.parse_args()

    if args.write_config:
        config = build_config()
        atomic_write(args.config, (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode())
        print(f"WROTE {args.config.relative_to(ROOT)} with 64 points and 1,600 configured full requests")
    config = load_config(args.config)
    if args.write_reuse_decision:
        decision = build_reuse_decision(args.config)
        atomic_write(args.reuse_decision, (json.dumps(decision, ensure_ascii=False, indent=2) + "\n").encode())
        print(f"WROTE {recorded_path(args.reuse_decision)} status={decision['status']}")
    decision = load_reuse_decision(args.reuse_decision, config, args.config)
    if args.check_config:
        expected = build_config()
        if config != expected:
            raise ConfigurationError("Checked-in configuration is not reproducible from the registry and pinned settings")
        print(f"PASS configuration: 64 points; registry SHA-256 {config['registry']['sha256']}; full requests 1,600")
    requests = build_requests(config, args.scope)
    if args.write_full_plan:
        if args.scope != "full":
            raise ConfigurationError("--write-full-plan requires --scope full")
        plan = build_full_plan(config, decision)
        summary = build_blocked_full_summary(config, plan, args.smoke_manifest)
        atomic_write(args.full_plan, (json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode())
        atomic_write(args.full_summary, (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode())
        print(
            f"WROTE {recorded_path(args.full_plan)} and {recorded_path(args.full_summary)}: "
            f"logical_requests={len(requests)} safe_reuses=0 status={plan['status']}"
        )
        if not args.execute:
            return
    if not args.execute:
        print(f"DRY RUN scope={args.scope} requests={len(requests)} concurrency=1 time_standard=LST")
        for request_spec in requests:
            print(f"{request_spec['request_id']} {request_spec['url']}")
        return
    if os.environ.get("OFFLINE") == "1":
        raise ConfigurationError("OFFLINE=1 blocks NASA POWER network acquisition")
    if args.scope == "full" and not args.confirm_full_collection:
        raise ConfigurationError("Full execution requires --confirm-full-collection")
    if args.scope == "full":
        require_full_execution_ready(decision)
    execute(config, args.scope, args.cache_dir, args.smoke_manifest)


if __name__ == "__main__":
    main()
