#!/usr/bin/env python3
"""Plan and smoke-test NASA POWER Daily Regional requests without full acquisition."""

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
        "status": "regional_smoke_configuration",
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
                    "schema has no numeric maximum bbox span; live full-period suitability remains unverified."
                ),
                "areas": [{"area_id": "bgd-padded-national", "bbox": request_bbox}],
            },
            "date_chunking": "calendar_year",
            "year_chunks": 25,
            "parameters_per_request": 1,
            "parameter_count": 4,
            "configured_request_count": 100,
            "execution_status": "proposal_only_full_collection_not_authorized_in_step_3b",
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
            "identities": [
                "Original district sampling coordinates are unchanged WGS84 anchors from the Step 1 registry.",
                "Regional output coordinates are API-returned GeoJSON positions and are stored exactly as returned.",
                "Native source-grid identity is not assigned; returned nodes are not claimed to be unique native cells.",
            ],
            "proposed_method": (
                "After exact cross-parameter coordinate/date alignment, choose the nearest returned output coordinate "
                "to each original district point using great-circle distance; record both coordinates, distance and "
                "deterministic distance/latitude/longitude tie-breaking."
            ),
            "contract_change": (
                "Yes. This would replace a point-API request at each district anchor with nearest-returned-node "
                "extraction. The registry points remain unchanged, but the scientific sampling method requires review."
            ),
            "edge_rule": (
                "Use the padded national request area and reject extraction if no returned coordinate surrounds or "
                "is acceptably near a district anchor; no acceptable-distance threshold is invented in Step 3B."
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
        if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
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
        series = feature.get("properties", {}).get("parameter")
        if not isinstance(series, dict) or set(series) != names:
            raise ResponseValidationError("Regional feature parameter set is missing or unexpected")
        for name in names:
            values = series[name]
            if not isinstance(values, dict) or list(values) != dates:
                raise ResponseValidationError(f"Regional {name} dates are missing, duplicated, reordered or unexpected")
            if any(not isinstance(value, (int, float)) for value in values.values()):
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
    ):
        self.config = config
        self.cache_root = Path(cache_root) / config["collection_id"]
        self.opener = opener
        self.sleeper = sleeper
        self.random_source = random_source
        self.now = now

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write-config", action="store_true")
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--plan", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--execute-smoke", action="store_true")
    parser.add_argument("--probe-multi-parameter", action="store_true")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--smoke-manifest", type=Path, default=DEFAULT_SMOKE_MANIFEST)
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
    if args.execute_smoke:
        if os.environ.get("OFFLINE") == "1":
            raise ConfigurationError("OFFLINE=1 blocks NASA POWER regional acquisition")
        if args.plan != "smoke":
            raise ConfigurationError("Step 3B supports live execution only for --plan smoke")
        execute_smoke(config, args.cache_dir, args.smoke_manifest, args.probe_multi_parameter)
        return
    if args.plan == "smoke":
        requests = build_smoke_requests(config)
        print(f"DRY RUN regional smoke requests={len(requests)} success_cap=4")
        if args.probe_multi_parameter:
            print(f"DIAGNOSTIC {build_multi_parameter_probe(config)['url']}")
        for request_spec in requests:
            print(f"{request_spec['request_id']} {request_spec['url']}")
    else:
        proposal = config["full_proposal"]
        print(
            f"DRY RUN regional full proposal areas={proposal['region_partitioning']['count']} "
            f"years={proposal['year_chunks']} parameters={proposal['parameter_count']} "
            f"requests={proposal['configured_request_count']} execution={proposal['execution_status']}"
        )


if __name__ == "__main__":
    main()
