# Soil to Stars frontend

Existing Next.js frontend demonstration. Current routes `/` and `/workspace` load supplied reference HTML/static scripts; additional React components are present but not all are mounted. Scores, traits, soil defaults and climate series are illustrative.

Run `npm ci` then `npm run dev`. Check with `npm run lint` and `npm run build -- --webpack`; after a successful build use `npm run start`. Keep the lockfile. See the [root quick start](../README.md), [task board](../docs/PROGRESS.md) and nearest [instructions](AGENTS.md).

The targeted dependency patch is documented in [SECURITY.md](../SECURITY.md). Data/API/scientific behavior and fully offline browser support remain planned; no NASA key is required for this demo. Existing asset credits and rights-review work remain in the repository.

## Required farmer intake

The mounted `/workspace` starts with independent confirmed map-pin or nationwide district selection and six required questions in `public/reference/intake-ui.js`; `intake.js` provides the shared validator and local sourced district directory. Genuine intake drafts/submissions are separate from the explicitly opened illustrative demo. A validated submission shows planning unavailable: scientific data, reviewed crop rules and the API/rotation engine are not connected.

Run `npm run test:intake` for validation and UI-controller tests. Public reference scripts are excluded from ESLint: directly run `node --check public/reference/intake.js`, `node --check public/reference/intake-ui.js` and `node --check public/reference/workspace.js` as well as lint/build. [Intake evidence and limits](../docs/INTAKE_QA.md) records actual checks.

The map extension uses MapLibre GL JS 6.16.0 through `components/IntakeMapRuntime.js`, plus local versioned district geometry. The default is OpenFreeMap Liberty street/reference mapping. Configure `NEXT_PUBLIC_BASEMAP_STYLE_URL` and `NEXT_PUBLIC_BASEMAP_LABEL` at build time if changing providers; keep style-source attribution. The library/worker and boundary geometry are lazy; district search stays independent. No field polygon/area tools or scientific API is added. See [location QA and browser checks still required](../docs/LOCATION_QA.md) and [schema/migration](../docs/API_CONTRACT.md).

Also syntax-check `public/reference/location.js` and `public/reference/intake-map.js`; `npm run test:intake` now includes geometry, migration and map-controller regression tests. Reproduce the administrative asset with `python3 scripts/prepare_district_boundaries.py` from the root, using the checked-in licensed source snapshot without network.
