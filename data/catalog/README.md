# Candidate crop evidence catalog

The multi-region collection is now preserved separately in [EVIDENCE_PACKAGE.md](EVIDENCE_PACKAGE.md), with normalized context, source-table identities, quarantine, rebuild scripts and candidate-rule compatibility. It retains all available regions without prioritizing Rajshahi. The existing files below remain unchanged and inactive; the research package does not expand executable recommendation coverage or modify the API contract.

[Source-semantics review](source_review/README.md) compares every collected Lentil region and audits all 318 extracted documents for definition leads. Source gaps and interval wording remain inactive evidence; no dates or normal-weather aggregation are inferred.

`rajshahi_crop_evidence_catalog.csv` is Maruf's first bounded G1B research package. It contains six inactive candidate records for the BAMIS Rajshahi calendar region: Aman rice, Boro rice, wheat, lentil, mustard and Kharif-1 mungbean.

The records preserve the four-district BAMIS coverage, printed crop duration, complete standard-week span, source-PDF path and taxonomy source. Each `calendar_source_pdf` is relative to the user-provided `D:\Workplace\Nasa Space Apps\Dataset` folder; the PDFs are not copied into this repository. The week span describes the whole printed crop calendar; it is not an exact sowing window. `proposed_record_id` values are working research identifiers until Fardin supplies or approves the executable rule schema.

Every record has source readiness `candidate` and remains `inactive_candidate`. The BAMIS crop-weather calendars do not establish soil, water or crop-sequence constraints. `rajshahi_candidate_rule_evidence.csv` therefore records later Bangladesh-source research separately: it contains candidate soil/drainage guidance, conditional irrigation management, variety-specific rice guidance and complete cropping-pattern examples. None is an executable rule. Lentil carries `source_calendar_month_conflict` because its printed month row conflicts with its standard weeks. Mustard carries `species_unresolved`. These records must not enter recommendations until the evidence scope is reviewed and converted to Fardin's agreed rule format.

Taxonomy references support crop identity, family and candidate life-cycle classification. They do not establish Bangladesh regional suitability. The BAMIS calendar and taxonomy pages must remain separate evidence roles.

## Candidate rule evidence

`rajshahi_candidate_rule_evidence.csv` is an evidence ledger, not an engine input. Its `normalized_*` fields are proposed research mappings so reviewers can inspect the intended meaning; they are not an agreed schema. Every row is `candidate` and `inactive_candidate`.

The evidence deliberately preserves scope:

- AIS soil descriptions are recorded as preferred or required management conditions without inventing numeric texture, drainage, pH or salinity thresholds.
- Irrigation schedules remain management guidance because the current product contract has no agreed conversion from event counts to field water availability.
- BRRI Aman and Boro water guidance remains BR3-variety-specific and cannot activate the generic rice records.
- Regional sequences remain complete patterns. They cannot be split into universally allowed crop-to-crop transitions, and several require Aus rice or named short-duration varieties absent from this bounded catalog.
- The mustard irrigation evidence is specific to a zero-tillage practice, while the BAMIS mustard species is unresolved.

Activation requires Fardin to approve enums, operators and failure behavior; Saim to align any rainfall or water trigger with defined climate units; and Maruf to verify that source scope has not been generalized. Until then, unsupported soil or water inputs must still yield incomplete/unavailable behavior rather than a recommendation.
