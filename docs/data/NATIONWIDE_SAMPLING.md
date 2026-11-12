# Nationwide district sampling registry

## Scope and status

Step 1 establishes one reproducible interior sampling point for each of all 64
Bangladesh districts. It does not download NASA or other weather observations,
calculate climate indicators, change the frontend, or establish scientific
coverage. This work is independent preparation under `CLIMATE-SAMPLING`; it
does not accept or advance G0.

The generated artifacts are:

- `data/climate/district_sampling_registry.csv`: 64 data rows with stable
  application district IDs, English/Bangla names, WGS84 coordinates, method,
  boundary provenance and row validation status.
- `data/climate/district_sampling_manifest.json`: pinned input identity,
  checksums, processing/version details, validation results, limitations and
  AI-assistance disclosure.
- `src/acquire/build_district_sampling_registry.py`: standard-library-only
  offline generator and checker.

## Administrative source and reuse decision

The registry reuses the repository's existing geoBoundaries gbOpen Bangladesh
ADM2 snapshot because it already has an explicit 64-row shape-ID mapping to the
application's district IDs and a verified source checksum. It does not reuse
`tests/fixtures/district-interior-points.json` or any earlier weather sampling
coordinate.

- Boundary ID: `BGD-ADM2-16705992`
- Local version: `BGD-ADM2-16705992@9469f09-local1`
- Pinned upstream revision: `9469f09`
- Source geometry: `data/admin/bgd-adm2-source.geojson.gz`
- Uncompressed source SHA-256:
  `7dbdb186f3b8af10417147a99859196fcd89c619fb5c6ac3804251fb6b449b6a`
- Metadata: <https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM2/>
- Pinned simplified geometry: <https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/BGD/ADM2/geoBoundaries-BGD-ADM2_simplified.geojson>
- Named providers: Bangladesh Bureau of Statistics (BBS), OCHA ROAP
- Declared represented year: 2020
- Linked underlying source: <https://data.humdata.org/dataset/administrative-boundaries-of-bangladesh-as-of-2015>
- License: [CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/)

The metadata's represented year (2020) conflicts with the linked underlying
dataset title (“as of 2015”). Both are retained. The repository has not
established current legal alignment, survey accuracy, positional accuracy or
the simplified geometry's tolerance. This asset is therefore administrative
reference geometry, not a cadastral or field boundary.

CC BY 3.0 IGO permits sharing and adaptation with appropriate credit, a license
link and an indication of changes. The manifest credits geoBoundaries, BBS and
OCHA ROAP and identifies the project-generated points as modifications. No
endorsement is implied.

District IDs and English/Bangla labels reuse the checked-in National Portal
directory snapshot `bd-national-portal-districts-2026-10-30`. The IDs are
application-owned stable identifiers, not official geocodes. The boundary's
historical English spellings remain mapped through
`data/admin/bgd-adm2-mapping.json` rather than fuzzy name matching.

## Sampling method

Method `deterministic_horizontal_scanline_point_on_surface_v1` derives each
coordinate anew from the pinned geometry:

1. For each polygon component, find the vertex-free vertical interval nearest
   the component bounding box's vertical midpoint.
2. Intersect a horizontal scanline through that interval with every exterior
   and hole ring, using odd-even parity to obtain interior spans.
3. Select the midpoint of the widest interior span. For a multipolygon, retain
   the component candidate with the widest span using stable tie-breaking.
4. Round longitude and latitude to six decimal places.
5. Recheck the rounded point for strict containment in its assigned district
   and require that it is contained by exactly one of the 64 district features.

This point-on-surface construction avoids the known centroid failure mode in
concave or multipart districts: an exterior centroid is never accepted. A
missing or invalid source geometry raises an error and stops generation instead
of inventing a coordinate.

## Coordinate order

Coordinates use WGS 84 (`EPSG:4326`). The CSV intentionally has separate
`latitude` and `longitude` columns in that order. GeoJSON positions and the
containment implementation use `[longitude, latitude]`. A NASA request must map
the named longitude and latitude parameters explicitly; callers must not infer
NASA parameter order from CSV column order.

## Reproduction and validation

From the repository root:

```bash
python3 src/acquire/build_district_sampling_registry.py --check
```

Intentional regeneration uses:

```bash
python3 src/acquire/build_district_sampling_registry.py --write --check
```

The checker verifies the source SHA-256, exact 64-shape mapping, directory ID
set, required names and coordinates, WGS84 ranges, strict point-in-polygon
containment, unique containing district and byte-for-byte regeneration. It
runs twice in one process and requires identical output. No network or
third-party Python package is required.

Results recorded on 13 November 2026:

- 64 rows and 64 unique district IDs: passed.
- Missing English/Bangla names: 0.
- Missing coordinates: 0.
- Coordinates within WGS84 ranges: 64/64.
- Strictly inside assigned pinned geometry: 64/64.
- Contained by exactly one district: 64/64.
- Independent check with the existing JavaScript runtime containment against
  `district-boundaries.v1.geojson`: 64/64 resolved to the assigned district.
- Deterministic repeated generation and checked-in byte comparison: passed.
- Registry SHA-256:
  `0b31748796de714f73de135ee3e0ec77c2e44813985d790b44f2d62e18c62dfa`.

## Interpretation and unresolved issues

One point samples regional gridded weather context. It is not a district-wide
spatial average, farm measurement, weather station or surveyed field location.
Nearby district points may fall in the same NASA weather grid cell. This step
does not assign or infer NASA grid-cell IDs.

Within-district climate variation remains unresolved by the one-point initial
design. Boundary vintage and positional limitations also remain unresolved.
Independent human review of the source choice and sampling method is pending.
Any later nationwide weather collection must preserve point-level provenance,
NASA product/version/units/time standard/missing-value handling and retrieval
checksums, and must continue to describe the values as point/grid context.

## AI-assisted work

Saim set the nationwide scope, prohibited reuse of previous weather coordinates,
selected one verified interior point per district and limited this delivery to
the registry. Codex inspected the existing assets, implemented the deterministic
generator/checker, generated the artifacts and ran the local validations. The
canonical contribution entry is in `docs/AI_USE.md`; AI assistance is not an
independent scientific or source approval.
