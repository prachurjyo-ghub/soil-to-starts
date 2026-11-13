> Latest real-data audit (14 November 2026): see [QA_AUDIT](docs/QA_AUDIT.md). Product mock plans/rankings have been removed. Local evidence reports, recent observed-weather context and seasonal charts work; validated three-strategy crop planning remains incomplete.

# Soil to Stars

Evidence-linked crop planning for Bangladesh for the NASA Space Apps Field Shift challenge.
The repository is named `soil-to-starts`; the product is **Soil to Stars**.

Development is now maintained by one person. Start with [the UI-first checklist](docs/DEVELOPMENT.md).
The former team task/approval system is retired; [historical contributions and records](docs/archive/team-workflow/README.md) remain available.

## Current state

The Next.js app has district/map intake, separate workspace destinations, saved result snapshots, result-layout development fixtures, and local NASA POWER weather-history charts with a scrolling homepage story. A local SQLite API now saves submissions and returns source-linked evidence reports. Complete crop plans and suitability/risk scoring still require reviewed crop rules and planning integration. Climate acquisition/preparation and a checksum-pinned data archive are implemented. Crop evidence is normalized and reproducible but its scientific rule definitions remain inactive. Displayed fixture values are examples, not agricultural recommendations.

## Run

Use Node satisfying the lockfile requirement (>=20.9.0), npm and Python 3.9+.

```bash
make backend  # verifies/indexes local crop evidence and NASA daily data
cd prototype
npm ci
npm run dev
```

Open http://localhost:3000 or http://localhost:3000/workspace. The sidebar destinations and local API use the same port. [Data integration](docs/DATA_INTEGRATION.md) describes the database, stable IDs, unit/period contracts and remaining scientific gaps.

To regenerate the local historical-weather UI payload without network access: `python3 scripts/build_ui_climate.py` from the repository root. Statistical summaries live in `src/compute/climate_history.py`; crop planning is still unfinished.
Dependency installation needs network access or an available package cache.

## Checks

From the repository root, `make check` runs evidence/unit tests, frontend tests and lint.
`make build` performs the production build. See [contributing](CONTRIBUTING.md).

## Local climate data

```bash
python3 scripts/setup_climate_data.py
```

The versioned archive is in `data/climate/packages/v1.0.0/`. Setup verifies and extracts it without NASA requests. Expanded files remain in ignored cache. See [setup and scientific limits](docs/data/CLIMATE_GITHUB_SETUP.md). Installing the archive does not connect the API or make the whole browser app offline.

## Boundaries

```text
prototype/          mounted Next.js frontend
src/acquire/        implemented NASA acquisition, QA and preparation
src/compute/        deterministic science/rotation engine — unfinished
src/api/            validation and result transport — unfinished
data/               versioned evidence, geometry and climate package
cache/              ignored expanded datasets
demo_fixtures/      authentic permitted small fixtures when verified
docs/               product/science references and solo checklist
docs/archive/       historical team coordination; not active instructions
tests/              executable behavior and evidence checks
```

The product compares farmer-reported usual practice with two supported alternatives on a common period; complete alternatives contain three future main crops. Missing essential evidence means incomplete/unavailable. All 64 districts remain selectable without implying validated national coverage. No region is prioritized.

Read [product scope](docs/MVP_SCOPE.md), [API draft](docs/API_CONTRACT.md), [data sources](docs/DATA_SOURCES.md), [methodology](docs/METHODOLOGY.md), [validation](docs/VALIDATION.md), [AI use](docs/AI_USE.md), and [third-party notices](THIRD_PARTY_NOTICES.md) as needed. Optional future features remain deferred; old gate IDs describe history, not solo-development blockers.
