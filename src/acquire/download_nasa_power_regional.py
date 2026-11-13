#!/usr/bin/env python3
"""Plan, acquire and validate NASA POWER Daily Regional requests."""

import argparse
import csv
import gzip
import json
import math
import os
import random
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
from pathlib import Path

import download_nasa_power as point


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "data/climate/nasa_power_daily_regional_v1.json"
DEFAULT_REGISTRY = ROOT / "data/climate/district_sampling_registry.csv"
DEFAULT_REGISTRY_MANIFEST = ROOT / "data/climate/district_sampling_manifest.json"
DEFAULT_BOUNDARY = ROOT / "data/admin/bgd-adm2-source.geojson.gz"
DEFAULT_CACHE = ROOT / "cache/nasa_power_regional"
DEFAULT_SMOKE_MANIFEST = ROOT / "data/climate/nasa_power_regional_smoke_test_manifest.json"
DEFAULT_PREFLIGHT_MANIFEST = ROOT / "data/climate/nasa_power_regional_preflight_2001_manifest.json"

PARAMETERS = point.PARAMETERS
TRANSIENT_HTTP_STATUS = point.TRANSIENT_HTTP_STATUS
ConfigurationError = point.ConfigurationError
ResponseValidationError = point.ResponseValidationError
DownloadError = point.DownloadError
sha256 = point.sha256
canonical_json = point.canonical_json
atomic_write = point.atomic_write
recorded_path = point.recorded_path
expected_dates = point.expected_dates
retry_after_seconds = point.retry_after_seconds
utc_now = point.utc_now


def boundary_extent(path=DEFAULT_BOUNDARY):
    payload = json.loads(gzip.decompress(path.read_bytes()))
    longitudes = []
    latitudes = []

    def visit(value):
        if isinstance(value, list) and len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
            longitudes.append(float(value[0]))
            latitudes.append(float(value[1]))
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for feature in payload.get("features", []):
        visit(feature.get("geometry", {}).get("coordinates"))
    if not longitudes:
        raise ConfigurationError("Pinned boundary contains no coordinates")
    return {
        "longitude_min": min(longitudes),
        "latitude_min": min(latitudes),
        "longitude_max": max(longitudes),
        "latitude_max": max(latitudes),
    }


def build_config(
    registry_path=DEFAULT_REGISTRY,
    registry_manifest_path=DEFAULT_REGISTRY_MANIFEST,
    boundary_path=DEFAULT_BOUNDARY,
):
    registry_raw = registry_path.read_bytes()
    registry_manifest = json.loads(registry_manifest_path.read_text())
    registry_hash = sha256(registry_raw)
    if registry_hash != registry_manifest["registry_sha256"]:
        raise ConfigurationError("Registry checksum does not match its manifest")
    source_hash = sha256(gzip.decompress(boundary_path.read_bytes()))
    if source_hash != registry_manifest["boundary_source"]["uncompressed_sha256"]:
        raise ConfigurationError("Pinned boundary checksum does not match the sampling manifest")
    extent = boundary_extent(boundary_path)
    padding = {"latitude_degrees": 0.5, "longitude_degrees": 0.625}
    request_bbox = {
        "longitude_min": round(extent["longitude_min"] - padding["longitude_degrees"], 6),
        "latitude_min": round(extent["latitude_min"] - padding["latitude_degrees"], 6),
        "longitude_max": round(extent["longitude_max"] + padding["longitude_degrees"], 6),
        "latitude_max": round(extent["latitude_max"] + padding["latitude_degrees"], 6),
    }
    return {
        "schema_version": "1.0.0",
        "collection_id": "nasa-power-daily-regional-bgd-v1",
        "status": "regional_full_collection_authorized_step_3d",
        "accessed_on": "2026-11-13",
        "source": {
            "name": "NASA POWER Daily Regional API",
            "endpoint": "https://power.larc.nasa.gov/api/temporal/daily/regional",
            "community": "AG",
            "format": "JSON",
            "time_standard": "LST",
            "units_system": "metric",
            "openapi_version": "v2.10.3",
            "documentation_urls": [
                "https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
                "https://power.larc.nasa.gov/docs/services/api/temporal/",
                "https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/",
                "https://power.larc.nasa.gov/api/temporal/daily/openapi.json",
            ],
        },
        "registry": {
            "path": recorded_path(registry_path),
            "manifest_path": recorded_path(registry_manifest_path),
            "sha256": registry_hash,
            "row_count": 64,
            "identity_role": "Original district sampling coordinates remain unchanged extraction anchors.",
        },
        "boundary": {
            "path": recorded_path(boundary_path),
            "uncompressed_sha256": source_hash,
            "source_id": registry_manifest["boundary_source"]["id"],
            "source_version": registry_manifest["boundary_source"]["version"],
            "geometry_extent": extent,
            "edge_padding": {
                **padding,
                "basis": (
                    "One full officially documented meteorological spacing is added on every edge so an output "
                    "coordinate beyond each administrative edge can be requested without assuming grid origin or snapping."
                ),
            },
            "national_request_bbox": request_bbox,
        },
        "requested_coverage": {
            "start": "20010101",
            "end": "20251231",
            "parameters": PARAMETERS,
            "temporal": "daily",
            "fill_value": -999,
        },
        "regional_contract": {
            "one_parameter_per_request": True,
            "live_minimum_bbox_span_degrees": {
                "latitude": 2.0,
                "longitude": 2.0,
                "evidence": (
                    "A 2026-11-13 live 422 response rejected the initial 0.7 by 0.8 degree smoke box and required "
                    "at least a 2 degree range in both latitude and longitude; the raw error body is preserved."
                ),
            },
            "published_coordinate_ranges": {"latitude": [-90.0, 90.0], "longitude": [-180.0, 180.0]},
            "published_start_minimum": "19810101",
            "published_numeric_bbox_span_limit": None,
            "published_numeric_response_value_limit": None,
            "formats": ["ASCII", "CSV", "JSON", "NETCDF", "XARRAY"],
            "large_region_guidance": "The v2.10.3 OpenAPI description recommends NETCDF for large regions.",
            "usage_guidance": (
                "Avoid excessive synchronous requests and do not request more finely than current source resolution."
            ),
        },
        "full_proposal": {
            "region_partitioning": {
                "count": 1,
                "strategy": "one padded nationwide bounding box",
                "reason": (
                    "A single area avoids overlapping tile edges and undocumented grid snapping. The published "
                    "schema has no numeric maximum bbox span; annual national JSON succeeded in the preflight; full collection is separately authorized in Step 3D."
                ),
                "areas": [{"area_id": "bgd-padded-national", "bbox": request_bbox}],
            },
            "date_chunking": "calendar_year",
            "year_chunks": 25,
            "parameters_per_request": 1,
            "parameter_count": 4,
            "configured_request_count": 100,
            "execution_status": "authorized_by_saim_independent_of_g0_step_3d",
        },
        "smoke_test": {
            "area_id": "central-bangladesh-smoke",
            "bbox": {
                "longitude_min": 89.5,
                "latitude_min": 22.75,
                "longitude_max": 91.5,
                "latitude_max": 24.75,
            },
            "bbox_basis": (
                "The minimum 2 by 2 degree span required by a preserved live 422 response, positioned over central "
                "Bangladesh and containing the unchanged Dhaka registry point. It is an API/parser test area, not "
                "a new district sampling coordinate or national partition."
            ),
            "start": "20010101",
            "end": "20010103",
            "parameters": list(PARAMETERS),
            "successful_data_request_cap": 4,
            "multi_parameter_probe": (
                "Optional diagnostic runs first. A 422 rejection permits the four single-parameter requests; an "
                "unexpected 200 counts toward the cap and stops the smoke test before further data requests."
            ),
        },
        "network_policy": {
            "concurrency": 1,
            "inter_request_delay_seconds": 1.0,
            "timeout_seconds": 90.0,
            "max_attempts": 3,
            "backoff_initial_seconds": 2.0,
            "backoff_max_seconds": 60.0,
            "backoff_jitter_seconds": 0.5,
            "retry_http_status": sorted(TRANSIENT_HTTP_STATUS),
            "retry_after": "Honor Retry-After delta-seconds or HTTP-date when present.",
        },
        "storage": {
            "root": "cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1",
            "raw_layout": "raw/{area_id}/{parameter}/{start}_{end}.json",
            "request_manifest_layout": "raw/{area_id}/{parameter}/{start}_{end}.manifest.json",
            "error_layout": "errors/{area_id}/{request_id}.{attempt}.{timestamp}.{body|partial|json}",
            "raw_policy": "Preserve exact response bytes; atomically publish only structurally verified responses.",
        },
        "identity_and_extraction": {
            "adoption": "Saim explicitly adopted representative-point context on 2026-11-13; independent scientific review remains pending.",
            "identities": [
                "Original district sampling coordinates are unchanged WGS84 anchors from the Step 1 registry.",
                "Regional output coordinates are API-returned GeoJSON positions and are stored exactly as returned.",
                "Native source-grid identity is not assigned; returned nodes are not claimed to be unique native cells.",
            ],
            "proposed_method": (
                "After exact cross-parameter coordinate/date alignment, use the user-adopted nearest returned output coordinate "
                "to each original district point using great-circle distance; record both coordinates, distance and "
                "deterministic distance/latitude/longitude tie-breaking."
            ),
            "contract_change": (
                "Yes. This would replace a point-API request at each district anchor with nearest-returned-node "
                "extraction. The registry points remain unchanged, but the scientific sampling method requires review."
            ),
            "edge_rule": (
                "Use the padded area; expose actual distances without an invented cutoff. Fail if an adopted "
                "coordinate is absent in a later verified regional view. No district-area or field measurement is claimed."
            ),
        },
    }


def validate_config(config, config_path=None):
    if config["source"]["community"] != "AG" or config["source"]["time_standard"] != "LST":
        raise ConfigurationError("Regional requests must retain AG and explicit LST")
    if config["source"]["format"] != "JSON":
        raise ConfigurationError("The Step 3B parser is intentionally JSON-only")
    if set(config["requested_coverage"]["parameters"]) != set(PARAMETERS):
        raise ConfigurationError("Regional configuration must retain the approved four parameters")
    if config["full_proposal"]["configured_request_count"] != 100:
        raise ConfigurationError("Regional proposal must be 25 years x four one-parameter requests")
    if config["smoke_test"]["successful_data_request_cap"] != 4:
        raise ConfigurationError("Regional smoke success cap must remain four")
    if sha256(DEFAULT_REGISTRY.read_bytes()) != config["registry"]["sha256"]:
        raise ConfigurationError("Regional configuration registry checksum is stale")
    bbox = config["boundary"]["national_request_bbox"]
    extent = config["boundary"]["geometry_extent"]
    if not (
        bbox["longitude_min"] < extent["longitude_min"]
        and bbox["latitude_min"] < extent["latitude_min"]
        and bbox["longitude_max"] > extent["longitude_max"]
        and bbox["latitude_max"] > extent["latitude_max"]
    ):
        raise ConfigurationError("Padded national bbox does not cover the pinned boundary extent")
    return config


def load_config(path=DEFAULT_CONFIG):
    return validate_config(json.loads(path.read_text()), path)


def build_request(config, area_id, bbox, parameter_names, start, end, diagnostic=False):
    names = list(parameter_names)
    if not names or not set(names).issubset(PARAMETERS):
        raise ConfigurationError("Regional request contains an unsupported parameter")
    params = {
        "parameters": ",".join(names),
        "community": config["source"]["community"],
        "latitude-min": f"{bbox['latitude_min']:.6f}",
        "latitude-max": f"{bbox['latitude_max']:.6f}",
        "longitude-min": f"{bbox['longitude_min']:.6f}",
        "longitude-max": f"{bbox['longitude_max']:.6f}",
        "start": start,
        "end": end,
        "format": config["source"]["format"],
        "time-standard": config["source"]["time_standard"],
        "units": config["source"]["units_system"],
    }
    label = "multi-parameter-probe" if diagnostic else names[0]
    return {
        "request_id": f"{area_id}__{label}__{start}_{end}",
        "area_id": area_id,
        "bbox": bbox,
        "parameter_names": names,
        "parameter_label": label,
        "start": start,
        "end": end,
        "diagnostic": diagnostic,
        "parameters": params,
        "url": config["source"]["endpoint"] + "?" + urllib.parse.urlencode(params),
    }


def build_smoke_requests(config):
    smoke = config["smoke_test"]
    return [
        build_request(config, smoke["area_id"], smoke["bbox"], [name], smoke["start"], smoke["end"])
        for name in smoke["parameters"]
    ]


def build_multi_parameter_probe(config):
    smoke = config["smoke_test"]
    return build_request(
        config,
        smoke["area_id"],
        smoke["bbox"],
        smoke["parameters"],
        smoke["start"],
        smoke["end"],
        diagnostic=True,
    )


def build_preflight_request(config):
    """Build the single Step 3C request; this does not authorize any other full-scope request."""
    return build_request(
        config,
        "bgd-padded-national",
        config["boundary"]["national_request_bbox"],
        ["PRECTOTCORR"],
        "20010101",
        "20011231",
    )


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


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ResponseValidationError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_response_bytes(raw, request_spec, config):
    try:
        payload = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ResponseValidationError("Regional response is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection":
        detail = payload.get("messages") or payload.get("message") or payload.get("header") if isinstance(payload, dict) else None
        raise ResponseValidationError(f"POWER regional error or unexpected payload: {detail!r}")
    header = payload.get("header")
    if not isinstance(header, dict):
        raise ResponseValidationError("Regional response has no header")
    if str(header.get("start")) != request_spec["start"] or str(header.get("end")) != request_spec["end"]:
        raise ResponseValidationError("Regional response date range differs from request")
    if str(header.get("time_standard", "")).upper() != config["source"]["time_standard"]:
        raise ResponseValidationError("Regional response time standard is not explicit LST")
    if header.get("fill_value") != config["requested_coverage"]["fill_value"]:
        raise ResponseValidationError("Regional fill value is missing or unexpected")
    names = set(request_spec["parameter_names"])
    metadata = payload.get("parameters")
    if not isinstance(metadata, dict) or set(metadata) != names:
        raise ResponseValidationError(f"Unexpected regional parameter metadata: {sorted(metadata or {})}")
    for name in names:
        if not isinstance(metadata[name], dict):
            raise ResponseValidationError(f"Malformed regional metadata for {name}")
        if metadata[name].get("units") != PARAMETERS[name]["units"]:
            raise ResponseValidationError(f"Unexpected regional units for {name}: {metadata[name].get('units')!r}")
    dates = expected_dates(request_spec["start"], request_spec["end"])
    features = payload.get("features")
    if not isinstance(features, list) or not features:
        raise ResponseValidationError("Regional response contains no output features")
    coordinates = []
    fill_counts = {name: 0 for name in names}
    for feature in features:
        geometry = feature.get("geometry") if isinstance(feature, dict) else None
        coordinate = geometry.get("coordinates") if isinstance(geometry, dict) else None
        if not isinstance(geometry, dict) or geometry.get("type") != "Point" or not isinstance(coordinate, list) or len(coordinate) < 2:
            raise ResponseValidationError("Regional feature geometry is not a coordinate point")
        longitude, latitude = coordinate[:2]
        if type(longitude) not in (int, float) or type(latitude) not in (int, float):
            raise ResponseValidationError("Regional output coordinate is non-numeric")
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            raise ResponseValidationError("Regional output coordinate is out of WGS84 range")
        bbox = request_spec["bbox"]
        if not (
            bbox["longitude_min"] <= longitude <= bbox["longitude_max"]
            and bbox["latitude_min"] <= latitude <= bbox["latitude_max"]
        ):
            raise ResponseValidationError("Regional output coordinate lies outside the requested bbox")
        pair = [longitude, latitude]
        if pair in coordinates:
            raise ResponseValidationError("Regional response repeats an output coordinate")
        coordinates.append(pair)
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise ResponseValidationError("Regional feature properties are malformed")
        series = properties.get("parameter")
        if not isinstance(series, dict) or set(series) != names:
            raise ResponseValidationError("Regional feature parameter set is missing or unexpected")
        for name in names:
            values = series[name]
            if not isinstance(values, dict) or list(values) != dates:
                raise ResponseValidationError(f"Regional {name} dates are missing, duplicated, reordered or unexpected")
            if any(type(value) not in (int, float) or not math.isfinite(value) for value in values.values()):
                raise ResponseValidationError(f"Regional {name} contains a non-numeric value")
            fill_counts[name] += sum(value == header["fill_value"] for value in values.values())
    sorted_coordinates = sorted(coordinates)
    api = header.get("api") if isinstance(header.get("api"), dict) else {}
    return {
        "status": "valid",
        "actual_start": str(header["start"]),
        "actual_end": str(header["end"]),
        "date_count": len(dates),
        "parameter_names": sorted(names),
        "units": {name: metadata[name]["units"] for name in sorted(names)},
        "time_standard": str(header["time_standard"]).upper(),
        "fill_value": header["fill_value"],
        "fill_counts": fill_counts,
        "feature_count": len(features),
        "value_count": len(features) * len(dates) * len(names),
        "output_coordinates": coordinates,
        "coordinate_set_sha256": sha256(canonical_json(sorted_coordinates)),
        "output_coordinate_extent": {
            "longitude_min": min(item[0] for item in coordinates),
            "latitude_min": min(item[1] for item in coordinates),
            "longitude_max": max(item[0] for item in coordinates),
            "latitude_max": max(item[1] for item in coordinates),
        },
        "coordinate_identity_note": (
            "API-returned output coordinates only; not asserted to be unique native source-grid cell identifiers."
        ),
        "api": api,
        "sources": header.get("sources"),
        "title": header.get("title"),
    }


def default_opener(url, timeout):
    request = point.urllib.request.Request(url, headers={"User-Agent": "soil-to-stars-climate-regional-acquire/1.0"})
    return point.urllib.request.urlopen(request, timeout=timeout)


class RegionalDownloader:
    def __init__(
        self,
        config,
        cache_root=DEFAULT_CACHE,
        opener=default_opener,
        sleeper=time.sleep,
        random_source=random.random,
        now=utc_now,
        timer=time.monotonic,
    ):
        self.config = config
        self.cache_root = Path(cache_root) / config["collection_id"]
        self.opener = opener
        self.sleeper = sleeper
        self.random_source = random_source
        self.now = now
        self.timer = timer

    def paths(self, request_spec):
        base = self.cache_root / "raw" / request_spec["area_id"] / request_spec["parameter_label"]
        raw = base / f"{request_spec['start']}_{request_spec['end']}.json"
        return raw, raw.with_suffix(".manifest.json")

    def _error_dir(self, request_spec):
        return self.cache_root / "errors" / request_spec["area_id"]

    def _save_failure(self, request_spec, attempt, kind, body, details):
        timestamp = self.now().replace(":", "").replace("-", "")
        directory = self._error_dir(request_spec)
        directory.mkdir(parents=True, exist_ok=True)
        stem = f"{request_spec['request_id']}.attempt-{attempt}.{timestamp}"
        if body:
            atomic_write(directory / f"{stem}.{kind}", body)
        record = {
            "schema_version": "1.0.0",
            "status": "failed_attempt",
            "attempt": attempt,
            "kind": kind,
            "recorded_at_utc": self.now(),
            "request_id": request_spec["request_id"],
            "request": request_spec["parameters"],
            **details,
        }
        atomic_write(directory / f"{stem}.json", (json.dumps(record, indent=2, sort_keys=True) + "\n").encode())

    def _quarantine(self, request_spec, paths, reason):
        timestamp = self.now().replace(":", "").replace("-", "")
        directory = self._error_dir(request_spec)
        directory.mkdir(parents=True, exist_ok=True)
        for path in paths:
            if path.exists():
                shutil.move(str(path), directory / f"{request_spec['request_id']}.corrupt.{timestamp}.{path.name}")
        atomic_write(
            directory / f"{request_spec['request_id']}.corrupt.{timestamp}.json",
            (json.dumps({"status": "quarantined", "reason": reason, "recorded_at_utc": self.now()}, indent=2) + "\n").encode(),
        )

    def _cached(self, request_spec):
        raw_path, manifest_path = self.paths(request_spec)
        if not raw_path.exists() and not manifest_path.exists():
            return None
        try:
            manifest = json.loads(manifest_path.read_text())
            raw = raw_path.read_bytes()
            if manifest["request"]["url"] != request_spec["url"] or manifest["request"]["parameters"] != request_spec["parameters"]:
                raise ValueError("full request identity mismatch")
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

    def _stream_once(self, request_spec, attempt):
        raw_path, _ = self.paths(request_spec)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".partial-", dir=raw_path.parent)
        keep = False
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
                        raise DownloadError(
                            f"HTTP {status}", status=status, retry_after=headers.get("Retry-After"), body=body, headers=headers
                        )
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
                keep = True
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
                raise DownloadError(f"Network or interrupted regional download: {error}") from error
            except ResponseValidationError as error:
                body = Path(temporary).read_bytes() if Path(temporary).exists() else b""
                self._save_failure(request_spec, attempt, "body", body, {"error": str(error), "http_status": 200})
                raise
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if not keep and "temporary" in locals() and os.path.exists(temporary):
                os.unlink(temporary)

    def download(self, request_spec):
        cached = self._cached(request_spec)
        if cached:
            return cached
        policy = self.config["network_policy"]
        started = self.timer()
        for attempt in range(1, policy["max_attempts"] + 1):
            try:
                temporary, raw, headers, validation = self._stream_once(request_spec, attempt)
                raw_path, manifest_path = self.paths(request_spec)
                os.replace(temporary, raw_path)
                manifest = {
                    "schema_version": "1.0.0",
                    "collection_id": self.config["collection_id"],
                    "configuration_fingerprint": sha256(canonical_json(self.config)),
                    "registry_sha256": self.config["registry"]["sha256"],
                    "request_id": request_spec["request_id"],
                    "request_fingerprint": request_fingerprint(self.config, request_spec),
                    "area_id": request_spec["area_id"],
                    "bbox": request_spec["bbox"],
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
                        "elapsed_seconds": round(self.timer() - started, 6),
                        "headers": {
                            name: value
                            for name, value in headers.items()
                            if name.lower()
                            in {"content-type", "content-length", "content-disposition", "etag", "last-modified"}
                        },
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
                if retry_after is not None and delay > policy["backoff_max_seconds"]:
                    raise DownloadError(f"Paused: Retry-After {delay} seconds exceeds bounded wait; resume later", status=error.status) from error
                self.sleeper(delay)
        raise AssertionError("unreachable")


def preflight_qa(raw, request_spec, config, registry_path=DEFAULT_REGISTRY):
    validation = validate_response_bytes(raw, request_spec, config)
    payload = json.loads(raw)
    parameter = request_spec["parameter_names"][0]
    fill_value = validation["fill_value"]
    non_fill_values = []
    negative_non_fill_count = 0
    non_finite_count = 0
    boolean_value_count = 0
    locations_with_complete_dates = 0
    expected_date_count = len(expected_dates(request_spec["start"], request_spec["end"]))
    for feature in payload["features"]:
        values = list(feature["properties"]["parameter"][parameter].values())
        if len(values) == expected_date_count:
            locations_with_complete_dates += 1
        for value in values:
            if isinstance(value, bool):
                boolean_value_count += 1
                continue
            if value == fill_value:
                continue
            if not math.isfinite(value):
                non_finite_count += 1
                continue
            non_fill_values.append(value)
            if value < 0:
                negative_non_fill_count += 1

    returned_extent = validation["output_coordinate_extent"]
    rows = list(csv.DictReader(registry_path.read_text().splitlines()))
    sampling_extent = {
        "longitude_min": min(float(row["longitude"]) for row in rows),
        "latitude_min": min(float(row["latitude"]) for row in rows),
        "longitude_max": max(float(row["longitude"]) for row in rows),
        "latitude_max": max(float(row["latitude"]) for row in rows),
    }
    outside_sampling_points = [
        row["district_id"]
        for row in rows
        if not (
            returned_extent["longitude_min"] <= float(row["longitude"]) <= returned_extent["longitude_max"]
            and returned_extent["latitude_min"] <= float(row["latitude"]) <= returned_extent["latitude_max"]
        )
    ]
    boundary = config["boundary"]["geometry_extent"]
    requested = request_spec["bbox"]
    unique_coordinates = len({tuple(item) for item in validation["output_coordinates"]})
    return {
        "validation": validation,
        "coordinate_uniqueness": {
            "coordinate_count": validation["feature_count"],
            "unique_coordinate_count": unique_coordinates,
            "all_unique": validation["feature_count"] == unique_coordinates,
            "identity_note": "Returned output coordinates only; not native NASA cell identifiers.",
        },
        "date_coverage": {
            "expected_dates_per_location": expected_date_count,
            "locations_checked": validation["feature_count"],
            "locations_with_complete_ordered_dates": locations_with_complete_dates,
            "locations_incomplete": validation["feature_count"] - locations_with_complete_dates,
            "returned_values_expected": validation["feature_count"] * expected_date_count,
            "returned_values_actual": validation["value_count"],
        },
        "value_qa": {
            "parameter": parameter,
            "unit": validation["units"][parameter],
            "fill_value": fill_value,
            "fill_count": validation["fill_counts"][parameter],
            "non_fill_count": len(non_fill_values),
            "minimum_non_fill": min(non_fill_values) if non_fill_values else None,
            "maximum_non_fill": max(non_fill_values) if non_fill_values else None,
            "negative_non_fill_count": negative_non_fill_count,
            "non_finite_count": non_finite_count,
            "boolean_value_count": boolean_value_count,
            "values_corrected": False,
        },
        "spatial_coverage": {
            "request_bbox": requested,
            "returned_coordinate_extent": returned_extent,
            "pinned_boundary_extent": boundary,
            "district_sampling_coordinate_extent": sampling_extent,
            "district_sampling_points_checked": len(rows),
            "district_sampling_points_within_returned_extent": len(rows) - len(outside_sampling_points),
            "district_sampling_points_outside_returned_extent": outside_sampling_points,
            "all_district_sampling_points_within_returned_extent": not outside_sampling_points,
            "returned_extent_margin_beyond_boundary_degrees": {
                "west": boundary["longitude_min"] - returned_extent["longitude_min"],
                "east": returned_extent["longitude_max"] - boundary["longitude_max"],
                "south": boundary["latitude_min"] - returned_extent["latitude_min"],
                "north": returned_extent["latitude_max"] - boundary["latitude_max"],
            },
            "returned_extent_inset_from_request_bbox_degrees": {
                "west": returned_extent["longitude_min"] - requested["longitude_min"],
                "east": requested["longitude_max"] - returned_extent["longitude_max"],
                "south": returned_extent["latitude_min"] - requested["latitude_min"],
                "north": requested["latitude_max"] - returned_extent["latitude_max"],
            },
            "edge_note": (
                "Extent containment verifies raw regional coordinate coverage only. It does not select an output "
                "coordinate for a district or approve nearest-node extraction."
            ),
        },
    }


def preflight_summary(config, request_spec, manifest, qa):
    observed_bytes = manifest["response"]["bytes"]
    observed_seconds = manifest["response"].get("elapsed_seconds")
    proposed_requests = config["full_proposal"]["configured_request_count"]
    return {
        "schema_version": "1.0.0",
        "preflight_id": "nasa-power-regional-bgd-prectotcorr-2001-v1",
        "recorded_at_utc": utc_now(),
        "status": "preflight_complete",
        "format_decision": {
            "selected": "JSON",
            "reason": (
                "The existing dependency-free JSON parser preserves and validates Regional coordinates, dates and "
                "metadata. The official schema recommends NetCDF for large regions, but this one-year preflight "
                "measures whether national JSON is practical before adding a NetCDF dependency."
            ),
            "comparison_download_performed": False,
        },
        "configuration": {
            "path": recorded_path(DEFAULT_CONFIG),
            "sha256": sha256(DEFAULT_CONFIG.read_bytes()),
            "fingerprint": sha256(canonical_json(config)),
            "registry_sha256": config["registry"]["sha256"],
        },
        "request": {
            "request_id": request_spec["request_id"],
            "area_id": request_spec["area_id"],
            "bbox": request_spec["bbox"],
            "parameters": request_spec["parameters"],
            "url": request_spec["url"],
        },
        "raw_response": manifest["response"],
        "qa": qa,
        "practicality": {
            "assessment": "annual_national_json_request_succeeded",
            "observed_raw_bytes_for_one_parameter_year": observed_bytes,
            "observed_elapsed_seconds": observed_seconds,
            "proposed_full_request_count": proposed_requests,
            "simple_linear_raw_byte_estimate_for_100_requests": observed_bytes * proposed_requests,
            "simple_linear_elapsed_estimate_seconds_for_100_sequential_requests": (
                round(observed_seconds * proposed_requests, 6) if observed_seconds is not None else None
            ),
            "estimate_limitations": (
                "The 100-request figures are arithmetic extrapolations from one PRECTOTCORR year, not measured "
                "storage or duration. Other parameters, years, service load and compression may differ."
            ),
            "proposed_chunking": "one national area, one parameter, one calendar year per request",
            "execution": "sequential with existing bounded transient retries, Retry-After and checksum-aware resume",
            "format_recommendation": (
                "Retain JSON annual chunks unless later observed responses become impractical; do not change to "
                "NetCDF without a separately tested parser and provenance path."
            ),
        },
        "separation": {
            "raw_regional_coverage": "Validated for PRECTOTCORR over the padded national area in calendar year 2001.",
            "district_derived_coverage": "Not generated; extraction method and distance/edge policy remain unresolved.",
            "nearest_node_approved": False,
            "native_cell_identity_claimed": False,
        },
    }


def execute_preflight(config, cache_dir, preflight_manifest_path):
    request_spec = build_preflight_request(config)
    downloader = RegionalDownloader(config, cache_dir)
    manifest = downloader.download(request_spec)
    raw_path = ROOT / manifest["response"]["raw_path"]
    qa = preflight_qa(raw_path.read_bytes(), request_spec, config)
    summary = preflight_summary(config, request_spec, manifest, qa)
    atomic_write(preflight_manifest_path, (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    print(
        f"PASS preflight request={request_spec['request_id']} bytes={manifest['response']['bytes']} "
        f"elapsed={manifest['response'].get('elapsed_seconds')} features={qa['validation']['feature_count']} "
        f"dates={qa['validation']['date_count']} sha256={manifest['response']['sha256']}"
    )
    print(f"WROTE {recorded_path(preflight_manifest_path)}")


def validate_preflight_cache(config, cache_dir, preflight_manifest_path):
    request_spec = build_preflight_request(config)

    def network_forbidden(*_args, **_kwargs):
        raise AssertionError("Cached-response validation attempted network access")

    downloader = RegionalDownloader(config, cache_dir, opener=network_forbidden)
    manifest = downloader.download(request_spec)
    if manifest.get("resume_status") != "cached_verified":
        raise ConfigurationError("Preflight cache was not accepted as checksum-verified resume evidence")
    raw_path = ROOT / manifest["response"]["raw_path"]
    qa = preflight_qa(raw_path.read_bytes(), request_spec, config)
    recorded = json.loads(preflight_manifest_path.read_text())
    if recorded["raw_response"]["sha256"] != manifest["response"]["sha256"]:
        raise ConfigurationError("Checked-in preflight manifest raw checksum differs from cache")
    if recorded["qa"] != qa:
        raise ConfigurationError("Checked-in preflight QA differs from fresh cached-response validation")
    print(
        f"PASS cached preflight: no network; sha256={manifest['response']['sha256']} "
        f"bytes={manifest['response']['bytes']} features={qa['validation']['feature_count']} "
        f"dates={qa['validation']['date_count']}"
    )


def haversine_km(latitude_a, longitude_a, latitude_b, longitude_b):
    radius_km = 6371.0088
    lat_a = math.radians(latitude_a)
    lat_b = math.radians(latitude_b)
    delta_lat = lat_b - lat_a
    delta_lon = math.radians(longitude_b - longitude_a)
    value = math.sin(delta_lat / 2) ** 2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(value))


def smoke_alignment(config, manifests, registry_path=DEFAULT_REGISTRY):
    coordinate_sets = {
        item["validation"]["coordinate_set_sha256"] for item in manifests
    }
    coordinates_match = len(coordinate_sets) == 1
    dates_match = len({(item["validation"]["actual_start"], item["validation"]["actual_end"]) for item in manifests}) == 1
    output_coordinates = manifests[0]["validation"]["output_coordinates"] if coordinates_match else []
    bbox = config["smoke_test"]["bbox"]
    mappings = []
    if coordinates_match:
        for row in csv.DictReader(registry_path.read_text().splitlines()):
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])
            if not (
                bbox["longitude_min"] <= longitude <= bbox["longitude_max"]
                and bbox["latitude_min"] <= latitude <= bbox["latitude_max"]
            ):
                continue
            candidates = sorted(
                (
                    haversine_km(latitude, longitude, coordinate[1], coordinate[0]),
                    coordinate[1],
                    coordinate[0],
                )
                for coordinate in output_coordinates
            )
            distance, output_latitude, output_longitude = candidates[0]
            mappings.append(
                {
                    "district_id": row["district_id"],
                    "original_sampling_coordinate": {"latitude": latitude, "longitude": longitude},
                    "nearest_returned_output_coordinate": {
                        "latitude": output_latitude,
                        "longitude": output_longitude,
                    },
                    "great_circle_distance_km": round(distance, 6),
                    "tie_break": "distance, then returned latitude, then returned longitude",
                    "method_status": "diagnostic_only_not_adopted",
                }
            )
    return {
        "coordinate_sets_identical": coordinates_match,
        "date_sets_identical": dates_match,
        "combination_status": (
            "safe_to_join_by_exact_returned_coordinate_and_date_for_smoke_analysis_only"
            if coordinates_match and dates_match
            else "not_safe_to_combine"
        ),
        "native_grid_identity_claimed": False,
        "district_mapping_diagnostics": mappings,
    }


def smoke_summary(config, manifests, probe_result):
    results = []
    for manifest in manifests:
        results.append(
            {
                "request_id": manifest["request_id"],
                "status": manifest["acquisition_status"],
                "resume_status": manifest.get("resume_status"),
                "request": manifest["request"],
                "bbox": manifest["bbox"],
                "response": manifest["response"],
                "validation": manifest["validation"],
            }
        )
    alignment = smoke_alignment(config, manifests) if len(manifests) == 4 else None
    return {
        "schema_version": "1.0.0",
        "collection_id": config["collection_id"],
        "recorded_at_utc": utc_now(),
        "status": "smoke_complete" if len(manifests) == 4 else "smoke_incomplete",
        "scope": "One central Bangladesh bbox, three daily dates, four approved parameters, at most four successful responses.",
        "configuration_fingerprint": sha256(canonical_json(config)),
        "registry_sha256": config["registry"]["sha256"],
        "multi_parameter_probe": probe_result,
        "successful_data_requests": len(manifests),
        "results": results,
        "cross_parameter_alignment": alignment,
        "limitations": [
            "Returned output coordinates are not asserted to be unique native source-grid cell identifiers.",
            "Exact smoke coordinate alignment does not prove identical upstream spatial support or point-API equivalence.",
            "Nearest-output-node mapping is diagnostic only and changes the original point-request sampling method.",
            "The smoke test does not verify national extent, annual chunks or 2001-2025 completeness.",
        ],
    }


def execute_smoke(config, cache_dir, smoke_manifest_path, run_probe):
    downloader = RegionalDownloader(config, cache_dir)
    probe_result = {"status": "not_run"}
    if run_probe:
        probe = build_multi_parameter_probe(config)
        try:
            manifest = downloader.download(probe)
            probe_result = {
                "status": "unexpectedly_succeeded",
                "http_status": 200,
                "request_id": probe["request_id"],
                "raw_path": manifest["response"]["raw_path"],
                "raw_sha256": manifest["response"]["sha256"],
                "note": "Counts as one successful request; smoke stopped to preserve the four-success cap.",
            }
            summary = smoke_summary(config, [manifest], probe_result)
            atomic_write(smoke_manifest_path, (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
            raise SystemExit("Multi-parameter regional probe unexpectedly succeeded; stopped before single-parameter smoke requests")
        except DownloadError as error:
            try:
                error_payload = json.loads(error.body) if error.body else {}
            except (UnicodeDecodeError, json.JSONDecodeError):
                error_payload = {}
            probe_result = {
                "status": "rejected_as_documented" if error.status == 422 else "failed",
                "http_status": error.status,
                "request_id": probe["request_id"],
                "error": str(error),
                "response_body_sha256": sha256(error.body) if error.body else None,
                "messages": error_payload.get("messages"),
            }
            if error.status != 422:
                summary = smoke_summary(config, [], probe_result)
                atomic_write(smoke_manifest_path, (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
                raise
    manifests = []
    requests = build_smoke_requests(config)
    for index, request_spec in enumerate(requests):
        manifest = downloader.download(request_spec)
        manifests.append(manifest)
        print(
            f"PASS {request_spec['request_id']}: features={manifest['validation']['feature_count']} "
            f"dates={manifest['validation']['date_count']} sha256={manifest['response']['sha256']}"
        )
        if index + 1 < len(requests):
            time.sleep(config["network_policy"]["inter_request_delay_seconds"])
    summary = smoke_summary(config, manifests, probe_result)
    atomic_write(smoke_manifest_path, (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    print(f"WROTE {recorded_path(smoke_manifest_path)} successful_requests={len(manifests)}")


def build_full_requests(config):
    area = config["full_proposal"]["region_partitioning"]["areas"][0]
    return [build_request(config, area["area_id"], area["bbox"], [name], start, end)
            for start, end in point.year_chunks(config["requested_coverage"]["start"], config["requested_coverage"]["end"])
            for name in PARAMETERS]


def compact_annual_qa(qa):
    qa["validation"].pop("output_coordinates", None)
    return qa


def validate_full_cache(config, cache_dir, summary_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline collection validation attempted network")
    downloader = RegionalDownloader(config, cache_dir, opener=forbidden)
    summary = json.loads(summary_path.read_text())
    recorded = {item["request_id"]: item for item in summary["results"]}
    for spec in build_full_requests(config):
        manifest = downloader._cached(spec)
        if manifest is None or spec["request_id"] not in recorded:
            raise ConfigurationError(f"Incomplete/invalid full cache: {spec['request_id']}")
        raw_path, _ = downloader.paths(spec)
        recorded[spec["request_id"]]["annual_qa"] = compact_annual_qa(preflight_qa(raw_path.read_bytes(), spec, config))
        recorded[spec["request_id"]]["validation"].pop("output_coordinates", None)
    summary["offline_validation"] = dict(status="passed", requests=len(recorded), configuration_sha256=sha256(canonical_json(config)))
    atomic_write(summary_path, (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode())
    print(f"PASS offline full cache requests={len(recorded)}; acquisition counts/timing preserved")


def execute_full(config, cache_dir, summary_path):
    requests = build_full_requests(config)
    downloader = RegionalDownloader(config, cache_dir)
    started = time.monotonic()
    results = []
    failures = []
    def save():
        summary = {
            "collection_id": config["collection_id"], "recorded_at_utc": utc_now(),
            "configuration_sha256": sha256(canonical_json(config)),
            "status": "complete" if len(results) == len(requests) else "partial",
            "planned": len(requests), "complete": len(results), "failed": len(failures),
            "pending": len(requests) - len(results) - len(failures),
            "reused": sum(r.get("resume_status") == "cached_verified" for r in results),
            "bytes": sum(r["response"]["bytes"] for r in results),
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "coordinate_support_hashes": sorted({r["validation"]["coordinate_set_sha256"] for r in results}),
            "results": results, "failures": failures,
            "resume_command": "python3 src/acquire/download_nasa_power_regional.py --plan full --execute-full",
            "district_series_produced": False,
        }
        atomic_write(summary_path, (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode())
    save()
    for spec in requests:
        try:
            manifest = downloader.download(spec)
            raw_path, _ = downloader.paths(spec)
            manifest["annual_qa"] = compact_annual_qa(preflight_qa(raw_path.read_bytes(), spec, config))
            manifest["validation"].pop("output_coordinates", None)
            results.append(manifest)
            save()
            print(f"PASS {spec['request_id']} {manifest.get('resume_status', 'downloaded')} bytes={manifest['response']['bytes']}", flush=True)
            if manifest.get("resume_status") != "cached_verified":
                time.sleep(config["network_policy"]["inter_request_delay_seconds"])
        except (DownloadError, ResponseValidationError) as error:
            failures.append({"request_id": spec["request_id"], "error": str(error)})
            save()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write-config", action="store_true")
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--plan", choices=("smoke", "preflight", "full"), default="smoke")
    parser.add_argument("--validate-full-cache", action="store_true")
    parser.add_argument("--execute-full", action="store_true")
    parser.add_argument("--full-summary", type=Path, default=ROOT / "data/climate/nasa_power_regional_full_summary.json")
    parser.add_argument("--execute-smoke", action="store_true")
    parser.add_argument("--execute-preflight", action="store_true")
    parser.add_argument("--validate-preflight-cache", action="store_true")
    parser.add_argument("--probe-multi-parameter", action="store_true")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--smoke-manifest", type=Path, default=DEFAULT_SMOKE_MANIFEST)
    parser.add_argument("--preflight-manifest", type=Path, default=DEFAULT_PREFLIGHT_MANIFEST)
    args = parser.parse_args()

    if args.write_config:
        config = build_config()
        atomic_write(args.config, (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode())
        print(f"WROTE {recorded_path(args.config)} proposed_full_requests=100")
    config = load_config(args.config)
    if args.check_config:
        if config != build_config():
            raise ConfigurationError("Checked-in regional configuration is not reproducible")
        print(
            f"PASS regional configuration: registry={config['registry']['sha256']} "
            f"national_bbox={config['boundary']['national_request_bbox']}"
        )
    if args.validate_full_cache:
        validate_full_cache(config, args.cache_dir, args.full_summary)
        return
    if args.execute_full:
        if args.plan != "full" or os.environ.get("OFFLINE") == "1":
            raise ConfigurationError("Full execution requires --plan full and network enabled")
        execute_full(config, args.cache_dir, args.full_summary)
        return
    if args.execute_smoke:
        if os.environ.get("OFFLINE") == "1":
            raise ConfigurationError("OFFLINE=1 blocks NASA POWER regional acquisition")
        if args.plan != "smoke":
            raise ConfigurationError("Step 3B supports live execution only for --plan smoke")
        execute_smoke(config, args.cache_dir, args.smoke_manifest, args.probe_multi_parameter)
        return
    if args.execute_preflight:
        if os.environ.get("OFFLINE") == "1":
            raise ConfigurationError("OFFLINE=1 blocks NASA POWER regional acquisition")
        if args.plan != "preflight":
            raise ConfigurationError("--execute-preflight requires --plan preflight")
        execute_preflight(config, args.cache_dir, args.preflight_manifest)
        return
    if args.validate_preflight_cache:
        if args.plan != "preflight":
            raise ConfigurationError("--validate-preflight-cache requires --plan preflight")
        validate_preflight_cache(config, args.cache_dir, args.preflight_manifest)
        return
    if args.plan == "smoke":
        requests = build_smoke_requests(config)
        print(f"DRY RUN regional smoke requests={len(requests)} success_cap=4")
        if args.probe_multi_parameter:
            print(f"DIAGNOSTIC {build_multi_parameter_probe(config)['url']}")
        for request_spec in requests:
            print(f"{request_spec['request_id']} {request_spec['url']}")
    elif args.plan == "preflight":
        request_spec = build_preflight_request(config)
        print("DRY RUN regional preflight requests=1 format=JSON extraction=none")
        print(f"{request_spec['request_id']} {request_spec['url']}")
    else:
        proposal = config["full_proposal"]
        print(
            f"DRY RUN regional full proposal areas={proposal['region_partitioning']['count']} "
            f"years={proposal['year_chunks']} parameters={proposal['parameter_count']} "
            f"requests={len(build_full_requests(config))} execution=authorized_step_3d_via_execute_full"
        )


if __name__ == "__main__":
    main()
