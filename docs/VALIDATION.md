# Validation and release plan

Status: development-helper tests exist; scientific/API/user-study checks below are planned acceptance, not passed results. Read [MVP_SCOPE](MVP_SCOPE.md); [future scope](FUTURE_ROADMAP.md) is not a release dependency.

| Slice | Required evidence before acceptance |
| --- | --- |
| Climate | Expected dates/leap years; fill values; units/time standard; missingness; grid/coordinate support; reproducible aggregation/checksum; actual coverage and suitable comparison periods. |
| Catalogue | Exact local sources, regional applicability, crop-season/variety duration, essentiality and source-backed soil/water/host rules; appropriate local review of active pilot rules. Unknown differs from conflict. |
| Intake | Equal previous/current crop IDs accepted; baseline distinct from history; fallow/repeats; available date, units, optional soil/equipment and water/preset handling; unsupported region states. |
| Engine | Cross-year windows, overlaps/preparation, constraint-first behavior, same horizon, exactly three future main crops per complete alternative, no fillers/forced distinct crop names, deterministic ranking/ties. |
| Comparison | Baseline assessed even if infeasible; two distinct supported alternatives for complete bundle; one complete plan can exist in incomplete bundle; essential unknowns never silently pass. |
| Quick assessment / check ledger | Planner and intended-crop results agree on identical crop/window; reason/rule/source IDs trace to actual checks; no generated advice or invented missing-information counterfactual. |
| Replay | Predeclared historical stress/period, non-climate assumptions fixed, calendar/cross-year/leap-day alignment, same engine, usable-year counts and missingness; changed checks/ranks reproducible; not a forecast or actual crop-failure observation. |
| Receipt | Canonical input/source/catalogue/method identity; timestamp separation; same inputs reproduce fingerprint; changed evidence changes it; JSON/print preserve status, units, unknowns and limits. |
| UI/story | Actual API values only; correct bundle/plan states; scientific/demo separation; source/failure/loading/coverage views; versioned story arrays; no asserted shift without evidence; CTA/skip/location continuity; phone/keyboard/EN-BN/reduced motion and print. |
| Offline science | Verified local fixtures; OFFLINE=1 blocks external acquisition/scientific upstream calls. Local browser-to-API requests may still operate. Absent coverage returns unavailable, not synthetic fallback. Test map and app assets separately. |
| Public release | Authorized deployment with persistent evidence, restart/data-refresh/failure behavior, anonymous access and reproducible setup; no unsupported national/soil/forecast claim. |
| Media/submission | Final scientific footage/narration follows G4 review; rights/credits, AI disclosure, real contributions, current portal requirements and accurate release/submission state. |

## Pilot and unknowns

Validate one supported regional pilot first. Rajshahi/Barind, Sunamganj/Haor and Satkhira/coastal remain possible contexts, not a requirement to fabricate three validated regions. Other locations explicitly remain unsupported or incomplete until source-reviewed. A regional soil estimate is not a field measurement; fertilizer tracking, nutrient depletion and numerical restoration are outside MVP.

A useful incomplete result can show supported checks and identify an essential unknown. It must not be described as a fully checked complete recommendation. No quantified irrigation, yield, nutrient or confidence result without an appropriate reviewed method and inputs.

## Review, offline and release boundaries

Unit/contract/scientific tests and appropriate domain review are distinct from development-helper checks and teammate software review. Record actual commands/revisions/results, representative cases, reviewer scope and unresolved limitations. Local checklist ticks do not establish independent approval, main-branch delivery or agronomic certification.

Prepared scientific evidence can work without NASA requests while browser assets/fonts/maps still need connectivity. A fully offline public website needs separate caching and browser tests; it remains future scope. Test the local rehearsal configuration with venue internet disconnected, not by blocking the local API itself. Map caching must respect provider rights.

G5 records accepted MVP release and prepares a truthful submission handoff. Actual submission is a separately authorized action, not a prerequisite that automatically activates all future development. Future packages retain explicit activation blockers. Run checks appropriate to changes; no frontend build is required merely for an unchanged application's planning documents.
