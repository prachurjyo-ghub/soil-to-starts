# Post-hackathon agent boundary

No runtime agent is implemented. See [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) for its possible role in the Field Shift pipeline. If added, this directory should contain orchestration, tool schemas, prompts, and provenance checks. Scientific values must come from `src/compute/` and sourced data tools, never from model-generated arithmetic. A failed citation check must block the generated explanation and fall back to a fixed, source-linked response.
