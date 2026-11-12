# Mandatory now — strengthened MVP

Status: implementation specification approved for planning on 30 October 2026. These are team release commitments, not claims that every feature is individually required by NASA. None of the science/API features below is implemented merely because it appears here. [PROGRESS](PROGRESS.md) records actual evidence; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) holds deferred work.

## Product and boundaries

Build a published, farmer-friendly Bangladesh crop-rotation comparison tool. Start with one explicitly supported pilot region and a small source-reviewed crop-season catalogue. The existing `prototype/` remains the frontend. Calculation is deterministic in `src/compute/`; data preparation is in `src/acquire/`; `src/api/` serves checked local evidence. No runtime AI, chatbot, generated agronomic prose, trained ML, fertilizer tracking, nutrient-depletion simulation or numerical soil-restoration claim in the MVP.

Previous and current crops are separate input roles and may be identical. A completed recommended plan contains exactly three future main-crop steps after the current harvest. The existing-practice baseline may include repeated crops and fallow. Do not mistake three crops in one plan for three different strategies.

## Mandatory capabilities and acceptance

| ID | Capability | Smallest acceptable implementation | Owners / implementation gate |
| --- | --- | --- | --- |
| M01 | Pilot coverage and short intake | Required location via confirmed contained map pin or independent search across all 64 Bangladesh districts, above six visible ordered questions: current crop/empty field, availability date/window, previous history/first cultivation, usual sequence/no established rotation, explicit water access with seasonal limits, and explicit priority without defaults. Area/unit only for dependent outputs; scientific unknowns remain unknown. District selection does not imply scientific coverage. Latest intake contract supersedes pilot-only intake wording. | Fardin/Prachurjo; G0-CONTRACT, G1D |
| M02 | Authentic NASA evidence | A reproducible POWER rainfall/temperature record, raw and normalized bytes, units/time standard, missingness, grid support, checksum and processing version. Compare suitable declared periods; keep acquisition separate from requests. | Saim; G1A |
| M03 | Executable local agronomy | A small pilot catalogue with exact regional calendars, durations, essential soil/water requirements, source-backed sequence cautions and review status. About 6–10 records is a planning target, not permission to fill gaps. Obtain appropriate local agronomic review of active rules. | Maruf; G1B |
| M04 | Chronological constraint-first engine | Validate inputs, check coverage, generate candidate windows and exactly three future main-crop steps where supported; reject actual infeasibility before preferences. Distinguish unknown evidence from proven conflict. | Fardin, Saim/Maruf review; G2 |
| M05 | Three-strategy trade-off matrix | Assess existing practice plus two distinct supported alternatives emphasizing water and soil/rotation characteristics. Use the same start/end horizon, field and environmental assumptions. Keep an infeasible baseline visible with its reasons. Avoid clones and arbitrary filler plans. | Fardin/Prachurjo; G2, G3 |
| M06 | Quick intended-crop assessment | A small workspace card asks whether a proposed crop fits the selected planting period and known constraints. Reuse the same catalogue, checks and evidence as the planner; no separate classifier or live crop diagnosis. | Fardin/Prachurjo; G2, G3 |
| M07 | Evidence-linked decision ledger | Every pass, caution, exclusion and missing essential input has a stable reason/rule ID, source IDs and short EN/BN label. Explain why a candidate was not selected and which missing fact could resolve an undecided check. Do not claim that an unperformed counterfactual has been calculated. | Fardin/Maruf/Prachurjo; G0, G2, G3 |
| M08 | One historical stress replay | One predeclared dry/wet/hot historical comparison, using the same deterministic engine and fixed non-climate assumptions. Show changed checks/rankings and a small sensitivity result. No future forecast, invented yields or predicted crop-failure probability. | Saim/Fardin/Prachurjo; G4 |
| M09 | Reproducible result receipt | Return normalized request identity, source/catalogue/method versions and a stable content fingerprint. Basic JSON download and print view use the actual API result, its assumptions and limitations. No accounts, public farm links or PDF server required. A fingerprint proves reproducibility, not scientific certification. | Fardin/Prachurjo; G2, G3-REPORT |
| M10 | Compact evidence-first climate story | After G3 works, add four short home scenes: place/record → temperature/rainfall evidence → reviewed crop-calendar implication → Plan My Field. Reuse versioned chart payloads. Keep CTA/skip/reduced motion and sources accessible. No compulsory globe or heavy 3D. | Prachurjo, Saim/Hla/Nadim support; G3-STORY |
| M11 | Accessible integrated workspace | Phone, keyboard and EN/BN flow; three priority presets; result timeline/comparison; loading, invalid, incomplete, unavailable and map-failure states; clear data mode and coverage. Existing illustrative constants never enter scientific results. | Prachurjo; G1D, G3 |
| M12 | Verified publication and offline science | Tests for actual calculations/contracts and representative UI; local/domain review; persistent versioned evidence, refresh/failure visibility, deployment reproduction and anonymous public-access test. Rehearse scientific replay with external acquisition blocked. Browser asset/map offline scope is tested separately. | Fardin/team; G4, G5 |

## Farmer interaction

Use the six-question ordered form in [API_CONTRACT](API_CONTRACT.md), with district selection above it. All six core answers require meaningful values or their named explicit absence/fallow states; general unknown/placeholder answers do not satisfy them. Use progressive disclosure only for dependent or additional controls. A soil report, login, phone number, fertilizer history or exact irrigation volume is not compulsory just to explore. Area is required only for outputs that depend on it; validate explicit units and regional conversions. Ask more only when a missing fact affects a real check. Never assign an invented soil texture, pH or salinity.

Priority presets are **Save water**, **Soil protection / rotation diversity**, and **Balanced**. Freeze deterministic ranking orders with Maruf/Fardin in G0. Prefer visible criterion values/categories and stable tie-breaking to an unexplained total score. A numerical index is optional and needs documented component definitions/normalization; it is never a success percentage. Weights cannot rescue excluded candidates or turn unknowns into passes.

## Completion and evidence semantics

- A recommended plan is `complete` only when three chronological future main-crop steps and all essential checks have supporting evidence. Unknown essential conditions leave that plan incomplete; useful supported checks may still be displayed.
- The comparison bundle is `complete` only when the baseline is assessed and at least two distinct complete alternatives share the agreed horizon and essential evidence. A baseline can be assessed as infeasible. Fewer alternatives or missing baseline details produce an `incomplete` bundle, even if one alternative is individually complete.
- `unavailable` means required evidence/coverage is absent; `invalid_input` means the request cannot be interpreted consistently. No fixture-looking success replaces a failed evidence gate.
- Crop-family change is a screening consideration, not proof that every pest disappears. Soil-health output describes supported compatibility and management potential, not measured fertility restoration. Fertilizer/NPK/carbon forecasts are excluded.
- Existing crop monitoring, actual crop-distribution maps and future-weather prediction are separate from the intended-crop check. Historical replay assesses model behavior under recorded climate, not actual historical harvest outcomes.
- First implement one supported end-to-end comparison. Then add the quick check, receipt/story and replay through the existing gates. Additional sources or rich motion must not delay that first vertical slice.

## Release checklist and team sequence

G0-CONTRACT → parallel G1A/G1B/G1C/G1D → G2 → G3 → parallel G3-STORY/G3-REPORT → G4 → G5. Early media packages cover preparation only; final claims, recordings and exports belong to G5. Actual publication/submission needs current human authorization. A passing development-helper test does not validate agricultural outputs.

Future packages remain planned, dependent on accepted G5, and explicitly blocked pending a separate implementation-scope decision. Do not turn the future list into hidden MVP acceptance criteria.
