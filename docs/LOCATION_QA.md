# INTAKE-MAP verification and handoff

Fardin authorized this bounded location extension on 30 October 2026. Current science remains unavailable. The six required intake questions and their order are preserved; the mounted reference workspace now offers independent map-pin and district-search methods above them. Broader G0/G1D/G3 gates and independent human approval remain pending.

## Files changed

- Runtime: `prototype/components/IntakeMapRuntime.js`, `prototype/app/workspace/page.js`, `prototype/public/reference/location.js`, `intake-map.js`, `intake.js`, `intake-ui.js`, `workspace.js`, `workspace-fixes.css`; existing reference HTML/mounting is preserved.
- Dependency/notices: `prototype/package.json`, `prototype/package-lock.json`, `prototype/public/reference/licenses/maplibre-gl.LICENSE.txt`, `THIRD_PARTY_NOTICES.md`.
- Data: `data/admin/README.md`, `bgd-adm2-source.geojson.gz`, `bgd-adm2-metadata.json`, `bgd-adm2-mapping.json`, `bgd-adm2-retrieval.json`; runtime `prototype/public/reference/data/district-boundaries.v1.geojson` and `district-boundaries.manifest.json`; `scripts/prepare_district_boundaries.py`, `scripts/check_location_assets.py`.
- Tests: `tests/intake.test.cjs`, `tests/location.test.cjs`, `tests/fixtures/district-interior-points.json`.
- Documents: `docs/API_CONTRACT.md`, `docs/UI_UX_SPEC.md`, `docs/MVP_SCOPE.md`, `docs/PRODUCT_SPEC.md`, `docs/DATA_SOURCES.md`, `docs/INTAKE_QA.md`, `docs/LOCATION_QA.md`, `prototype/README.md`.
- Records: `docs/tasks/INTAKE-MAP.json`, `docs/tasks/INTAKE-UI.json`, `docs/prompt_logs/fardin-0001.md`; regenerated `README.md`, `docs/PROGRESS.md`, `docs/PROMPT_LOG.md`. Existing unrelated changes remain preserved.

## Reproduction

```bash
python3 scripts/prepare_district_boundaries.py
node --check prototype/public/reference/location.js
node --check prototype/public/reference/intake-map.js
node --check prototype/public/reference/intake.js
node --check prototype/public/reference/intake-ui.js
node --check prototype/public/reference/workspace.js
cd prototype
npm run test:intake
npm run lint
npm run build -- --webpack
```

For read-only HTTP asset verification, start a production preview on loopback port 3014 and run `python3 scripts/check_location_assets.py --base-url http://127.0.0.1:3014`. It compares served assets, the boundary checksum and the deployed license; it does not test WebGL or mobile behavior.

Then from repository root:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/workflow.py render
python3 scripts/workflow.py check
```

Direct syntax checks matter: ESLint still excludes the public reference scripts. The Node suite exercises the actual production validator and UI submit handler with a document/event harness; map lifecycle/failure tests use mocked MapLibre/DOM APIs. They are not a browser or agronomic validation.

## Provider and data evidence

- **MapLibre GL JS 6.16.0**, BSD-3-Clause, installed explicitly in the existing npm lockfile. Next.js/React versions were preserved. A small Client Component exposes a lazy dynamic import; the map library is fetched only when map mode opens. The ESM worker uses a bundler-emitted URL, not an unversioned CDN. An explicit deployed license file accompanies the optimized output, because the worker header is stripped by build optimization.
- Default style: [OpenFreeMap Liberty](https://tiles.openfreemap.org/styles/liberty), following [official setup](https://openfreemap.org/quick_start/). It is labelled street/reference mapping, not satellite imagery. Source attribution remains visible in the map and adjacent credits. `NEXT_PUBLIC_BASEMAP_STYLE_URL` and `NEXT_PUBLIC_BASEMAP_LABEL` configure another style/name at build time; custom styles must carry correct source attribution. No tile bulk download/cache is added.
- Local [boundary snapshot/alias ledger](../data/admin/README.md): geoBoundaries gbOpen `BGD-ADM2-16705992`, revision `9469f09`, represented year 2020 per metadata, declared **CC BY 3.0 IGO**, BBS / OCHA ROAP sources. Metadata's underlying source link says as of 2015; that limitation is retained. All 64 mappings are explicit, including ten spelling aliases; no fuzzy matching or nearest district assignment.
- The downloaded upstream simplified source is **1,686,112 bytes**, SHA-256 `7dbdb186f3b8af10417147a99859196fcd89c619fb5c6ac3804251fb6b449b6a`. Its Git LFS pointer was verified against actual downloaded bytes. A lossless gzip snapshot permits offline reproduction.
- The runtime output is **1,494,403 bytes**, 47 Polygons / 17 MultiPolygons, 377 rings, 38,112 vertices, SHA-256 `9503a358ddcb99714db5866ef049e7ddea0d5fd6e05a0d3719a6553b3953c01a`. Property mapping, bbox addition, sorting and minification are recorded; no additional coordinate rounding/simplification is performed. The source does not establish survey-level precision.
- Deterministic offline gzip size is **507,697 bytes**. A production loopback HTTP request returned **513,054 transferred gzip bytes**, decoded to the exact 1,494,403-byte asset, in **51.94 ms** on this host. This is a loopback measurement, **not mobile-network performance**. Runtime geometry/worker loading is lazy; district-only use downloads neither the geometry nor the map code. Saved point rechecking loads local geometry but need not open a map. The bundled worker was served as JavaScript, 510,888 decoded bytes / 146,732 gzip bytes in the observed production build.

## Behavior covered by automated checks

The **31-test** intake/location suite retains the original 18 regression cases and adds exact source/mapping/checksum checks, independent geometry-derived interior fixtures for every district, Polygon/MultiPolygon/hole cases, invalid/reversed coordinates, outside/unresolved/overlap/shared-border cases, required pin confirmation/reconfirmation, switching methods without stale data, v1-to-v2 migration and saved-pin pending recheck. It verifies district search without boundaries, a successful map submission through the actual UI handler, a subsequent successful district submission, EN/BN labels, draft/last-submission separation, one map instance across rerenders, and cleanup on leaving the view. WebGL, context loss, tile and local-boundary network failures retain other answers and leave district fallback usable.

`farmer-intake.v2` emits either a confirmed, contained point with actual selected coordinates/boundary provenance, or district context with null coordinates/directory provenance (including `directory_version`). The existing storage key retains envelope version 2. New pins are pending, and switching methods clears inactive location values. Old genuine district answers migrate without guessed coordinates. Saved point submissions are retained pending geometry recheck if loading fails. No coordinates are included in command logs or public field URLs; map hash tracking is disabled.

## Browser attempts and remaining checks

The browser connector reported **“The browser access host is unavailable.”** Native Chrome loaded the production workspace and showed both method controls above the six questions. Native pointer operations then repeatedly returned **`noWindowsAvailable`** and select/keyboard interactions could not be verified reliably, even after Fardin left Chrome idle. These are tool limitations, not passing browser tests.

**Not performed/verified:** a complete successful browser submission for either method; real browser WebGL/worker/tile initialization; drag/tap confirmation; browser reload persistence; current map phone-width layout; physical-phone operation; mobile throttling and actual touch behavior. Earlier intake-only mobile observations in INTAKE_QA are historical and do not establish new map behavior. Map code/controller tests and HTTP asset checks do not substitute for these walkthroughs.

Prachurjo's independent review should open each location method, complete all six questions, submit, reload and verify summary/source/state. For map mode, check an initial empty selection, a contained point, drag/reconfirmation, outside/border corrections, language switching and marker/camera persistence during other answers. Test a narrow phone viewport and physical device, attribution visibility, keyboard navigation and forced WebGL/tile/boundary failures. Until then, local implementation is reviewable but browser usability is unverified.

## Scientific limits and status

Administrative location is not scientific recommendation coverage. A precise pin does not make NASA grids exact field measurements. All validated inputs still show planning/comparison unavailable; no NASA calls, crop recommendations/scores, nutrient features, accounts or engine were added. Geometry gaps/coasts/borders are not silently resolved. Basemap tiles need network access; complete browser offline use remains untested.

Boundary integrity uses WebCrypto SHA-256; map mode requires a secure browser context (HTTPS or localhost), WebGL and the configured basemap. An insecure LAN preview can fall back to district search. Use HTTPS for physical-phone review. District search does not need those map capabilities.

Shared INTAKE-UI readiness was reopened for regression checks; prior evidence remains intact and independent review is still pending. Task **INTAKE-MAP**, command **P-c57fe1ebaa44** (one new Fardin implementation instruction). At that implementation handoff no commit, push, merge or deployment was authorized/performed. Fardin subsequently authorized feature-branch commit/push delivery under DELIVERY-INTAKE; review/scientific gates remain pending.
