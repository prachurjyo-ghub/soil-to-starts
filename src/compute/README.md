# Deterministic analysis boundary

Implemented: `assessment.py` joins farmer inputs to preserved crop/weather evidence; `metric_contract.py` defines canonical metrics/units; `weather.py` reads exact historical daily windows; `rule_engine.py` supplies tested, inactive-by-default threshold/operation/scoring primitives. These are not an activated three-crop planner.

`climate_history.py` produces descriptive annual weather summaries and equal ten-year period comparisons for the static UI payload. It preserves incomplete years and uses day-weighted temperature means. This is not a crop-risk, suitability or rotation engine; those outputs remain planned below.

Planned inputs are quality-checked, locally cached series plus explicit local soil/crop information. Planned outputs are season indicators, feasible rotations, comparative scores, assumptions, uncertainty, and source references. An LLM must not invent values or perform the calculations.

Before coding a rainfall-onset or growing-degree-day rule, document the crop, season, thresholds, look-ahead period, missing-data behavior, and local agronomic rationale. Test boundary cases and sensitivity. The build guide's sample onset function is not a validated implementation; see [`docs/METHODOLOGY.md`](../../docs/METHODOLOGY.md).

Mandatory planning scope includes existing baseline/fallow, common-horizon alternatives, shared intended-crop checks, a source-linked decision ledger and one historical replay. Prior/current IDs may match. Rankings use supported indicators; aggregate scores are optional. No fertilizer/NPK/carbon restoration model in MVP. See [scope](../../docs/MVP_SCOPE.md) and [contract](../../docs/API_CONTRACT.md).
