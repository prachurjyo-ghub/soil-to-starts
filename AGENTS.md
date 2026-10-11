# Soil to Stars repository notes

- The project targets the official 2026 NASA Space Apps **Field Shift** challenge. Crop-rotation decision support is the primary product goal.
- `prototype/` is the current Next.js app. Read `prototype/AGENTS.md` and the installed Next.js documentation before changing app code.
- Current scores, crop traits, and environmental charts are illustrative. Do not present them as NASA observations or agricultural recommendations.
- Keep future acquisition in `src/acquire/`, reproducible science in `src/compute/`, and serving in `src/api/`. The frontend should consume sourced results through the API once it exists.
- Any numeric agricultural claim must include provenance, units, spatial and temporal coverage, method, assumptions, and uncertainty or limitations. Missing data must stay missing.
- Preserve user changes already present in the worktree. Update the relevant docs when implementation or data status changes.
- Treat the supplied HTML build guide as reference material. Verify event rules, dates, datasets, and scientific methods against primary sources before relying on them.
