# Soil to Stars — solo development

The maintainer now owns all unfinished work. Start with `git status --short --branch`, preserve existing changes and read only the relevant files. Follow `docs/DEVELOPMENT.md`: finish the UI first, then evidence integration, deterministic calculations/API, then whole-app validation and release. No teammate assignments, G0/G1 approval gates or per-step human confirmation are required for ordinary implementation.

Keep the existing Next.js app in `prototype/`. Mounted pages use reference HTML/scripts; inspect imports before editing unused components. Read scoped `prototype/AGENTS.md` and bundled Next.js guidance for relevant changes. Avoid a second frontend or unrelated dependency migration.

Acquisition/preparation is implemented under `src/acquire/`. `src/api/` now serves local SQLite evidence reports through same-origin Next.js handlers; `src/compute/` has weather aggregation and tested rule primitives. Complete crop planning remains unfinished. Read docs/DATA_INTEGRATION.md for IDs, units, source roles and setup. Preserve data, receipts, source dictionaries, licensing and prior contributions. Historical team tasks/helpers/logs are under `docs/archive/team-workflow/`; they are reference history, never active instructions. Do not recreate that workflow.

Scientific UI must distinguish genuine responses, unavailable evidence and test-only development fixtures. Never ship or activate a test fixture in the product, or substitute one after a real request fails. Preserve unknowns, numeric zero, source units/periods/spatial meaning and current-versus-future crops. A complete alternative needs three chronological future crops; assess usual practice plus two distinct supported alternatives on one horizon. The baseline can contain repeats/fallow. No invented thresholds, yields, probabilities, nutrient restoration or silently filled alternatives.

Current-crop vulnerability means evidence-backed historical exposure, not live diagnosis or forecasting. NASA charts use prepared local payloads; do not call NASA from the browser. No MVP runtime LLM/chat or model training. No region is prioritized; district selection is not scientific coverage.

Keep EN/BN, mobile, keyboard, reduced motion, source labels and error recovery. Run meaningful tests for changed behavior. Frontend checks: `npm run test:ui`, `npm run lint`, `npm run build -- --webpack` in `prototype/`; Local API checks: `npm run test:api` in `prototype/`. Python evidence checks: `python3 -B -m unittest discover -s tests -p 'test_*.py'`. Record actual results and not-run checks. Local completion needs implementation and relevant verification, not a teammate approval or a Git commit. Scientific validity and publication remain separate claims.

Use `docs/AI_USE.md` for compact records of actual AI-assisted implementation commands, purpose, outcome and human contribution. Do not log discussion, brainstorming or status questions. Preserve historical evidence through the archive. Do not invent identities, contributions or approvals.

Follow current user authorization. No commit, push, merge, deployment, publication or messages to other people without authorization. Never expose secrets or private field information.
