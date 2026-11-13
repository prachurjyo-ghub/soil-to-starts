# Local data cache

Place downloaded NASA and partner data here during acquisition. Git ignores the contents of this directory. Each processed dataset should have a provenance record before it is used in an analysis: product/version, URL or DOI, download date, coordinates or polygon, time range, units, transformations, and quality checks.

The Step 2 NASA POWER smoke test stores four verified raw JSON responses and
their request manifests under `cache/nasa_power/nasa-power-daily-bgd-64-v1/`.
These ignored files cover Bagerhat and Rangamati for January 2001 and January
2025 only. They are not a full historical or nationwide collection; checked-in
evidence and checksums are in
`data/climate/nasa_power_smoke_test_manifest.json`.

The Step 3B Regional API smoke test stores four verified three-day JSON
responses and request manifests under
`cache/nasa_power_regional/nasa-power-daily-regional-bgd-v1/`. Preserved 422
diagnostics record the one-parameter and minimum 2° × 2° extent restrictions.
Checked-in checksums and findings are in
`data/climate/nasa_power_regional_smoke_test_manifest.json`; these files are not
a national historical collection.

The Step 3C national-extent preflight adds one verified raw JSON response and
manifest at `raw/bgd-padded-national/PRECTOTCORR/20010101_20011231.*` within
the same Regional cache collection. It covers raw Regional PRECTOTCORR for
calendar year 2001 only and does not contain district-derived series.

## Current Regional collection and teammate delivery

The smoke/preflight descriptions above are historical bounded stages. The full
Regional 2001–2025 collection now contains 100 verified annual parameter responses
in `nasa_power_regional/nasa-power-daily-regional-bgd-v1/raw/`; prepared regional,
monthly/chart/replay and district-context files are in
`nasa_power_regional/prepared-v1/`. These remain ignored by Git.

The sealed v1.0.0 archive remains in `climate_handoff/`. The ready-to-copy folder
for Fardin is **`climate_delivery/Saim_to_Fardin_climate_v1.0.0/`**. Copy the whole
folder separately; cloning/pulling the repository will not deliver it. Its
`START_HERE.md` gives trust/hash, safe extraction, offline validation/reproduction
and loading instructions. `LOCAL_PRODUCER_CHECKS.json` is producer-side evidence,
not a claim that Fardin has received or independently accepted the data. No
archive upload or recipient contact was performed. See the canonical report at
`docs/data/CLIMATE_TEAM_HANDOFF_REPORT.md` and preserve the package's sharing terms.


## Current Git-based delivery

Manual transfer is no longer required: the sealed archive and metadata are
tracked under `data/climate/packages/v1.0.0/`. After clone/pull on `main2`, run
`python3 scripts/setup_climate_data.py`. The default installation is under
`cache/climate_repository/v1.0.0/`; expanded files remain ignored. The older
local delivery directories are preserved as historical artifacts. See
`docs/data/CLIMATE_GITHUB_SETUP.md`; installation is not application integration.
