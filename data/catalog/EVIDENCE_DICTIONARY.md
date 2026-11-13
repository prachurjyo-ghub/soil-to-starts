# Crop evidence data dictionary

Schema: `crop-evidence-research-v1`. This supplements the retained original extraction's fields; it does not replace the shared API contract. JSON null is an unknown/missing value, never zero or an inferred default. All JSON is UTF-8; JSONL has one record per line. The compatibility CSV uses UTF-8 with BOM; empty cells are missing, with reasons in adjacent fields.

## Original imported fields

Each original CSV row is an analytical source-calendar observation, not a unique week key or an independently reviewed agronomic rule.

| Field | Meaning / unit / unresolved interpretation |
| --- | --- |
| crop | Retained normalized common label; species unresolved unless separate taxonomy evidence supports it. |
| season | Printed/extracted season or rice-system label, including `Unspecified`; does not define planting dates. |
| region | BAMIS calendar region, distinct from administrative division. |
| district_coverage | Legacy semicolon list; exact membership checked against separate district mapping. Not district measurements. |
| standard_week | Printed/extracted integer label; not established as ISO week. Compressed/unparseable labels remain in unfiltered source entries/quarantine. |
| month | Existing normalized Gregorian label or null. Corrections use exact observed labels, never a week-derived month. |
| growth_stage | Extracted geometry-aligned stage label or null; no verified event duration implied. |
| duration_min_days / duration_max_days | Printed whole-calendar range, days. Origin, endpoint, maturity versus final harvest and clearance unresolved. |
| rainfall_mm | Printed rainfall normal, mm. Accumulation/averaging interval and reference period unknown. |
| temp_min_c / temp_max_c | Printed minimum/maximum temperature normal, degC. Absolute extrema versus mean daily extrema unknown. |
| temp_mean_c | Printed mean temperature normal, degC. Within-day and multi-year averaging conventions unknown. |
| humidity_mean_pct | Printed mean relative humidity, %. Sampling and aggregation conventions unknown. |
| sunshine_hours | Printed sunshine duration, hours. Daily/weekly accumulation unknown; not solar radiation. |
| wind_speed_kmh | Printed wind speed, km/hour. Height, mean/gust and aggregation convention unknown. |
| source_pdf | Relative path within original Dataset workspace. It is not a verified download URL. |
| source_page | Original 1-based PDF page number. |

Temperature/rain/humidity/wind/sunshine values are calendar normals. They are not crop preferences, tolerances, measured farm weather or projections. `weather_definitions.json` records the unit, printed meaning, missing period/statistic/spatial definitions and possible POWER counterpart for each weather field. Source page/table/cell links provide per-observation labels and units; a numerical extraction match is not semantic verification.

## Normalized files and relationships

| File | Identity / relationship / content |
| --- | --- |
| crops.json | `crop_id` hashes the original normalized common label. `folder_aliases` preserves associated external folder spellings/season labels, without making them species synonyms. `species` remains null; legacy taxonomy is separately retained. |
| regions.json | `region_id` hashes the BAMIS region label. Type explicitly says BAMIS calendar region. |
| district_memberships.json | One membership per district, preserving division, source basis and mapping status. `region_id` references regions. |
| source_artifacts.json | `source_id` is the original extraction document ID (filename plus path hash), with relative PDF path, SHA-256, bytes and extraction hash. Original download URL/date and rights remain unresolved unless a separate existing citation is supplied. Script artifact rows have `path`/`sha256` but no document identity. |
| calendar_inventory.json | All weather-bearing extracted tables. `calendar_id` hashes `source_id` + original `source_table_id`; page/table are original extraction references. Counts retained entries and links original exclusions. Original folder labels are not automatically validated printed identities. |
| calendars.json | Metadata for source tables with retained CSV rows: crop/region/season/rice-system label, duration, raw header/calendar label and inactive status. `species`, `variety`, duration events and clearance remain unknown. A distinct source table is not proof of an independent crop cycle. |
| source_entries.jsonl | One physical calendar column, including upstream rejected records. `source_entry_id` hashes document/table/column; `sequence_index` is original 1-based physical column, including gaps/nonstandard week labels. These are unfiltered evidence, not eligible recommendation entries. |
| entries.jsonl | Each retained CSV row has `entry_id`, `calendar_id`, original `csv_line` (header is line 1), raw week/month labels and nullable stage. A unique physical match uses table/column identity; an ambiguous analytical row uses a content fingerprint and all candidate source-entry IDs. Its identity can change if its analytical content is corrected. `sequence_index` is null for ambiguous matches; otherwise physical column order. `year_offset`/`cycle_offset` remain null for all entries. |
| weather_normals.jsonl | One weather bundle per retained `entry_id`. `values` holds seven numeric values/nulls; `source_values` holds raw values, metric labels, units, original cell IDs and extraction method. For ambiguous columns the first candidate's raw cells are explicitly labelled; every alternative remains in the frozen extraction. `missing_reasons` explains blanks. `definition_set_id` links common unresolved field semantics. |
| repeated_weeks.json | Stable repeated-key group with crop/season/region/week key and all retained entry IDs. No alternative removed or averaged. |
| lineage_audit.json | The 221 initially ambiguous analytical rows, all numeric candidate columns and their replayed original stages, selected physical entry IDs, and prior ambiguous `entry_id` values. Exact nonblank stage matches resolve import construction only; they do not validate source science. Use this mapping when migrating consumers of the first research snapshot. |
| coverage.json | Every collected crop/season combination crossed with all 14 regions. Lists source calendar IDs or explicit unavailable evidence. Absence is not inability to grow a crop. See inventory/quarantine for excluded calendars. |
| legacy_crop_candidates.json / candidate_evidence.json | Faithful copies of the existing six catalogue and 14 evidence records. Original source links, summaries, dates, operators and scope remain research evidence, not executable rules. |
| page_candidates.json | Three additional inactive Mymensingh Pointed Gourd evidence statements with original PDF/pages, qualified preferred conditions and explicit gaps. No implied independent approval. |
| rule_compatibility.json / .csv | One row per candidate statement. Stable rule ID, crop/calendar/management applicability, required metric, unit, stage/time text, spatial scope, URL or local PDF/page, evidence state, potential counterpart, transformation and missing information. `evaluable_now=false` is explicit. Legacy web-source page number is null because no PDF page applies/was recorded. |
| source_reviews.json | Specific assistant inspections of original local PDFs and published banana source; findings, unresolved interpretation and next owner. Not human approval. |
| month_corrections.json | 106 row-specific original/corrected month values, source/page/week, exact CSV line, reason and evidence reference. Existing normalization is preserved, not newly certified. |
| quarantine.json | Preserved upstream excluded records, correction notes and processing counts. Full originals remain in `evidence_inputs/documents.jsonl.gz`. Legacy audit lacks row identities for all 21 analytically removed records; do not invent them. |
| qa.json | Measured counts, missingness, checks and limitations. Count of reviewed executable rules remains zero. |
| receipt.json | SHA-256 of source inputs and generated outputs. Each input declares its hash method: text normalizes CRLF to LF, compressed binary uses exact bytes. Output hashes use exact bytes, protected by scoped Git attributes. PDF/source artifact hashes remain byte-exact. Does not hash itself; no runtime timestamp is included, so rebuilds are deterministic. |

## Frozen extraction

`evidence_inputs/documents.jsonl.gz` is deterministic gzip of all original extracted document records. Each document preserves `source_pdf`, SHA-256, full page text, table row matrices and cells, numeric weather observations, original labels, coordinates, extraction methods and issues. `table_id`, `cell_id`, `week_cell_id`, `page_number` and `calendar_column` are source references; source table/cell numbers are 1-based. Bounding boxes are PDF points, origin at upper left. Full source values and exclusions must be inspected there before activating anything.

Confidence is qualitative: preserved upstream extraction method plus **unreviewed** interpretation. No numerical confidence was estimated. Rights, acquisition dates, climate reference periods, source aggregation and essential unknown agronomy retain missing reasons; missing source metadata is not filled from PDF creation dates, folder names or NASA conventions.
