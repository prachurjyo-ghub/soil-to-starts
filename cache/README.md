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
