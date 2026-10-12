# Future data and service code

This area is a scaffold for the Field Shift data path. Nothing here is wired to the Next.js frontend yet. Keep responsibilities separate so a displayed number can be traced to an input and a tested calculation.

- `acquire/`: download, parse, quality-check, and cache data.
- `compute/`: deterministic indicators, feasibility rules, comparison, and sensitivity analysis.
- `agents/`: optional orchestration and sourced explanations after the core pipeline works.
- `api/`: serve computed results and provenance from local files; no network dependency during an offline demo.

See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) for the complete pipeline and [`docs/METHODOLOGY.md`](../docs/METHODOLOGY.md) for analysis and validation details.
