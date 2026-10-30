# Bangladesh district boundary snapshot

Administrative location context only. No farm coordinates, crop rules, NASA observations or advice coverage are supplied by this dataset.

- Dataset: **geoBoundaries gbOpen BGD ADM2**, boundary ID `BGD-ADM2-16705992`, pinned upstream revision `9469f09`.
- Provider metadata: [geoBoundaries API](https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM2/). Metadata names Bangladesh Bureau of Statistics (BBS) and OCHA ROAP as sources and declares **CC BY 3.0 IGO**. Retain [license attribution](https://creativecommons.org/licenses/by/3.0/igo/) and indicate modifications. No endorsement is implied.
- Represented year is **2020 according to metadata**; its underlying source URL says “as of 2015.” This discrepancy is preserved. Current legal/survey alignment and positional accuracy are not established.
- `bgd-adm2-source.geojson.gz` losslessly stores the downloaded upstream simplified GeoJSON. Its uncompressed bytes must match the Git LFS SHA-256 recorded in `bgd-adm2-retrieval.json`. The LFS pointer was inspected, then actual data downloaded from GitHub's media endpoint and verified; a pointer is not geometry.
- `bgd-adm2-metadata.json` preserves the metadata response values. `bgd-adm2-retrieval.json` records the actual source-file retrieval timestamp, bytes and checksum.
- `bgd-adm2-mapping.json` is an explicit 64-row mapping by **source shape ID and exact source name** to existing application district IDs. No runtime name or nearest-neighbor matching is performed.

Reviewed spelling aliases:

| Source shape name | Directory display name |
| --- | --- |
| Barisal | Barishal |
| Bogra | Bogura |
| Brahamanbaria | Brahmanbaria |
| Chittagong | Chattogram |
| Comilla | Cumilla |
| Jessore | Jashore |
| Jhalokati | Jhalakathi |
| Maulvibazar | Moulvibazar |
| Nawabganj | Chapainawabganj |
| Netrakona | Netrokona |

Rebuild offline from repository root:

```bash
python3 scripts/prepare_district_boundaries.py
```

The script verifies source identity, uses the exact mapping ledger, preserves all geometry coordinates/rings, adds bounding boxes and application IDs, sorts features and minifies JSON. It performs **no further simplification or coordinate rounding**. The browser manifest records processing and output checksum. The same output is used for display and containment; no incompatible country mask is applied. The output has 47 Polygons, 17 MultiPolygons, 377 rings and 38,112 vertices. Dataset simplification tolerance is not established here; this is not survey geometry.

`tests/fixtures/district-interior-points.json` contains 64 geometric test interiors derived independently from source polygons with a Python ring-parity/grid sampler. These are test fixtures, not observed farms, official city points or defaults for intake. They retain source shape IDs/version and are subject to the same attribution.
