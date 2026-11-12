# Future implementation — after the accepted MVP

Status: deferred options, not current release requirements or completed features. [MVP_SCOPE](MVP_SCOPE.md) is the mandatory-now context. Each future package depends on accepted G5 and retains an explicit activation blocker. G5 completion alone does not authorize or start any of these tracks. Choose one bounded issue, evidence needs and owner before removing its blocker.

| Track / task | What may be added | What must exist first | Acceptance before claiming support |
| --- | --- | --- | --- |
| FUT-COVERAGE | More Bangladesh regions/crops; varieties; fruits/perennials and long-duration paths such as sugarcane | Exact local sources, dates/management horizon, reviewed constraints and representative cases | New coverage passes the same evidence gates; no universal defaults. Long-duration crops are not squeezed into three short seasons. |
| FUT-DATA | IMERG rainfall cross-check, SMAP moisture, vegetation evidence and justified vulnerability overlays | A specific unresolved decision question, product/version/rights, overlapping periods, QA and spatial/temporal alignment | Demonstrate the added source's effect and limits. Surface moisture is not nutrients/pH; NDVI alone is not crop identity; resampling creates no finer field truth. |
| FUT-EXPERIENCE | Richer scrollytelling/3D, voice, richer reports/calendar exports, saved plans and full browser offline installation | Accepted core/story/receipt, asset rights, usability need and device/network budget | Mobile/keyboard/EN-BN/reduced motion remain usable; app assets and permitted maps are actually tested offline. Mandatory basic print/JSON receipts are already in MVP. |
| FUT-SCENARIOS | Multiple replays, custom scenario sliders and carefully sourced climate projections | Reviewed scenario semantics, exact model/pathway/period/baseline/ensemble, uncertainty and comparability method | Clearly separate recorded observations, hypothetical changes and projections; no precise future weather or unvalidated yield claim. MVP requires only one historical replay. |
| FUT-SOIL | Optional fertilizer records, nutrient budgets and richer soil-state/carbon modeling | Explicit team choice; actual input/removal/management data, units/methods, local parameterization and qualified review | Unknown inputs remain unknown; account consistently for residues/losses; budgets do not become laboratory measurements. This track is not promised or required. |
| FUT-OPERATIONS | Optional accounts/sync, economic information, market/forage extensions, sensors and notifications | A selected farmer need, consent/storage approach where relevant, real source permissions/costs and maintenance plan | Pilot the selected service separately; validate any financial/sensor claims. Do not make every listed service one compulsory project. |
| FUT-ASSIST | Optional conversational/voice explanation or developer-independent runtime agents | Explicit new scope, useful task, source-grounded tool contract, evaluation and operating budget | Never perform scientific arithmetic in an LLM; evaluate unsupported claims and offline/error paths. A useful release does not require this track. |

## How to activate a future track

1. Confirm the MVP is accepted and maintain its regression fixtures.
2. Select the smallest useful extension, owner, exact files, source/input needs and measurable acceptance. Obtain authorization to implement that extension.
3. Update the chosen task's blocker and true dependencies through review; create smaller child work packages if needed. Do not clear every future blocker together.
4. Reuse acquisition/compute/API/frontend boundaries and the contribution/check/review workflow.
5. Publish only tested coverage and explain any changed scientific assumptions. Keep discussion out of command logs; log actual implementation commands when implementation is authorized.

Deferred research is not active product work. None of the optional tracks is a condition for demonstrating the MVP's three-strategy comparison.
