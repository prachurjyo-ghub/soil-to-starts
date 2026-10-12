# Soil to Stars — Field Shift

Soil to Stars is a decision-support prototype for the [2026 NASA Space Apps Challenge, **Field Shift: Adapting Farms with NASA Data**](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/). Its Bangladesh pilot helps a farmer compare crop rotations against field conditions, water access, crop characteristics, and their own priorities. The intended result is an understandable choice with reasons and trade-offs, rather than a score alone.

## Current state

**The working app is a frontend demonstration.** It contains a landing page and a field-planning workspace with field inputs, rotation comparisons, a scenario explorer, illustrative environmental charts, English/Bangla interface text, and browser-local saved plans. Crop traits, scores, locations, and chart values are examples. The app does **not** fetch NASA observations, calculate a validated planting window, predict yield, or provide field-specific agricultural advice. The workspace labels its demo data and planned sources accordingly.

## Run the app

```bash
cd prototype
npm ci
npm run dev
```

Open `http://localhost:3000` for the landing page and `http://localhost:3000/workspace` for the planning workspace. To check the production build, run `npm run build` from `prototype/`. No NASA credentials are needed for the current frontend.

## Repository layout

```text
.
├── README.md                 Project entry point and current status
├── AGENTS.md                 Repository conventions for coding agents
├── .env.example              Planned data-mode setting; no secrets
├── cache/                    Local downloaded data (gitignored)
├── demo_fixtures/            Future committed, sourced offline samples
├── docs/
│   ├── AI_USE.md             AI contribution log
│   ├── ARCHITECTURE.md       End-to-end data and decision pipeline
│   ├── BUILD_GUIDE_REVIEW.md What we adopted from the supplied guide
│   ├── DATA_SOURCES.md       Planned datasets and provenance requirements
│   └── METHODOLOGY.md        Decision logic and validation plan
├── src/
│   ├── acquire/              Planned data acquisition boundary
│   ├── compute/              Planned deterministic analysis boundary
│   ├── agents/               Optional future explanation/orchestration layer
│   └── api/                  Planned local API boundary
└── prototype/                Existing Next.js frontend (the guide's web layer)
```

The `src/` directories describe the intended data path; they are **not an implemented backend**. The existing frontend remains in `prototype/` to preserve its working commands and supplied reference assets. An agent or MCP service would only be built if the product needs one. The complete proposed flow is in [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Product path

1. **Describe the field:** district or coordinates, measured soil conditions where available, irrigation access, crop history, and farmer priorities. Keep missing values visible.
2. **Assemble evidence:** use locally cached NASA POWER weather series first; evaluate IMERG rainfall, SMAP soil moisture, and MODIS vegetation indices where their resolution and time coverage fit the question. Record product, version, dates, spatial support, quality flags, and extraction method. See [data sources](docs/DATA_SOURCES.md).
3. **Compute in reproducible functions:** derive season-level indicators and feasible crop sequences without an LLM calculating scientific values. A rainfall-onset indicator and growing degree days may inform rotation timing, but their thresholds and crop-specific assumptions need local agronomic review. See [methodology](docs/METHODOLOGY.md).
4. **Compare rotations:** show the effect of water, soil, climate, and farmer priorities, including disqualifying constraints, uncertainty, and the source behind each claim. The farmer-facing answer should name a usable option and explain why.
5. **Demonstrate offline:** once real samples exist, commit a small, attributed fixture and make the data mode visible in the interface. Until then, the frontend's demo values remain labeled illustrative.

## What must happen before real advice

- Select a district, crops, crop calendar, and agronomic thresholds with local expertise.
- Ingest and quality-check NASA data and local soil/crop information; do not imply a satellite grid cell is a field measurement.
- Implement and test the analysis, including missing-data behavior, threshold sensitivity, historical replay, and comparison with local observations.
- Connect the API and frontend, then test Bangla wording and phone usability with intended users.
- Replace every demo score and chart with sourced results, or keep it clearly labeled as an example.

The attached build guide informed this structure. Its rainfall-onset snippet is a sketch, not a validated rule: its code does not actually test the documented “dry spell longer than seven days” condition. The guide's example 11-day shift is also a demo sentence, not a result for Rajshahi. See the [review](docs/BUILD_GUIDE_REVIEW.md).

## Source and reuse status

The [official Field Shift challenge](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/) defines the project goal. Dataset links and current integration status are in [DATA_SOURCES.md](docs/DATA_SOURCES.md). Image and video credits for the supplied frontend are in [credits.txt](prototype/public/reference/assets/credits.txt). The project does not yet contain a root license; the team must choose an OSI-approved license and check third-party asset terms before publishing a submission. [NASA's 2026 participant terms](https://www.spaceappschallenge.org/legal/) require original project content to be freely available without restriction or open source.
