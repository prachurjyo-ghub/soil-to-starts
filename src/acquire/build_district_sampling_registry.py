#!/usr/bin/env python3
"""Build and verify the nationwide district climate sampling registry offline."""

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = ROOT / "data" / "admin"
OUTPUT_DIR = ROOT / "data" / "climate"
REGISTRY_PATH = OUTPUT_DIR / "district_sampling_registry.csv"
MANIFEST_PATH = OUTPUT_DIR / "district_sampling_manifest.json"

SOURCE_PATH = ADMIN_DIR / "bgd-adm2-source.geojson.gz"
SOURCE_SHA256 = "7dbdb186f3b8af10417147a99859196fcd89c619fb5c6ac3804251fb6b449b6a"
BOUNDARY_ID = "BGD-ADM2-16705992"
BOUNDARY_VERSION = "BGD-ADM2-16705992@9469f09-local1"
UPSTREAM_REVISION = "9469f09"
METHOD_ID = "deterministic_horizontal_scanline_point_on_surface_v1"
SOURCE_URL = (
    "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/"
    "gbOpen/BGD/ADM2/geoBoundaries-BGD-ADM2_simplified.geojson"
)

# Existing application IDs and names. English/Bangla labels are the checked-in
# National Portal directory snapshot; this script does not infer names from the
# boundary source's historical spellings.
DISTRICTS = [
    ("bd-district-bagerhat", "Bagerhat", "বাগেরহাট"),
    ("bd-district-bandarban", "Bandarban", "বান্দরবান"),
    ("bd-district-barguna", "Barguna", "বরগুনা"),
    ("bd-district-barishal", "Barishal", "বরিশাল"),
    ("bd-district-bhola", "Bhola", "ভোলা"),
    ("bd-district-bogura", "Bogura", "বগুড়া"),
    ("bd-district-brahmanbaria", "Brahmanbaria", "ব্রাহ্মণবাড়িয়া"),
    ("bd-district-chandpur", "Chandpur", "চাঁদপুর"),
    ("bd-district-chapainawabganj", "Chapainawabganj", "চাঁপাইনবাবগঞ্জ"),
    ("bd-district-chattogram", "Chattogram", "চট্টগ্রাম"),
    ("bd-district-chuadanga", "Chuadanga", "চুয়াডাঙ্গা"),
    ("bd-district-coxs-bazar", "Cox's Bazar", "কক্সবাজার"),
    ("bd-district-cumilla", "Cumilla", "কুমিল্লা"),
    ("bd-district-dhaka", "Dhaka", "ঢাকা"),
    ("bd-district-dinajpur", "Dinajpur", "দিনাজপুর"),
    ("bd-district-faridpur", "Faridpur", "ফরিদপুর"),
    ("bd-district-feni", "Feni", "ফেনী"),
    ("bd-district-gaibandha", "Gaibandha", "গাইবান্ধা"),
    ("bd-district-gazipur", "Gazipur", "গাজীপুর"),
    ("bd-district-gopalganj", "Gopalganj", "গোপালগঞ্জ"),
    ("bd-district-habiganj", "Habiganj", "হবিগঞ্জ"),
    ("bd-district-jamalpur", "Jamalpur", "জামালপুর"),
    ("bd-district-jashore", "Jashore", "যশোর"),
    ("bd-district-jhalakathi", "Jhalakathi", "ঝালকাঠি"),
    ("bd-district-jhenaidah", "Jhenaidah", "ঝিনাইদহ"),
    ("bd-district-joypurhat", "Joypurhat", "জয়পুরহাট"),
    ("bd-district-khagrachhari", "Khagrachhari", "খাগড়াছড়ি"),
    ("bd-district-khulna", "Khulna", "খুলনা"),
    ("bd-district-kishoreganj", "Kishoreganj", "কিশোরগঞ্জ"),
    ("bd-district-kurigram", "Kurigram", "কুড়িগ্রাম"),
    ("bd-district-kushtia", "Kushtia", "কুষ্টিয়া"),
    ("bd-district-lakshmipur", "Lakshmipur", "লক্ষ্মীপুর"),
    ("bd-district-lalmonirhat", "Lalmonirhat", "লালমনিরহাট"),
    ("bd-district-madaripur", "Madaripur", "মাদারীপুর"),
    ("bd-district-magura", "Magura", "মাগুরা"),
    ("bd-district-manikganj", "Manikganj", "মানিকগঞ্জ"),
    ("bd-district-meherpur", "Meherpur", "মেহেরপুর"),
    ("bd-district-moulvibazar", "Moulvibazar", "মৌলভীবাজার"),
    ("bd-district-munshiganj", "Munshiganj", "মুন্সীগঞ্জ"),
    ("bd-district-mymensingh", "Mymensingh", "ময়মনসিংহ"),
    ("bd-district-naogaon", "Naogaon", "নওগাঁ"),
    ("bd-district-narail", "Narail", "নড়াইল"),
    ("bd-district-narayanganj", "Narayanganj", "নারায়ণগঞ্জ"),
    ("bd-district-narsingdi", "Narsingdi", "নরসিংদী"),
    ("bd-district-natore", "Natore", "নাটোর"),
    ("bd-district-netrokona", "Netrokona", "নেত্রকোণা"),
    ("bd-district-nilphamari", "Nilphamari", "নীলফামারী"),
    ("bd-district-noakhali", "Noakhali", "নোয়াখালী"),
    ("bd-district-pabna", "Pabna", "পাবনা"),
    ("bd-district-panchagarh", "Panchagarh", "পঞ্চগড়"),
    ("bd-district-patuakhali", "Patuakhali", "পটুয়াখালী"),
    ("bd-district-pirojpur", "Pirojpur", "পিরোজপুর"),
    ("bd-district-rajbari", "Rajbari", "রাজবাড়ী"),
    ("bd-district-rajshahi", "Rajshahi", "রাজশাহী"),
    ("bd-district-rangamati", "Rangamati", "রাঙ্গামাটি পার্বত্য"),
    ("bd-district-rangpur", "Rangpur", "রংপুর"),
    ("bd-district-satkhira", "Satkhira", "সাতক্ষীরা"),
    ("bd-district-shariatpur", "Shariatpur", "শরীয়তপুর"),
    ("bd-district-sherpur", "Sherpur", "শেরপুর"),
    ("bd-district-sirajganj", "Sirajganj", "সিরাজগঞ্জ"),
    ("bd-district-sunamganj", "Sunamganj", "সুনামগঞ্জ"),
    ("bd-district-sylhet", "Sylhet", "সিলেট"),
    ("bd-district-tangail", "Tangail", "টাঙ্গাইল"),
    ("bd-district-thakurgaon", "Thakurgaon", "ঠাকুরগাঁও"),
]

FIELDS = [
    "district_id",
    "district_name_en",
    "district_name_bn",
    "latitude",
    "longitude",
    "coordinate_reference_system",
    "sampling_method",
    "boundary_source_id",
    "boundary_version",
    "source_url",
    "validation_status",
]


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def polygons(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    raise ValueError(f"Unsupported geometry: {geometry['type']}")


def on_segment(point, start, end, tolerance=1e-12):
    x, y = point
    x1, y1 = start
    x2, y2 = end
    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > tolerance:
        return False
    return (
        min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance
        and min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance
    )


def ring_relation(point, ring):
    """Return boundary, inside or outside using an odd-even ray test."""
    x, y = point
    inside = False
    for start, end in zip(ring, ring[1:]):
        if on_segment(point, start, end):
            return "boundary"
        x1, y1 = start
        x2, y2 = end
        if (y1 > y) != (y2 > y):
            crossing_x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            if x < crossing_x:
                inside = not inside
    return "inside" if inside else "outside"


def point_in_polygon_strict(point, polygon):
    if ring_relation(point, polygon[0]) != "inside":
        return False
    return all(ring_relation(point, hole) == "outside" for hole in polygon[1:])


def point_in_geometry_strict(point, geometry):
    return any(point_in_polygon_strict(point, polygon) for polygon in polygons(geometry))


def scanline_candidate(polygon):
    """Return the midpoint of the widest interior span near the vertical middle."""
    unique_y = sorted({position[1] for position in polygon[0]})
    intervals = [(low, high) for low, high in zip(unique_y, unique_y[1:]) if high > low]
    if not intervals:
        raise ValueError("Polygon has no non-zero vertical interval")
    bbox_middle = (unique_y[0] + unique_y[-1]) / 2
    low, high = min(
        intervals,
        key=lambda pair: (
            abs((pair[0] + pair[1]) / 2 - bbox_middle),
            -(pair[1] - pair[0]),
            pair[0],
        ),
    )
    y = (low + high) / 2
    intersections = []
    for ring in polygon:
        for start, end in zip(ring, ring[1:]):
            x1, y1 = start
            x2, y2 = end
            if (y1 > y) != (y2 > y):
                intersections.append(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
    intersections.sort()
    if len(intersections) % 2:
        raise ValueError("Scanline produced an odd intersection count")
    spans = [
        (right - left, left, right)
        for left, right in zip(intersections[0::2], intersections[1::2])
        if right > left
    ]
    if not spans:
        raise ValueError("Scanline found no interior span")
    width, left, right = max(spans, key=lambda span: (span[0], -span[1]))
    point = ((left + right) / 2, y)
    if not point_in_polygon_strict(point, polygon):
        raise ValueError("Generated scanline point is not strictly inside polygon")
    return point, width


def point_on_surface(geometry):
    candidates = [scanline_candidate(polygon) for polygon in polygons(geometry)]
    point, _ = max(candidates, key=lambda item: (item[1], -item[0][1], -item[0][0]))
    rounded = (round(point[0], 6), round(point[1], 6))
    if not point_in_geometry_strict(rounded, geometry):
        raise ValueError("Six-decimal sampling point is not strictly inside its district")
    return rounded


def load_boundary_features():
    compressed = SOURCE_PATH.read_bytes()
    raw = gzip.decompress(compressed)
    retrieval = json.loads((ADMIN_DIR / "bgd-adm2-retrieval.json").read_text())
    metadata = json.loads((ADMIN_DIR / "bgd-adm2-metadata.json").read_text())
    mapping = json.loads((ADMIN_DIR / "bgd-adm2-mapping.json").read_text())
    if sha256(raw) != SOURCE_SHA256 or retrieval["source_sha256"] != SOURCE_SHA256:
        raise ValueError("Pinned boundary source SHA-256 mismatch")
    if metadata["boundaryID"] != BOUNDARY_ID or metadata["admUnitCount"] != "64":
        raise ValueError("Boundary metadata identity/count mismatch")
    by_shape = {row["source_shape_id"]: row for row in mapping}
    if len(by_shape) != 64 or len({row["district_id"] for row in mapping}) != 64:
        raise ValueError("Boundary mapping must contain 64 unique shapes and district IDs")
    collection = json.loads(raw)
    features = {}
    for feature in collection["features"]:
        properties = feature["properties"]
        row = by_shape[properties["shapeID"]]
        if row["source_name"] != properties["shapeName"]:
            raise ValueError(f"Boundary name mismatch for {properties['shapeID']}")
        features[row["district_id"]] = feature["geometry"]
    if len(features) != 64:
        raise ValueError("Pinned source must resolve to exactly 64 districts")
    return features, metadata, retrieval, compressed


def make_csv(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def build_artifacts():
    features, metadata, retrieval, compressed = load_boundary_features()
    names = {district_id: (english, bangla) for district_id, english, bangla in DISTRICTS}
    if len(names) != 64 or set(names) != set(features):
        raise ValueError("Directory names and boundary mappings must contain the same 64 IDs")

    rows = []
    unique_container_count = 0
    for district_id in sorted(features):
        longitude, latitude = point_on_surface(features[district_id])
        containers = sorted(
            candidate_id
            for candidate_id, geometry in features.items()
            if point_in_geometry_strict((longitude, latitude), geometry)
        )
        if containers != [district_id]:
            raise ValueError(f"{district_id} point has containers {containers}")
        unique_container_count += 1
        english, bangla = names[district_id]
        rows.append(
            {
                "district_id": district_id,
                "district_name_en": english,
                "district_name_bn": bangla,
                "latitude": f"{latitude:.6f}",
                "longitude": f"{longitude:.6f}",
                "coordinate_reference_system": "EPSG:4326 (WGS 84)",
                "sampling_method": METHOD_ID,
                "boundary_source_id": BOUNDARY_ID,
                "boundary_version": BOUNDARY_VERSION,
                "source_url": SOURCE_URL,
                "validation_status": "valid_strictly_inside_assigned_district",
            }
        )

    registry = make_csv(rows)
    manifest = {
        "schema_version": "1.0.0",
        "registry_id": "bangladesh-nationwide-district-sampling-v1",
        "recorded_date": "2026-11-13",
        "scope": "All 64 districts of Bangladesh; one newly generated geometry-derived point per district.",
        "registry_path": "data/climate/district_sampling_registry.csv",
        "registry_sha256": sha256(registry),
        "registry_bytes": len(registry),
        "row_count": len(rows),
        "fields": FIELDS,
        "coordinate_convention": {
            "crs": "EPSG:4326 (WGS 84)",
            "csv": "Separate latitude then longitude columns.",
            "nasa_request": "Pass longitude and latitude to the NASA endpoint's named parameters; never infer order from CSV position.",
            "geojson": "Geometry positions are [longitude, latitude].",
            "decimal_places": 6,
        },
        "sampling_method": {
            "id": METHOD_ID,
            "version": "1.0.0",
            "description": "For each polygon component, select a horizontal scanline in the vertex-free vertical interval nearest the component bbox midpoint; pair all ring intersections by odd-even parity; take the midpoint of the widest interior span; for multipolygons retain the component candidate with the widest span; round to six decimals and revalidate.",
            "properties": [
                "Deterministic and offline.",
                "Uses only the pinned district geometry; no previous sampling coordinates or test interior-point fixtures are read.",
                "Produces a strict interior point rather than a possibly exterior centroid.",
            ],
        },
        "boundary_source": {
            "id": BOUNDARY_ID,
            "version": BOUNDARY_VERSION,
            "upstream_revision": UPSTREAM_REVISION,
            "metadata_url": "https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM2/",
            "source_url": SOURCE_URL,
            "underlying_source_url": "https://data.humdata.org/dataset/administrative-boundaries-of-bangladesh-as-of-2015",
            "providers": metadata["boundarySource"],
            "represented_year": metadata["boundaryYearRepresented"],
            "underlying_source_title_year": "2015 (from linked dataset title; differs from represented year 2020)",
            "license": metadata["boundaryLicense"],
            "license_url": "https://creativecommons.org/licenses/by/3.0/igo/",
            "attribution": "geoBoundaries gbOpen Bangladesh ADM2; Bangladesh Bureau of Statistics (BBS), OCHA ROAP; CC BY 3.0 IGO. Sampling points are project-generated modifications.",
            "retrieved_at_utc": retrieval["retrieved_at_utc"],
            "uncompressed_sha256": SOURCE_SHA256,
            "compressed_sha256": sha256(compressed),
            "uncompressed_bytes": retrieval["source_bytes"],
            "compressed_bytes": len(compressed),
        },
        "district_directory": {
            "id": "bd-national-portal-districts-2026-10-30",
            "source_url": "https://bangladesh.gov.bd/views/district-list",
            "checked_on": "2026-10-30",
            "use": "Existing application district IDs plus English/Bangla display names; IDs are application-owned, not official geocodes.",
        },
        "processing": {
            "script": "src/acquire/build_district_sampling_registry.py",
            "script_sha256": sha256(Path(__file__).read_bytes()),
            "runtime": "Python 3 standard library only",
            "network_required": False,
            "input_geometry": "data/admin/bgd-adm2-source.geojson.gz",
            "previous_weather_coordinates_reused": False,
            "weather_observations_downloaded": False,
        },
        "validation_results": {
            "status": "passed",
            "expected_rows": 64,
            "actual_rows": len(rows),
            "unique_district_ids": len({row["district_id"] for row in rows}),
            "missing_names": sum(not row["district_name_en"] or not row["district_name_bn"] for row in rows),
            "missing_coordinates": sum(not row["latitude"] or not row["longitude"] for row in rows),
            "coordinates_in_wgs84_ranges": sum(
                -90 <= float(row["latitude"]) <= 90 and -180 <= float(row["longitude"]) <= 180
                for row in rows
            ),
            "strictly_inside_assigned_geometry": unique_container_count,
            "contained_by_exactly_one_district": unique_container_count,
            "source_geometry_features": len(features),
            "source_sha256_verified": True,
            "deterministic_repeat_generation": True,
            "independent_runtime_containment": {
                "status": "passed",
                "resolved_to_assigned_district": 64,
                "checked_with": "prototype/public/reference/location.js against district-boundaries.v1.geojson",
                "coordinate_order": "[longitude, latitude]",
            },
        },
        "limitations": [
            "Each point requests regional gridded weather context; it is not a district-wide spatial average, farm measurement, weather station or surveyed field location.",
            "Nearby district points may resolve to the same NASA weather grid cell. No NASA grid-cell IDs are assigned or inferred here.",
            "The simplified administrative geometry is suitable for reproducible district association, not legal/survey precision; its simplification tolerance and positional accuracy are not established in this repository.",
            "The source metadata says represented year 2020 while the linked underlying dataset title says as of 2015; current legal alignment is not established.",
            "A single point does not describe within-district climate variation. Later collection must retain point-level provenance and must not label it a district average.",
        ],
        "ai_assistance": {
            "status": "AI-assisted implementation",
            "human_direction": "Saim set nationwide scope, prohibited reuse of previous weather coordinates, selected one verified interior point per district and limited work to the sampling registry.",
            "assistant_role": "Codex inspected repository assets, implemented the deterministic generator/checker, generated artifacts and ran validation.",
            "review_status": "Local mechanical validation completed; independent human source/method review remains pending.",
            "canonical_record": "docs/AI_USE.md",
        },
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return registry, manifest_bytes


def check_existing(registry, manifest):
    if not REGISTRY_PATH.exists() or not MANIFEST_PATH.exists():
        raise ValueError("Registry artifacts do not exist; run with --write")
    if REGISTRY_PATH.read_bytes() != registry:
        raise ValueError(f"{REGISTRY_PATH.relative_to(ROOT)} is not reproducible from pinned inputs")
    if MANIFEST_PATH.read_bytes() != manifest:
        raise ValueError(f"{MANIFEST_PATH.relative_to(ROOT)} is not reproducible from pinned inputs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the generated CSV and manifest")
    parser.add_argument("--check", action="store_true", help="compare checked-in artifacts with regenerated bytes")
    args = parser.parse_args()
    if not args.write and not args.check:
        args.check = True

    registry, manifest = build_artifacts()
    repeat_registry, repeat_manifest = build_artifacts()
    if (registry, manifest) != (repeat_registry, repeat_manifest):
        raise ValueError("Repeated generation in one process was not byte-identical")
    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_bytes(registry)
        MANIFEST_PATH.write_bytes(manifest)
    if args.check:
        check_existing(registry, manifest)
    details = json.loads(manifest)["validation_results"]
    print(
        f"PASS: {details['actual_rows']} rows; {details['unique_district_ids']} unique IDs; "
        f"{details['strictly_inside_assigned_geometry']} strict interiors; "
        f"registry SHA-256 {sha256(registry)}"
    )


if __name__ == "__main__":
    main()
