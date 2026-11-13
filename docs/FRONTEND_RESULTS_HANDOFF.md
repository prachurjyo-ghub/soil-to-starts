> Local API update — 13 November 2026: genuine inputs now generate persisted SQLite evidence reports through the same localhost:3000 server. Crop identity options expand to 30 labels, and reports include joined regional calendars, NASA weather, metric-definition gaps and reload restoration. Statements below about the scientific crop engine remain valid: full crop plans/risk scoring are still pending. See DATA_INTEGRATION.md.

# Frontend workspace — current state

Follow [DEVELOPMENT.md](DEVELOPMENT.md) for the solo checklist. The existing Next.js app is served on port 3000. No additional API server is required for UI navigation or archived weather charts.

## Destinations

| URL | Function |
| --- | --- |
| `/` | Homepage, direct workspace entry, scrolling NASA weather-history story |
| `/workspace#profile` | Six-question intake, district search/map, validated drafts/submissions |
| `/workspace#overview` | Result status, submitted field, current-crop exposure panel |
| `/workspace#rotations` | Supplied alternatives and operations timeline |
| `/workspace#compare` | Same-period baseline/alternative comparison and evidence |
| `/workspace#simulator` | Separate water/priority scenario request; original answers preserved |
| `/workspace#climate` | Local NASA annual temperature/rainfall, district selector, period comparison |
| `/workspace#saved` | Labelled result snapshot save/restore/download/print |
| `/workspace#methodology` | Data sources, pipeline, implemented/pending calculations and limits |

Back/Forward and homepage/workspace links work with the browser history. Genuine planning is not replaced by a fixture. Explicit examples remain marked and can be saved only with their provenance intact.

## Data and implementation

Mounted routes use reference HTML via Next.js; `workspace.js` dispatches to the existing result renderer and `workspace-pages.js`. The common `climate-history.js` renderer serves both workspace weather and `weather-story.js`. Statistics live in `src/compute/climate_history.py`; `scripts/build_ui_climate.py` verifies the archive checksum and builds `prototype/public/data/climate-history.json`. No NASA calls or weather calculations run in the browser.

The payload contains all 64 district representative-point mappings and 25 years of annual NASA POWER T2M/PRECTOTCORR summaries. Rainfall annual totals sum complete months; temperature is weighted by days. Period comparison requires ten complete years in both 2001–2010 and 2016–2025. The difference is descriptive, not a significance, causal or forecast claim. Grid positions, anchor distance, source/chart hashes, units and limits are displayed. Independent scientific review remains pending.

## Pending scientific work

Crop suitability/ranking, current-crop heat/water assessment, same-engine scenario evaluation, intended-crop checks and replay still require reviewed crop rules and the deterministic engine/API. UI exposes unknown/unavailable states until those outputs exist. These are functional routes, not a claim that the complete agricultural decision system is implemented.

## Verification

60 Node UI tests and 70 Python tests passed; frontend lint and production webpack build passed. The climate payload reproduces from the pinned archive. Browser walkthrough covered sidebar destinations, complete valid input submission, exposed current-crop unknowns, example comparisons and snapshot reload, what-if isolation, real weather controls, EN/BN story, browser Back/Forward and mobile More navigation. Climate page at 390px had no document overflow. Physical phone/touch, final print output, exhaustive translation/accessibility and disconnected-browser certification remain open.
