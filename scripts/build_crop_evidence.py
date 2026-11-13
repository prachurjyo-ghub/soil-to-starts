"""Build a deterministic, inactive research package from preserved local evidence.

No network calls. Calendar identities describe extracted source tables, not
reviewed planting cycles. A week label is never converted to a date.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import tempfile
from crop_evidence_lineage import stages, stage_for_week, select_stage_candidates

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data/catalog/evidence_inputs"
DEFAULT_OUTPUT = ROOT / "data/catalog/normalized"
METRICS = {
    "rainfall_mm": ("rainfall", "mm", "PRECTOTCORR"),
    "temp_min_c": ("minimum_temperature", "degC", "T2M_MIN"),
    "temp_max_c": ("maximum_temperature", "degC", "T2M_MAX"),
    "temp_mean_c": ("mean_temperature", "degC", "T2M"),
    "humidity_mean_pct": ("mean_relative_humidity", "%", None),
    "sunshine_hours": ("sunshine_duration", "hours", None),
    "wind_speed_kmh": ("wind_speed", "km/hour", None),
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def identity(prefix, *parts):
    # Source/table/column identity survives scientific-value corrections.
    return prefix + "-" + hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()[:20]


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write_utf8(path, text):
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def number(value):
    return None if value == "" or value is None else float(value)


def input_fingerprint(path):
    raw = path.read_bytes()
    binary = path.suffix == ".gz"
    data = raw if binary else raw.replace(b"\r\n", b"\n")
    return dict(sha256=hashlib.sha256(data).hexdigest(),
                method="exact binary bytes" if binary else "UTF-8 source bytes with CRLF normalized to LF")


def validate_rows(rows, mapping):
    if len(mapping) != 64 or len({r["district"] for r in mapping}) != 64:
        raise ValueError("District mapping must contain exactly 64 unique memberships")
    regions = {r["bamis_region"] for r in mapping}
    memberships = defaultdict(set)
    for record in mapping:
        memberships[record["bamis_region"]].add(record["district"])
    for row in rows:
        if row["region"] not in regions or set(row["district_coverage"].split("; ")) != memberships[row["region"]]:
            raise ValueError("Region or district coverage mismatch")
        week = int(row["standard_week"])
        if not 1 <= week <= 53:
            raise ValueError("Invalid standard-week label; no ISO interpretation implied")
        lo, hi = number(row["duration_min_days"]), number(row["duration_max_days"])
        if lo is None or hi is None or not 0 < lo <= hi:
            raise ValueError("Invalid duration range")
        for key in METRICS:
            value = number(row[key])
            if value is not None and not math.isfinite(value):
                raise ValueError("Non-finite weather value")
            if value is not None and key in ("rainfall_mm", "sunshine_hours", "wind_speed_kmh") and value < 0:
                raise ValueError("Negative nonnegative measure")
        humidity = number(row["humidity_mean_pct"])
        if humidity is not None and not 0 <= humidity <= 100:
            raise ValueError("Invalid relative humidity")
        if not number(row["temp_min_c"]) <= number(row["temp_mean_c"]) <= number(row["temp_max_c"]):
            raise ValueError("Temperature order conflict")


def build(output):
    rows = read_csv(ROOT / "assets/crop_planning_dataset.csv")
    mapping = read_csv(ROOT / "assets/bamis_region_district_mapping.csv")
    validate_rows(rows, mapping)
    report = json.loads((ROOT / "assets/crop_planning_dataset_report.json").read_text(encoding="utf-8-sig"))
    with gzip.open(INPUTS / "documents.jsonl.gz", "rt", encoding="utf-8") as stream:
        docs = [json.loads(line) for line in stream]
    by_pdf = {doc["source_pdf"]: doc for doc in docs}
    # Index the extraction by original physical column, not by sorted CSV week.
    columns = defaultdict(dict)
    tables, table_weather = {}, defaultdict(list)
    for doc in docs:
        for table in doc["tables"]:
            tables[table["table_id"]] = table
        for obs in doc["weekly_weather"]:
            table_weather[obs["table_id"]].append(obs)
            key = (doc["source_pdf"], obs["page_number"], obs["standard_week"])
            column = (obs["table_id"], obs["calendar_column"])
            columns[key].setdefault(column, {})[obs["metric"]] = obs
    stage_by_column = {}
    for table_id, observations in table_weather.items():
        table = tables[table_id]
        stage_cells = stages(table, observations)
        cells = {cell["cell_id"]: cell for cell in table["cells"]}
        for obs in observations:
            stage_by_column[(table_id, obs["calendar_column"])] = stage_for_week(stage_cells, cells[obs["week_cell_id"]]["bbox"])
    entries, weather, calendars, lineage_audit = [], [], {}, []
    used_columns, repetitions = set(), defaultdict(list)
    for line, row in enumerate(rows, 2):
        doc = by_pdf[row["source_pdf"]]
        key = (row["source_pdf"], int(row["source_page"]), int(row["standard_week"]))
        candidates = []
        for column, observations in columns[key].items():
            if all(number(row[field]) == observations.get(metric, {}).get("value_numeric")
                   for field, (metric, _, _) in METRICS.items()):
                candidates.append((column, observations))
        if not candidates or len({c[0][0] for c in candidates}) != 1:
            raise ValueError(f"Ambiguous extraction lineage at CSV line {line}: {len(candidates)} matches")
        numeric_candidates = candidates
        if len(candidates) > 1:
            candidates = select_stage_candidates(candidates, row["growth_stage"], stage_by_column)
        stage_resolved = len(numeric_candidates) > 1 and len(candidates) == 1
        (table_id, column), observations = candidates[0]
        ambiguous = len(candidates) > 1
        physical_refs = [dict(source_table_id=ref[0], calendar_column=ref[1],
                              source_entry_id=identity("source-entry", doc["document_id"], ref[0], ref[1])) for ref, _ in candidates]
        lineage_key = (table_id, tuple(c[0][1] for c in candidates), row["growth_stage"])
        if lineage_key in used_columns:
            raise ValueError("Two retained rows map to the same physical source column")
        used_columns.add(lineage_key)
        calendar_id = identity("calendar", doc["document_id"], table_id)
        entry_id = identity("entry", calendar_id, "ambiguous", tuple(row.items())) if ambiguous else identity("entry", calendar_id, column)
        if len(numeric_candidates) > 1:
            lineage_audit.append(dict(csv_line=line, calendar_id=calendar_id, entry_id=entry_id,
                                      previous_entry_id=identity("entry", calendar_id, "ambiguous", tuple(row.items())),
                                      imported_growth_stage=row["growth_stage"] or None,
                                      numeric_candidates=[dict(source_table_id=ref[0], calendar_column=ref[1],
                                                               source_entry_id=identity("source-entry", doc["document_id"], ref[0], ref[1]),
                                                               extracted_stage=stage_by_column[ref]) for ref, _ in numeric_candidates],
                                      selected_source_entry_ids=[r["source_entry_id"] for r in physical_refs],
                                      status="unique original-stage geometry match" if stage_resolved else "unresolved; all numeric candidates retained",
                                      method="Replay preserved upstream stage geometry; exact nonblank label match; no scientific interpretation"))
        first = next(iter(observations.values()))
        table = tables[table_id]
        metadata = dict(calendar_id=calendar_id, source_id=doc["document_id"], source_table_id=table_id,
                        source_page=key[1], crop_id=identity("crop", row["crop"]), crop_label=row["crop"],
                        region_id=identity("bamis-region", row["region"]), region_label=row["region"],
                        season_label=row["season"], rice_system_label=row["season"] if row["crop"] == "Rice" else None,
                        variety=None, species=None, missing_reasons={"variety": "not established", "species": "not reviewed"},
                        duration_min_days=number(row["duration_min_days"]), duration_max_days=number(row["duration_max_days"]),
                        duration_origin=None, duration_endpoint=None, clearance_days=None,
                        duration_event_status="unresolved: whole printed calendar; not final-harvest or clearance evidence",
                        source_header=table["rows"][0], calendar_label_raw=first["calendar_label_raw"],
                        identity_status="source_table; cycle/variant interpretation unreviewed", activation_status="inactive_candidate")
        if calendar_id in calendars and calendars[calendar_id] != metadata:
            raise ValueError("Inconsistent metadata within a source table")
        calendars[calendar_id] = metadata
        entry = dict(entry_id=entry_id, calendar_id=calendar_id, sequence_index=None if ambiguous else column,
                     source_column_candidates=physical_refs,
                     lineage_status="ambiguous identical numeric columns" if ambiguous else ("unique numeric and original-stage geometry match" if stage_resolved else "unique numeric column match"),
                     sequence_basis="original calendar_column (1-based); retained gaps preserved",
                     csv_line=line, standard_week=int(row["standard_week"]), week_label_raw=first["week_label_raw"],
                     month=row["month"] or None, month_label_raw=first["month_label_raw"],
                     growth_stage=row["growth_stage"] or None, cycle_offset=None, year_offset=None,
                     missing_reasons={k: "blank in preserved CSV; source interpretation not supplied" for k in ("month", "growth_stage") if not row[k]},
                     extraction_confidence="unreviewed; geometry-based extraction, not a probability")
        entries.append(entry)
        weather.append(dict(entry_id=entry_id, values={k: number(row[k]) for k in METRICS},
                            source_value_status="first candidate shown; all candidate cells retained in frozen extraction" if ambiguous else "unique column",
                            source_values={field: {k: observations.get(metric, {}).get(k) for k in
                                                  ("value_raw", "metric_label_raw", "unit", "cell_id", "extraction_method")}
                                           for field, (metric, _, _) in METRICS.items()},
                            missing_reasons={k: "blank in preserved CSV/extraction" for k in METRICS if not row[k]},
                            definition_set_id="bamis-printed-normal-unresolved-v1"))
        repetitions[(row["crop"], row["season"], row["region"], row["standard_week"])].append(entry_id)
    ordered = sorted(entries, key=lambda e: (e["calendar_id"], e["sequence_index"] or 100000, e["entry_id"]))
    conflict_groups = [dict(group_id=identity("repetition", *key), key=list(key), entry_ids=values,
                            status="unresolved source alternatives; retained, never averaged or deduplicated")
                       for key, values in sorted(repetitions.items()) if len(values) > 1]
    raw_calendars, source_entries = [], []
    for doc in docs:
        physical = {}
        for obs in doc["weekly_weather"]:
            physical.setdefault((obs["table_id"], obs["calendar_column"]), obs)
        for (table_id, column), obs in sorted(physical.items()):
            source_entries.append(dict(source_entry_id=identity("source-entry", doc["document_id"], table_id, column),
                                       calendar_id=identity("calendar", doc["document_id"], table_id),
                                       source_id=doc["document_id"], source_table_id=table_id,
                                       source_page=obs["page_number"], sequence_index=column,
                                       week_label_raw=obs["week_label_raw"], standard_week=obs["standard_week"],
                                       month_label_raw=obs["month_label_raw"], year_offset=None, cycle_offset=None,
                                       status="unfiltered source column; consult quarantine before use"))
        weather_tables = {obs["table_id"] for obs in doc["weekly_weather"]}
        for table in doc["tables"]:
            if table["table_id"] not in weather_tables:
                continue
            cid = identity("calendar", doc["document_id"], table["table_id"])
            raw_calendars.append(dict(calendar_id=cid, source_id=doc["document_id"], source_pdf=doc["source_pdf"],
                                      source_page=table["page_number"], source_table_id=table["table_id"],
                                      crop_folder=doc["crop_folder"], region=doc["region"],
                                      retained_entries=sum(e["calendar_id"] == cid for e in entries),
                                      status="partially_or_fully_retained" if cid in calendars else "no_retained_entries",
                                      exclusion_records=[r for r in report["excluded_records"] if r["source_pdf"] == doc["source_pdf"]
                                                         and r.get("source_page", table["page_number"]) == table["page_number"]]))
    legacy = read_csv(ROOT / "data/catalog/rajshahi_crop_evidence_catalog.csv")
    evidence = read_csv(ROOT / "data/catalog/rajshahi_candidate_rule_evidence.csv")
    legacy_by_id = {r["proposed_record_id"]: r for r in legacy}
    compatibility = []
    for rule in evidence:
        record = legacy_by_id[rule["proposed_record_id"]]
        compatibility.append(dict(rule_id=rule["rule_evidence_id"], proposed_record_id=rule["proposed_record_id"],
                                  crop_calendar_applicability=dict(crop=record["crop_name_en"], season=rule["applicability_season"],
                                                                   variety=rule["applicability_variety"], management=rule["management_context"],
                                                                   calendar_ids=[c["calendar_id"] for c in calendars.values() if
                                                                                 c["crop_label"] == record["crop_name_en"] and
                                                                                 c["region_label"] == record["bamis_region"] and
                                                                                 c["season_label"] == record["season_label"]]),
                                  required_metric=rule["normalized_attribute"], unit=rule["unit"],
                                  time_stage_interval=rule["source_summary"], spatial_applicability=rule["applicability_geography"],
                                  source_url=rule["source_url"], source_page=None, evidence_status=rule["activation_status"],
                                  nasa_counterpart=None, needed_transformation="No direct mapping: soil, irrigation management or full-pattern evidence is not POWER precipitation/temperature",
                                  missing_information=rule["blocking_reason"] + " " + rule["limitations"],
                                  evaluable_now=False))
    page_candidates = json.loads((INPUTS / "reviewed_page_candidates.json").read_text(encoding="utf-8"))
    for rule in page_candidates:
        compatibility.append(dict(rule, crop_calendar_applicability=[c["calendar_id"] for c in calendars.values()
                                                                    if (c["crop_label"], c["region_label"], c["season_label"]) ==
                                                                    (rule["crop"], rule["region"], rule["season"])],
                                  spatial_applicability=rule["region"], source_id=by_pdf[rule["source_pdf"]]["document_id"]))
    coverage = []
    for crop in sorted({r["crop"] for r in rows}):
        for season in sorted({r["season"] for r in rows if r["crop"] == crop}):
            for region in sorted({r["bamis_region"] for r in mapping}):
                matches = [c for c in calendars.values() if (c["crop_label"], c["season_label"], c["region_label"]) == (crop, season, region)]
                coverage.append(dict(crop=crop, season=season, bamis_region=region,
                                     calendar_ids=[c["calendar_id"] for c in matches],
                                     evidence_status="collected_context_only" if matches else "unavailable; not evidence of unsuitability"))
    definitions = []
    for field, (metric, unit, nasa) in METRICS.items():
        definitions.append(dict(field=field, source_metric=metric, unit=unit, meaning="printed calendar normal; not crop tolerance",
                                time_interval=None, statistic="printed " + metric + "; calculation convention unresolved",
                                reference_period=None, spatial_support="BAMIS calendar region; stations/area weighting unresolved",
                                counterpart=nasa, evaluable_now=False,
                                required_transform=("Source-defined accumulation over matching days" if field == "rainfall_mm" else
                                                    "Match source statistic and days; do not substitute mean daily extrema for absolute extrema") if nasa else "Unavailable in current four-parameter POWER package",
                                missing_information="Source week definition, aggregation/statistic, reference period and spatial method; no ISO-week assumption",
                                definition_set_id="bamis-printed-normal-unresolved-v1"))
    crops = [dict(crop_id=identity("crop", label), original_label=label,
                  folder_aliases=sorted({doc["crop_folder"] for doc in docs if doc["source_pdf"] in
                                         {r["source_pdf"] for r in rows if r["crop"] == label}}),
                  species=None, species_status="unreviewed; see separate existing taxonomy candidates")
             for label in sorted({r["crop"] for r in rows})]
    artifacts = json.loads((INPUTS / "source_artifacts.json").read_text(encoding="utf-8"))
    for artifact in artifacts:
        links = sorted({r["calendar_source_url"] for r in legacy if r["calendar_source_pdf"] == artifact["path"]})
        if links:
            artifact["source_urls_from_existing_catalog"] = links
            artifact["url_status"] = "preserved existing citation; not reverified by builder"
    qa = dict(schema_version="crop-evidence-research-v1", activation_status="inactive_candidate",
              input_rows=len(rows), crops=len(crops), regions=len({r["region"] for r in rows}),
              source_pdfs_in_csv=len({r["source_pdf"] for r in rows}), source_documents=len(docs),
              retained_calendars=len(calendars), inventoried_calendars=len(raw_calendars),
              entries=len(entries), source_entries=len(source_entries), repeated_week_groups=len(conflict_groups),
              ambiguous_entry_lineage=sum(e["sequence_index"] is None for e in entries),
              stage_resolved_entry_lineage=sum(r["status"] == "unique original-stage geometry match" for r in lineage_audit),
              missing_values={k: sum(not r[k] for r in rows) for k in rows[0]},
              month_corrections=len(json.loads((INPUTS / "month_corrections.json").read_text(encoding="utf-8"))),
              candidate_evidence=len(evidence) + len(page_candidates), executable_rules=0,
              checks=["Every retained row matched to a source table and numeric weather values; ambiguous columns explicitly retained",
                      "64 distinct district mappings; exact regional membership and finite numeric/range checks",
                      "No week-to-date conversion, cycle offsets, regional substitution or rule activation"],
              limitations=["Source climate period, week standard and aggregation unresolved",
                           "PDF hashes verified at import; original PDFs remain external with rights/download-log gaps",
                           "Original upstream exclusions/deduplication retained in audit, not repeated on normalized entries",
                           "Source-table identity is provisional; human cycle/variant review pending",
                           "Whole-corpus extraction snapshot preserves context, not verification of every scientific statement"])
    output.mkdir(parents=True, exist_ok=True)
    outputs = {"crops.json": crops, "calendars.json": sorted(calendars.values(), key=lambda c: c["calendar_id"]),
               "regions.json": [dict(region_id=identity("bamis-region", r), original_label=r, type="BAMIS calendar region") for r in sorted({m["bamis_region"] for m in mapping})],
               "district_memberships.json": [dict(r, region_id=identity("bamis-region", r["bamis_region"])) for r in mapping],
               "calendar_inventory.json": raw_calendars, "coverage.json": coverage, "repeated_weeks.json": conflict_groups,
               "candidate_evidence.json": evidence, "page_candidates.json": page_candidates, "legacy_crop_candidates.json": legacy,
               "source_reviews.json": json.loads((INPUTS / "source_reviews.json").read_text(encoding="utf-8")),
               "lineage_audit.json": lineage_audit,
               "rule_compatibility.json": compatibility, "weather_definitions.json": definitions,
               "source_artifacts.json": artifacts, "qa.json": qa,
               "quarantine.json": dict(exclusions=report["excluded_records"], upstream_label_corrections=report["label_corrections"],
                                        processing_counts=report["processing_counts"], full_source_snapshot="../evidence_inputs/documents.jsonl.gz",
                                        note="Excluded values and analytical duplicates remain in original extraction; legacy report does not identify every deduplicated row"),
               "month_corrections.json": json.loads((INPUTS / "month_corrections.json").read_text(encoding="utf-8"))}
    for name, records in (("entries.jsonl", ordered), ("source_entries.jsonl", source_entries), ("weather_normals.jsonl", sorted(weather, key=lambda w: w["entry_id"]))):
        write_utf8(output / name, "".join(dump(record) + "\n" for record in records))
    fields = ["rule_id", "crop_calendar_applicability", "required_metric", "unit", "time_stage_interval",
              "spatial_applicability", "source_url", "source_pdf", "source_page", "source_pages", "evidence_status", "nasa_counterpart",
              "needed_transformation", "missing_information", "evaluable_now"]
    with (output / "rule_compatibility.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows({key: dump(value) if isinstance(value, (list, dict)) else value for key, value in rule.items()} for rule in compatibility)
    for name, value in outputs.items():
        write_utf8(output / name, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    input_paths = [ROOT / "assets/crop_planning_dataset.csv", ROOT / "assets/bamis_region_district_mapping.csv",
                   ROOT / "assets/crop_planning_dataset_report.json", ROOT / "data/catalog/rajshahi_crop_evidence_catalog.csv",
                   ROOT / "data/catalog/rajshahi_candidate_rule_evidence.csv", *sorted(INPUTS.glob("*")), Path(__file__),
                   ROOT / "scripts/crop_evidence_lineage.py", ROOT / "scripts/vendor/bamis/build_planning_dataset.py"]
    receipt = dict(inputs={p.relative_to(ROOT).as_posix(): input_fingerprint(p) for p in input_paths if p.is_file()},
                   outputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file() and p.name != "receipt.json"})
    write_utf8(output / "receipt.json", json.dumps(receipt, indent=2) + "\n")
    print(f"PASS: {len(entries)} preserved entries, {len(calendars)} source-table calendars, {len(conflict_groups)} repeated-week groups; zero active rules")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Rebuild in temporary storage and compare exact output bytes")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            build(scratch)
            expected = {p.name: p.read_bytes() for p in args.output.iterdir() if p.is_file()}
            actual = {p.name: p.read_bytes() for p in scratch.iterdir()}
            if expected != actual:
                raise SystemExit("FAIL: normalized package differs; rebuild and inspect changes")
        print("PASS: byte-identical normalized rebuild")
    else:
        build(args.output)
