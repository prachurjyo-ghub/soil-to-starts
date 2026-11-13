# Teammate climate-data setup — package v1.0.0

**Current delivery:** the archive is now included in Git on `main2`. Use
`python3 scripts/setup_climate_data.py` after cloning/pulling; no manual folder
transfer is needed. See [current GitHub setup](CLIMATE_GITHUB_SETUP.md). The
local handoff instructions below preserve the earlier package workflow.

Obtain these local delivery files from Saim; no upload/share service is configured:

- `cache/climate_handoff/soil-to-stars-climate-bgd-v1.0.0.tar.gz`
- Its `.tar.gz.sha256` sidecar and the trusted producer receipt
  `data/climate/climate_data_package_v1_receipt.json`.
- Standalone `cache/climate_handoff/package_climate_data.py` bootstrap verifier.
  Its hash is also in the producer receipt; this avoids extracting an unverified
  archive to obtain the verifier. A `PACKAGE_MANIFEST.json` sidecar permits inventory
  review before extraction. The same manifest is inside the archive.

Use Python **3.9 or newer**, standard library only; no pip, Node, NASA credentials,
Git repository or external service is needed after delivery. Keep at least 2 GiB
free for extraction and the separate reproduction workspace. The manifest records
the tested Python/zlib runtime: compressed bytes can differ across compression
versions even when decoded values agree. An exact-byte mismatch must be examined,
not waived. Package data remain local and are not integrated into the application.

## Verify and extract safely

Work outside an existing checkout/cache. Let `DELIVERY` be the directory holding
the delivered archive/bootstrap/sidecar. Verify the bootstrap SHA-256 against the
producer receipt using a trusted local hashing tool before running it. For example:

```bash
python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' /path/to/delivery/package_climate_data.py
```

Compare that output with `bootstrap_sha256` in the trusted receipt. A checksum
received through the same untrusted channel is integrity evidence, not sender
authentication. Then run (replace `/path/to/delivery` only):

```bash
DELIVERY=/path/to/delivery
EXPECTED_SHA256=$(python3 -c 'import sys; print(open(sys.argv[1]).read().split()[0])' "$DELIVERY/soil-to-stars-climate-bgd-v1.0.0.tar.gz.sha256")
python3 "$DELIVERY/package_climate_data.py" extract "$DELIVERY/soil-to-stars-climate-bgd-v1.0.0.tar.gz" --destination /tmp/soil-climate-handoff-v1 --sha256 "$EXPECTED_SHA256"
CLIMATE_ROOT=/tmp/soil-climate-handoff-v1/soil-to-stars-climate-bgd-v1.0.0
python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" verify --root "$CLIMATE_ROOT"
```

Confirm the sidecar's hash also equals `archive_sha256` in the trusted producer
receipt. Extraction rejects a wrong archive hash, existing destination, traversal,
absolute/noncanonical paths, links, duplicate members, unlisted files and size
mismatches. It writes regular files only and verifies every payload checksum.
It never extracts into or overwrites the working cache. A failed extraction may
leave its new diagnostic directory; choose a different fresh destination for a
retry rather than reusing it. The helper never silently deletes an old workspace.

Expected layout under `CLIMATE_ROOT`:

- `PACKAGE_MANIFEST.json`: version, full file list/sizes/hashes/roles, requested
  and actual coverage, working source hashes plus Git HEAD, runtime, scientific
  limits, missingness and all 11 outside-polygon mappings. Its own hash is in
  the external producer receipt; it is excluded from its own file table.
- `src/acquire/`: exact executable working source snapshot, including imported
  helpers. HEAD alone does not identify these uncommitted/untracked files.
- `data/climate/`: configuration, original registry, manifests and existing receipts.
- `data/admin/`: pinned compressed geometry, mapping/metadata/retrieval and attribution.
- `assets/`: only the small required BAMIS region mapping and provenance README.
- `cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/`: 100 original
  annual responses plus their 100 request manifests, with unchanged raw bytes.
- `cache/nasa_power_regional/prepared-v1/`: regional/district prepared products.
- `docs/data/`: setup/terms, scientific method and extreme-audit documentation;
  `LICENSE` and `THIRD_PARTY_NOTICES.md` retain source/rights context.

## Offline validation and reproduction

```bash
OFFLINE=1 python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" validate --root "$CLIMATE_ROOT" --report /tmp/climate-package-validation.json
OFFLINE=1 python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" reproduce --root "$CLIMATE_ROOT" --destination /tmp/soil-climate-reproduction-v1 --report /tmp/climate-package-reproduction.json
```

Validation checks all payload bytes, all 100 raw request identities/checksums and
response structures, deterministic registry regeneration, geometry roles and the
unchanged output mapping. The helper starts Python with `-I -B`, sets `OFFLINE=1`
and installs a socket audit hook that rejects networking. It does not rely on a
user's Python path, site packages, the original working directory or `.git`.
Validation may rewrite identical evidence receipts **inside the fresh extraction**;
it verifies package checksums again afterwards. It never touches Saim's cache.

Reproduction requires a destination that does not exist. It copies only profile A
sources/inputs/raw files into that separate root, with **no derived data copied**,
then runs the existing normalizer and adopted district exporter offline. It
compares the exact generated file set and SHA-256 of all **2,387 derived files**
(786 regional plus 1,601 district files including the manifest), rechecks raw/input
bytes and verifies the extracted package again. It preserves the original
prepared inventory/checksums and the 11 outside-polygon mappings.

## Load examples and choose inputs

```bash
python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" examples --root "$CLIMATE_ROOT"
```

This loads one regional daily wide record from `2001.wide-replay.jsonl.gz` and
one Chapainawabganj context record from
`district-context/bd-district-chapainawabganj-2001.wide-replay.jsonl.gz`. Read gzip
JSONL one line at a time with `gzip.open(path, "rt")` and `json.loads(line)`.
Daily `values`, `units`, LST date, coordinates and raw artifact identities remain
explicit. The Chapainawabganj record has separate original anchor and selected
output position: only the selected output is outside pinned country polygons.

For **A: offline preparation**, the manifest's `required_for: ["A", ...]` marks
raw responses/request manifests, exact sources and required configuration,
registry, geometry, small BAMIS mapping and evidence. No prepared bytes are needed
to compute outputs. For **B: consumption**, use wide daily regional/district files,
monthly JSON, chart JSON, inventory/manifests and supporting provenance/terms.
Raw files need not be loaded simply to consume those views. Long-form observations
are an optional consumption view, retained as canonical outputs because their
hashes belong to the original preparation receipt. The audit script is optional
for re-running the earlier extreme audit; it is not needed to load data.

No Point/smoke/error/quarantine caches, temporary downloads, `.git`, credentials,
frontend, map tiles, crop datasets/rules or duplicate archives are included.
These are historical regional context, not forecasts, district averages, field
measurements, verified physical weather or active agronomic rules. Preserve
nulls and coverage; do not clip unusual source values. See
[sharing terms](CLIMATE_DATA_PACKAGE_TERMS.md) before transferring/public sharing.

## If the archive is unavailable

Obtain the hash-matched working source and profile A input files from Saim or an
appropriate reviewed source snapshot first. The recorded HEAD alone lacks the
uncommitted implementation. A live NASA refresh is **not archival reproduction**:
upstream bytes/metadata may change. The following is a separately intentional
reacquisition/resume path, not a command executed during Step 3:

```bash
python3 -B src/acquire/download_nasa_power_regional.py --check-config --plan full
python3 -B src/acquire/download_nasa_power_regional.py --plan full --execute-full
OFFLINE=1 python3 -B src/acquire/prepare_nasa_power_regional.py
OFFLINE=1 python3 -B src/acquire/regional_climate_handoff.py --export-context
```

Run from the matching repository/snapshot root with OFFLINE unset only for the
second command. It is sequential, one parameter-year per request, 90-second
timeout and bounded transient retries; valid matching raw caches resume, while
sustained failure/throttling pauses. Do not bypass checksum/technical failures.
Any changed NASA bytes require renewed QA and a new package version, not a claim
that this v1.0.0 receipt was reproduced. Public sharing is not cleared or performed.
