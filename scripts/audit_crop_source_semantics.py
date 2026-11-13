"""Offline source-review leads across the preserved BAMIS extraction.

Never repairs months, converts weeks to dates, parses executable thresholds or
promotes source statements to approved rules. Pattern absence is not evidence
that a definition is absent from an original PDF or another publication.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/catalog/evidence_inputs/documents.jsonl.gz"
OUTPUT = ROOT / "data/catalog/source_review"
MONTHS = {label.lower(): i for i, label in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
MONTHS.update({label: i for i, label in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)})
DEFINITION_PATTERNS = {
    "year_range_lead": re.compile(r"\b(?:19|20)\d{2}\s*[-–/]\s*(?:(?:19|20)\d{2}|\d{2})\b"),
    "week_convention_lead": re.compile(r"\bISO(?:\s+8601)?\b|\bstandard\s+meteorological\s+week\b|\bweek\s+(?:1|one)\s+(?:starts|begins)\b", re.I),
    "normal_reference_year_lead": re.compile(r"\b(?:normal|climatological|reference)\b[^\n]{0,100}\b(?:19|20)\d{2}\b", re.I),
}
METRIC = re.compile(r"rain|temp|humid|sunshine|wind|water", re.I)
INTERVAL = re.compile(r"\b(?:daily|weekly|morning|afternoon)\b|\bmm\s*/\s*day\b|\b(?:day|night)\s*temp|\b(?:for|over|during)\s+(?:\d+|one|two|three)\s*(?:days?|hours?)\b", re.I)


def write(path, value):
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def month_number(label):
    # Exact single English label only; compressed ranges remain uninterpreted.
    return MONTHS.get(label.strip().rstrip(".").lower())


def month_sequences(doc):
    by_table = defaultdict(dict)
    for obs in doc["weekly_weather"]:
        by_table[obs["table_id"]].setdefault(obs["calendar_column"], obs)
    result = []
    for table_id, columns in sorted(by_table.items()):
        groups = []
        for column, obs in sorted(columns.items()):
            raw = obs["month_label_raw"]
            if not groups or groups[-1]["month_label_raw"] != raw:
                groups.append(dict(month_label_raw=raw, month_number=month_number(raw), standard_weeks=[], source_columns=[]))
            groups[-1]["standard_weeks"].append(obs["standard_week"])
            groups[-1]["source_columns"].append(column)
        gaps = []
        for before, after in zip(groups, groups[1:]):
            if before["month_number"] is not None and after["month_number"] is not None:
                jump = (after["month_number"] - before["month_number"]) % 12
                if jump > 1:
                    gaps.append(dict(before=before["month_label_raw"], after=after["month_label_raw"],
                                     before_last_week=before["standard_weeks"][-1], after_first_week=after["standard_weeks"][0],
                                     omitted_month_numbers=[(before["month_number"] + n - 1) % 12 + 1 for n in range(1, jump)],
                                     disposition="printed month-label gap; no corrected date/month or ISO-week interpretation assigned"))
        result.append(dict(source_table_id=table_id, source_page=next(iter(columns.values()))["page_number"],
                           month_groups=groups, month_label_gaps=gaps))
    return result


def source_role(row, current):
    text = " ".join(str(value or "") for value in row)
    if len(text) < 240:
        if re.search(r"weather\s*warning", text, re.I):
            return "weather_warning"
        if re.search(r"favo[u]?rable|congenial", text, re.I):
            if re.search(r"disease|pest|insect", text, re.I):
                return "pest_or_disease_context"
            return "crop_requirement_or_preference_context"
        if re.search(r"std\.?\s*week|standard\s*week", text, re.I):
            return "calendar_normal_context"
    return current


def audit(docs):
    inventory, lentil, interval_leads = [], [], []
    for doc in sorted(docs, key=lambda d: d["source_pdf"]):
        hits = []
        for page in doc["pages"]:
            for label, pattern in DEFINITION_PATTERNS.items():
                for match in pattern.finditer(page["text"]):
                    hits.append(dict(kind=label, source_page=page["page_number"],
                                     text=page["text"][max(0, match.start()-90):match.end()+90],
                                     status="search lead only; definition not established"))
        inventory.append(dict(source_id=doc["document_id"], source_pdf=doc["source_pdf"], source_sha256=doc["source_sha256"],
                              crop_folder=doc["crop_folder"], region=doc["region"],
                              definition_search_leads=hits, evidence_status="unreviewed definitions; no scientific activation"))
        if doc["crop_folder"] == "Lentil":
            sequences = month_sequences(doc)
            lentil.append(dict(source_id=doc["document_id"], source_pdf=doc["source_pdf"], source_sha256=doc["source_sha256"],
                               region=doc["region"], calendars=sequences,
                               has_month_label_gap=any(c["month_label_gaps"] for c in sequences),
                               status="preserved source comparison; no cross-region substitution"))
        for table in doc["tables"]:
            role = "unclassified_source_context"
            for row_index, row in enumerate(table["rows"], 1):
                role = source_role(row, role)
                text = " ".join(str(value or "") for value in row)
                if METRIC.search(text) and INTERVAL.search(text):
                    interval_leads.append(dict(source_id=doc["document_id"], source_pdf=doc["source_pdf"],
                                               source_page=table["page_number"], source_table_id=table["table_id"],
                                               source_row_index=row_index, source_cells=[c["cell_id"] for c in table["cells"] if c["row_index"] == row_index],
                                               raw_row=row, source_role_lead=role,
                                               status="interval wording lead only; original layout/applicability review required",
                                               usable_as_normal_definition=False, executable=False))
    summary = dict(source_documents=len(inventory), regions=len({r["region"] for r in inventory}),
                   lentil_documents=len(lentil), lentil_regions_with_month_label_gaps=sorted({r["region"] for r in lentil if r["has_month_label_gap"]}),
                   definition_leads_by_kind=dict(Counter(h["kind"] for r in inventory for h in r["definition_search_leads"])),
                   interval_wording_leads=len(interval_leads), interval_roles=dict(Counter(r["source_role_lead"] for r in interval_leads)),
                   executable_rules_added=0, scientific_values_changed=0,
                   limitations=["English text patterns and original extraction only; OCR/language/layout gaps can hide definitions",
                                "Zero search matches never establishes absence of a definition",
                                "Source-role labels are review leads, not approved interpretation",
                                "Explicit interval wording in pest/warning text does not define calendar-normal aggregation",
                                "Month-label sequence gaps do not establish which printed value is wrong or a date mapping"])
    return dict(document_definition_leads=inventory, lentil_region_comparison=lentil,
                interval_wording_leads=interval_leads, summary=summary)


def build(output):
    with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as stream:
        result = audit([json.loads(line) for line in stream])
    output.mkdir(parents=True, exist_ok=True)
    for name, records in result.items():
        write(output / (name + ".json"), records)
    inputs = [SNAPSHOT, Path(__file__)]
    receipt = dict(inputs={path.relative_to(ROOT).as_posix(): dict(
        sha256=hashlib.sha256(path.read_bytes() if path.suffix == ".gz" else path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        method="exact binary bytes" if path.suffix == ".gz" else "UTF-8 bytes with CRLF normalized to LF") for path in inputs},
        outputs={name + ".json": hashlib.sha256((output / (name + ".json")).read_bytes()).hexdigest() for name in result})
    write(output / "receipt.json", receipt)
    print("PASS: " + str(result["summary"]["source_documents"]) + " documents; " + str(result["summary"]["lentil_documents"]) + " Lentil regions; " + str(len(result["summary"]["lentil_regions_with_month_label_gaps"])) + " printed month-label gaps; no corrections or rules")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            build(scratch)
            names = ["document_definition_leads.json", "lentil_region_comparison.json", "interval_wording_leads.json", "summary.json", "receipt.json"]
            if any((scratch / name).read_bytes() != (args.output / name).read_bytes() for name in names):
                raise SystemExit("FAIL: source-semantics audit differs from preserved outputs")
        print("PASS: byte-identical source-semantics audit rebuild")
    else:
        build(args.output)
