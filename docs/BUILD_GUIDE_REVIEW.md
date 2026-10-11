# Review of the supplied build guide

The attached `index (1).html` is an independent build guide for the 2026 NASA Space Apps Challenge Bangladesh. It is useful planning material, not the authoritative challenge statement or a source of validated agricultural results. This review focuses on its **Field Shift** section and shared architecture.

## Keep

| Guide idea | Use in Soil to Stars |
| --- | --- |
| Show a farmer-facing decision, not only charts | Put the chosen rotation, reasons, trade-offs, and assumptions ahead of charts. |
| Separate acquisition, compute, API, and frontend | Keep science reproducible and make every displayed value traceable. |
| Cache sourced data and rehearse offline | Use a small committed fixture and a visible data-mode label once real data is integrated. |
| State definitions and sensitivity | Document rainfall onset and crop heat thresholds before showing timing advice. |
| Bangla and phone-friendly presentation | Keep both languages and test actual wording with intended users. |
| Cite data and disclose AI use | Maintain `DATA_SOURCES.md`, `AI_USE.md`, and asset credits as work proceeds. |

## Adapt for the actual challenge

The guide's Field Shift page proposes a Bangladeshi rice **planting-window advisory**. The [official challenge](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/) asks for a **crop-rotation decision-support tool** that combines NASA Earth observations with local soil information, crop characteristics, and farmer priorities. The present frontend already demonstrates rotation comparison. Planting timing can become one evidence layer within that decision, after validation; it should not displace the main rotation workflow.

The guide's “Rajshahi Aman onset moved eleven days later” is a hypothetical demo moment. This repository has no historical POWER series or analysis that supports that number. Do not reuse it as a finding.

The guide's onset function claims to reject a dry spell longer than seven days, but the code only checks whether **any** day in the next seven exceeds 1 mm. It does not scan for a later dry spell or define a full follow-up period. A tested method needs a clear dry-day threshold, look-ahead length, missing-data rule, season bounds, and sensitivity analysis, with local agronomic review.

The guide splits 2001–2012 and 2013–2025 for a statistical comparison. That period is a design suggestion, not a decision we have validated. Soil-moisture and vegetation datasets also have different time coverage and spatial support from POWER; they cannot automatically be treated as one 25-year field-level record. See [data sources](DATA_SOURCES.md) and [methodology](METHODOLOGY.md).

## Repository choices

- `prototype/` serves as the guide's `web/` layer; keeping its path avoids disturbing the working app and its reference assets.
- `src/acquire/`, `src/compute/`, and `src/api/` mark the future boundaries. No placeholder backend is presented as working.
- No executable agent, MCP server, or skill files were copied. The possible agent role is documented in [ARCHITECTURE.md](ARCHITECTURE.md); add one only for a concrete use case with a constrained output contract.
- The guide's proposed event schedule and judging details are not carried into project instructions. Check the [official event site](https://www.spaceappschallenge.org/2026/) for current dates and submission requirements.
- The guide recommends Apache-2.0. The repository has no license yet; the team must select an OSI-approved license and review the supplied media's reuse terms before publication.
