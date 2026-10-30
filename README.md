# Soil to Stars

Explainable crop-rotation planning for Bangladesh for [NASA Space Apps 2026 — Field Shift](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/).

**Start your day with the [team task board](docs/PROGRESS.md).** It lists every work package, small checklist item, owner, prerequisites, errors, verification and next handoff. The repository's historical name is `soil-to-starts`; the product is **Soil to Stars**.

## Honest current status

The working product is a Next.js frontend demonstration at `/` and `/workspace`, backed by supplied reference HTML/assets. Its crop traits, scores, soil defaults and climate charts are illustrative. The React components also present in the tree are not all mounted by the current routes. There is no integrated NASA ingestion, validated agronomic engine, FastAPI service or verified offline science dataset yet.

The development workflow is implemented locally: task checklists, generated progress, command-only AI logs, tests and CI definitions. Independent review, publication, scientific validation and submission remain separate gates. A green workflow check does not validate agricultural advice.

<!-- workflow:progress:start -->
## Team progress and next steps

Generated from task records; the detailed board is the team's daily starting point.

**Accepted work packages: 0/29 · Implemented checklist items: 30/134.** Checked items can still await independent review and merge.

| Member | First available action |
| --- | --- |
| Fardin | DELIVERY-INTAKE / a2: Pass delivery checks and inspect the staged changes before creating scoped commits. |
| Saim | Review/collaborate on G0-CONTRACT |
| Maruf | Review/collaborate on G0-CONTRACT |
| Prachurjo | Review/collaborate on G0-CONTRACT, MEDIA-STORYBOARD |
| Nadim | MEDIA-STORYBOARD / s01: Plan the shots and visual sequence |
| Hla | MEDIA-STORY / s01: Define the problem and audience |

[Detailed progress, acceptance and blockers](docs/PROGRESS.md) · [Workflow commands](docs/WORKFLOW.md) · [Short prompt logs](docs/PROMPT_LOG.md)

<!-- workflow:progress:end -->

## Run in five minutes

Prerequisites: Git, Python 3.9+, Node.js satisfying the locked Next.js requirement (>=20.9.0), and npm. CI uses Node 24. No NASA key, Python packages or database is needed for the current frontend.

```bash
python3 scripts/doctor.py
cd prototype
npm ci
npm run dev
```

Open [the homepage](http://localhost:3000) or [the workspace](http://localhost:3000/workspace). Keep `package-lock.json`; do not upgrade dependencies incidentally. Installation needs network access or a populated package cache.

From the repository root:

```bash
make check
make build
```

Equivalent commands are documented in [CONTRIBUTING.md](CONTRIBUTING.md). `make check` runs workflow tests, record validation and frontend lint; `make build` performs the production build using the installed Next.js webpack option. Backend launch/science-test commands remain planned until their implementation PRs exist.

## What we are building

Start with one supported Bangladesh pilot. A short form records location, current harvest/field availability, recent crops/usual rotation, seasonal water access and a priority preset; relevant soil details may be unknown. Previous/current crops may match.

**Mandatory now:** authentic POWER evidence and reviewed crop rules; deterministic three-future-crop alternatives compared with existing practice; a trade-off matrix, quick intended-crop check and evidence-linked rejection reasons; one historical stress replay; versioned receipt with basic print/JSON; a compact climate story after the first scientific flow; accessible EN/BN UI, verified offline science and an authorized published pilot. Aggregate scores are optional. These are team commitments, not extra NASA mandates.

**Future only:** wider coverage, additional datasets/maps, long-duration crops, rich 3D/voice/PWA, broader projections, optional soil/fertilizer research, accounts/economics/sensors and runtime assistance. Future tasks remain blocked after the MVP until separately activated. No fertilizer tracking, nutrient-depletion simulation, numerical soil-restoration claims or runtime AI in MVP.

Read the two contexts: **[Mandatory-now specification](docs/MVP_SCOPE.md)** and **[Future implementation roadmap](docs/FUTURE_ROADMAP.md)**. [Product details](docs/PRODUCT_SPEC.md) preserve sources, constraints and completion semantics. A complete comparison needs an assessed baseline and two distinct supported alternatives on a common horizon; missing evidence produces a useful incomplete/unavailable state, never filler crops.

## Repository boundaries

```text
prototype/        existing Next.js application; preserve routes/reference assets
src/acquire/      planned authentic source ingestion, QA and caching
src/compute/      planned deterministic climate/agronomy/rotation/scenario logic
src/api/          planned validation, transport and provenance gate
src/agents/       future only; no MVP runtime AI
cache/            local downloads, ignored except its README
demo_fixtures/   small verified/licensed offline evidence when available
docs/            specifications, team board, sources and truthful AI records
scripts/         development workflow, diagnostics and PR validation
tests/           development-helper tests; science/API tests added with implementation
.github/          task/PR templates and CI definitions
```

Scientific data flow: NASA/local sources → acquisition/QA → versioned local cache/fixtures → API + deterministic compute → provenance gate → frontend. The frontend never queries NASA for scientific results. Local prepared data supports the scientific demo; browser assets/fonts/maps need their own offline validation. Never cache restricted map tiles.

## Six owners

| Owner | Accountability |
| --- | --- |
| Fardin | Contracts, backend/API, rotation engine, integration and freeze |
| Saim | NASA evidence, climate indicators, QA and reproducibility |
| Maruf | Bangladesh crop/soil rules, source applicability and limitations |
| Prachurjo | Existing frontend, maps/fallback, API integration, bilingual UX/access |
| Nadim | Storyboard, video/motion, subtitles, exports and asset credits |
| Hla | Story/script, narration, claims review, presentation and Q&A |

Each person follows the [team playbook](docs/TEAM_PLAYBOOK.md), works on a bounded branch, records evidence and hands off through review. Equal responsibility does not mean equal commit counts. GitHub identities remain unconfirmed until real contribution evidence and an explicit name mapping exist.

## Find the right document

| Need | Read |
| --- | --- |
| What do I do next? | [Team task board](docs/PROGRESS.md) |
| How do I update a task or command record? | [Workflow commands](docs/WORKFLOW.md) |
| How do teammates coordinate? | [Team playbook](docs/TEAM_PLAYBOOK.md), [contributing](CONTRIBUTING.md) |
| What is mandatory now / deferred? | [MVP scope](docs/MVP_SCOPE.md), [future roadmap](docs/FUTURE_ROADMAP.md) |
| What exactly must the product do? | [Product](docs/PRODUCT_SPEC.md), [UI/UX](docs/UI_UX_SPEC.md) |
| Where does data come from? | [Sources](docs/DATA_SOURCES.md), [references](docs/REFERENCES.md) |
| How is science verified? | [Methodology](docs/METHODOLOGY.md), [validation](docs/VALIDATION.md) |
| What are the API decisions? | [Draft API contract](docs/API_CONTRACT.md), [architecture](docs/ARCHITECTURE.md) |
| What is required before judging? | [Submission](docs/SUBMISSION.md), [third-party notices](THIRD_PARTY_NOTICES.md) |
| What did AI actually do? | [AI-use disclosure](docs/AI_USE.md), [command log index](docs/PROMPT_LOG.md) |

AI assistance is declared per contribution, including tool and human review. Logs contain implementation/commit/push commands and actual work only; ordinary conversation, ideas and explanations are excluded. A manual contribution uses no invented AI prompt. Current user authorization controls commits, pushes and publication; these files do not authorize them.

Source and asset rights must be reviewed before release. The code-license scope and known third-party items are recorded in [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Font/media clearance, official local/global submission requirements and agronomic evidence remain explicit board items. The supplied independent build guide is planning context, not NASA authority or validated observations.
