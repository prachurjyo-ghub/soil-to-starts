# Field Shift methodology plan

This is a design plan. The current frontend has illustrative ranking logic; it does not run the scientific workflow below.

## Decision and evidence

The target decision is: **which crop rotation is feasible and preferable for this field under the farmer's constraints and priorities, and why?** A useful result names at least one rotation, shows what excluded alternatives, and explains the water, soil, and climate trade-offs. The user can inspect provenance and change priorities without changing the underlying observations.

Inputs should be separated by type:

1. **Measured or documented local inputs:** soil tests, irrigation access, crop calendars, field history, and crop requirements, each with source and date.
2. **NASA regional context:** rainfall, temperature, soil moisture, and vegetation products with product/version, scale, and quality information.
3. **Farmer preferences:** explicit weights or priorities. These affect ranking, not the observed data or agronomic feasibility rules.

## Proposed deterministic pipeline

```text
Raw NASA/local inputs → quality checks → season indicators
                    → feasible rotation generation → comparison
                    → explanation + assumptions + provenance
```

- **Quality checks:** missing dates, fill values, units, time standard, spatial coverage, and product quality flags. Fail visibly if an essential input is absent.
- **Season indicators:** rainfall onset, rainfall totals and dry spells, growing degree days, and possibly soil moisture/vegetation checks. Define crop and district seasons before calculating.
- **Feasibility:** apply locally reviewed crop calendar, water, soil, and sequence constraints. Do not allow a high preference score to override an infeasible rotation.
- **Comparison:** normalize and document criteria, show the contribution of each criterion and the impact of changing farmer weights. Avoid a single unexplained “best” score.
- **Uncertainty:** evaluate threshold sensitivity, grid-to-field mismatch, missing data, and rank stability. Use local observations or historical replay where available.

## Rainfall-onset method to specify before implementation

The supplied guide suggests the first seven-day rainfall window reaching 20 mm, followed by a dry-spell check. These numbers are **candidate parameters**, not agreed local thresholds. Its code does not implement the dry-spell condition stated in its docstring. Before adding `src/compute/agro.py`, agree and document:

- search season and how a calendar year is assigned;
- rainfall threshold, rolling-window length, dry-day threshold, maximum subsequent dry spell, and follow-up length;
- behavior for incomplete follow-up windows and missing days;
- treatment of multiple apparent onsets and district/grid variation;
- sensitivity at nearby thresholds and comparison with ground observations.

If comparing historical onset distributions, show the year-level points, period definitions, sample sizes, and a defensible effect size. A significance test alone does not establish a safe planting-window change. Do not display the guide's example “11 days later” as a measured result.

## Growing degree days

Specify the crop-specific base temperature and temperature convention with an agronomist. A common candidate calculation is `max(0, (Tmax + Tmin) / 2 − Tbase)` for each day, accumulated over a defined crop stage; this is not yet a validated rice or rotation rule for the pilot. Units are degree-days (°C·day). Compare against local phenology and state how missing temperatures are handled.

## Minimum validation before connecting the frontend

- Unit tests for science functions, including missing data and seasonal boundaries.
- Sensitivity results for chosen thresholds and preference weights.
- A sourced pilot dataset with a reproducible acquisition/processing command and manifest.
- At least one comparison against local agronomic knowledge or observations.
- Bangla and English review of the resulting advice on a phone.

The current `prototype/` scores are useful for testing interface flows, but no one should treat them as validated crop recommendations.
