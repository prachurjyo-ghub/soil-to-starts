# Deterministic analysis boundary

Planned inputs are quality-checked, locally cached series plus explicit local soil/crop information. Planned outputs are season indicators, feasible rotations, comparative scores, assumptions, uncertainty, and source references. An LLM must not invent values or perform the calculations.

Before coding a rainfall-onset or growing-degree-day rule, document the crop, season, thresholds, look-ahead period, missing-data behavior, and local agronomic rationale. Test boundary cases and sensitivity. The build guide's sample onset function is not a validated implementation; see [`docs/METHODOLOGY.md`](../../docs/METHODOLOGY.md).
