"""Build compact, flat crop-calendar features for Soil to Stars.

One row = crop / region / season / standard week. Values are printed calendar
weather normals, not observed crop outcomes or crop suitability thresholds.
"""
from pathlib import Path
import collections
import csv
import json
import math
import re

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "BAMIS_Dataset"
CSV_PATH = ROOT / "crop_planning_dataset.csv"
XLSX_PATH = ROOT / "crop_planning_dataset.xlsx"
DISTRICT_MAP_PATH = ROOT / "bamis_region_district_mapping.csv"
FIELDS = ["crop", "season", "region", "district_coverage", "standard_week", "month", "growth_stage",
          "duration_min_days", "duration_max_days", "rainfall_mm", "temp_min_c",
          "temp_max_c", "temp_mean_c", "humidity_mean_pct", "sunshine_hours",
          "wind_speed_kmh", "source_pdf", "source_page"]
MEASURES = {"rainfall": "rainfall_mm", "minimum_temperature": "temp_min_c",
            "maximum_temperature": "temp_max_c", "mean_temperature": "temp_mean_c",
            "mean_relative_humidity": "humidity_mean_pct", "sunshine_duration": "sunshine_hours",
            "wind_speed": "wind_speed_kmh"}
ALIASES = {"barisal": "barishal", "bogra": "bogura", "jessore": "jashore", "comilla": "cumilla",
           "chittagong": "chattogram", "chottogram": "chattogram", "rongpur": "rangpur", "rangmati": "rangamati", "dinjpur": "dinajpur"}
STAGE = re.compile(r"seed|sow|transplant|germinat|tiller|vegetat|flower|grain|matur|harvest|ripen|fruit|panicle|pea\s*stage|swell|bud|root|tuber|sprout|spout|boll|squar|canopy|leaf|heading|emergen|nursery|elongat|shoot|sucker", re.I)

# These 14 BAMIS calendar regions partition the 64 districts. The names are
# normalized from the district lists printed in the retained source PDFs; they
# are not inferred field-level coverage or district-specific measurements.
REGION_DISTRICTS = {
    "Barishal": ("Barguna", "Barishal", "Bhola", "Jhalakathi", "Patuakhali", "Pirojpur"),
    "Bogura": ("Bogura", "Joypurhat", "Pabna", "Sirajganj"),
    "Chattogram": ("Chattogram", "Cox's Bazar", "Feni", "Lakshmipur", "Noakhali"),
    "Cumilla": ("Brahmanbaria", "Chandpur", "Cumilla"),
    "Dhaka": ("Dhaka", "Gazipur", "Kishoreganj", "Manikganj", "Munshiganj", "Narayanganj", "Narsingdi", "Tangail"),
    "Dinajpur": ("Dinajpur", "Panchagarh", "Thakurgaon"),
    "Faridpur": ("Faridpur", "Gopalganj", "Madaripur", "Rajbari", "Shariatpur"),
    "Jashore": ("Chuadanga", "Jashore", "Jhenaidah", "Kushtia", "Magura", "Meherpur"),
    "Khulna": ("Bagerhat", "Khulna", "Narail", "Satkhira"),
    "Mymensingh": ("Jamalpur", "Mymensingh", "Netrokona", "Sherpur"),
    "Rajshahi": ("Chapainawabganj", "Naogaon", "Natore", "Rajshahi"),
    "Rangamati": ("Bandarban", "Khagrachhari", "Rangamati"),
    "Rangpur": ("Gaibandha", "Kurigram", "Lalmonirhat", "Nilphamari", "Rangpur"),
    "Sylhet": ("Habiganj", "Moulvibazar", "Sunamganj", "Sylhet"),
}
REGION_DIVISIONS = {
    "Barishal": "Barishal", "Bogura": "Rajshahi", "Chattogram": "Chattogram",
    "Cumilla": "Chattogram", "Dhaka": "Dhaka", "Dinajpur": "Rangpur",
    "Faridpur": "Dhaka", "Jashore": "Khulna", "Khulna": "Khulna",
    "Mymensingh": "Mymensingh", "Rajshahi": "Rajshahi",
    "Rangamati": "Chattogram", "Rangpur": "Rangpur", "Sylhet": "Sylhet",
}

# The printed district list is a copied header error in these three PDFs. Their
# folder/title/table region agrees, and all retained weekly weather rows match
# other calendars from that same region (21/21 in each case).
COVERAGE_CORRECTIONS = {
    "BAMIS_All_Crops/Ground nut (Robi)/Jashore/9914.pdf": "printed districts list Rangpur-area districts; use Jashore region coverage",
    "BAMIS_All_Crops/Pointed Gourd/Dinajpur/27396.pdf": "printed districts list Rajshahi-area districts; use Dinajpur region coverage",
    "BAMIS_All_Crops/Pointed Gourd/Rangpur/27404.pdf": "printed districts list Rajshahi-area districts; use Rangpur region coverage",
}

# This document cannot be safely reassigned: folder/title say Mymensingh while
# its table heading and district list say Cumilla. Exclude it from planning.
COVERAGE_EXCLUSIONS = {
    "BAMIS_All_Crops/Onion/Mymensingh/26480.pdf": "folder/title Mymensingh conflict with Cumilla table and districts",
}


def clean(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    return re.sub(r"\b(Flowe)\s+(ring)\b|\b(Harve)\s+(sting)\b", lambda m: "".join(x for x in m.groups() if x), s, flags=re.I)


def crop_name(text):
    text = clean(text).lower()
    names = [(r"pointed\s*gourd", "Pointed Gourd"), (r"sweet\s*gourd|pumpkin", "Pumpkin"),
             (r"bottle\s*gourd", "Bottle Gourd"), (r"green\s*gram|mungbean", "Mungbean"),
             (r"ground\s*nut", "Groundnut"), (r"eggplant|brinjal", "Brinjal"),
             (r"chill?i|pepper", "Chilli"), (r"ma[iz]+e|mazie", "Maize"),
             (r"rice", "Rice"), (r"wheat", "Wheat"), (r"jute", "Jute"),
             (r"lentil", "Lentil"), (r"mustard", "Mustard"), (r"potato", "Potato"),
             (r"sugarcane", "Sugarcane"), (r"tomato", "Tomato"), (r"onion", "Onion"), (r"garlic|gurlic", "Garlic"),
             (r"cucumber", "Cucumber"), (r"cotton", "Cotton"), (r"pineapple", "Pineapple"),
             (r"jackfruit", "Jackfruit"), (r"papaya", "Papaya"), (r"banana", "Banana"),
             (r"mango", "Mango"), (r"litchi", "Litchi"), (r"jujub", "Jujube"),
             (r"guava", "Guava"), (r"soybean", "Soybean"), (r"gourd", "Bottle Gourd")]
    return next((name for pattern, name in names if re.search(pattern, text)), None)


def season_name(text):
    text = clean(text).lower()
    for name in ("aman", "aus", "boro"):
        if name in text:
            return name.title()
    if re.search(r"rabi|robi|রবি", text):
        return "Rabi"
    if re.search(r"kharif|kharip|karif|kharif|খবরপ|খরিপ|খারিফ", text):
        if re.search(r"(?:kharif|kharip|karif)[\s-]*(?:1|i)(?![a-z0-9])", text):
            return "Kharif-1"
        if re.search(r"(?:kharif|kharip|karif)[\s-]*(?:2|ii)(?![a-z0-9])", text):
            return "Kharif-2"
        return "Kharif"
    return "Unspecified"


def printed_region(text):
    # Check only the title; avoid matching districts or unrelated paragraphs.
    first = clean(text[:650]).split("District", 1)[0]
    m = re.search(r"([A-Za-z]+)\s*Region", first, re.I)
    if not m:
        return None
    name = m.group(1).lower()
    return ALIASES.get(name, name)


def duration(header):
    # Header includes only the first row, not weekly measurements.
    m = re.search(r"(?:duration|life\s*(?:span|cycle(?:\s*of\s*crop)?))\s*[:,]?\s*(\d{2,3})(?:\s*[-–]\s*(\d{2,3}))?", header, re.I)
    if not m:
        m = re.search(r"(?<!\d)(\d{2,3})\s*[-–]\s*(\d{2,3})(?!\d)", header)
    if not m:
        return None, None
    a, b = int(m.group(1)), int(m.group(2) or m.group(1))
    return (a, b) if 1 <= a <= b <= 1000 else (None, None)


def stages(table, weather):
    ids = {w["cell_id"] for w in weather}
    end_row = max(c["row_index"] for c in table["cells"] if c["cell_id"] in ids)
    candidates = collections.defaultdict(list)
    for c in table["cells"]:
        text = clean(c["text"])
        if end_row < c["row_index"] <= end_row+3 and 2 < len(text) <= 135 and STAGE.search(text):
            if not re.search(r"weather|disease|temperature|rainfall|humidity|requirement", text, re.I):
                candidates[c["row_index"]].append(c)
    if not candidates:
        return []
    best = max(candidates.values(), key=len)
    return best if len(best) >= 2 else []


def stage_for_week(stage_cells, week_bbox):
    x = (week_bbox[0]+week_bbox[2])/2
    matches = [c for c in stage_cells if c["bbox"][0] <= x <= c["bbox"][2]]
    return clean(matches[0]["text"]) if matches else ""


def invalid_reason(row):
    if not all(row.get(k) is not None for k in ("rainfall_mm", "temp_min_c", "temp_max_c", "temp_mean_c")):
        return "missing_core_weather_value"
    if not (row["temp_min_c"] <= row["temp_mean_c"] <= row["temp_max_c"]):
        return "inconsistent_temperature_order"
    limits = {"rainfall_mm": (0, 3000), "temp_min_c": (-30, 70), "temp_max_c": (-30, 70),
              "temp_mean_c": (-30, 70), "humidity_mean_pct": (0, 100), "sunshine_hours": (0, 168), "wind_speed_kmh": (0, 300)}
    for field, (low, high) in limits.items():
        value = row.get(field)
        if value is not None and (not math.isfinite(value) or not low <= value <= high):
            return "invalid_"+field
    return None


def build():
    rows, excluded, corrections = [], [], []
    counts = collections.Counter()
    seen_sha = set()
    for path in sorted((DATA/"documents").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        base = {"source_pdf": doc["source_pdf"]}
        counts["source_documents_read"] += 1
        assert crop_name(doc["crop_folder"]), "Unmapped source crop folder: "+doc["crop_folder"]
        assert doc["region"] in REGION_DISTRICTS, "Unmapped BAMIS region: "+doc["region"]
        if doc["source_pdf"] in COVERAGE_EXCLUSIONS:
            excluded.append(dict(base, reason="source_region_district_labels_conflict",
                                 detail=COVERAGE_EXCLUSIONS[doc["source_pdf"]]))
            continue
        if doc["source_pdf"] in COVERAGE_CORRECTIONS:
            corrections.append(dict(base, correction="district_coverage_from_region_consensus",
                                    region=doc["region"],
                                    district_coverage=list(REGION_DISTRICTS[doc["region"]]),
                                    detail=COVERAGE_CORRECTIONS[doc["source_pdf"]]))
        if doc["source_sha256"] in seen_sha:
            excluded.append(dict(base, reason="duplicate_pdf"))
            continue
        seen_sha.add(doc["source_sha256"])
        page_map = {p["page_number"]: p for p in doc["pages"]}
        cell_map = {c["cell_id"]: c for t in doc["tables"] for c in t["cells"]}
        by_table = collections.defaultdict(list)
        for w in doc["weekly_weather"]:
            by_table[w["table_id"]].append(w)
        for table in doc["tables"]:
            values = by_table[table["table_id"]]
            if not values:
                if any("source_calendar_row_labels_inconsistent" == issue.get("code") and table["table_id"] in issue.get("detail", "") for issue in doc["issues"]):
                    excluded.append(dict(base, source_page=table["page_number"], reason="source_calendar_row_labels_inconsistent"))
                continue
            counts["calendars_examined"] += 1
            page = page_map[table["page_number"]]
            context = dict(base, source_page=table["page_number"])
            if "visual_transcription" in page["extraction_method"]:
                excluded.append(dict(context, reason="unverified_low_resolution_scan"))
                continue
            region_in_title = printed_region(page["text"])
            if region_in_title and region_in_title != doc["region"].lower():
                excluded.append(dict(context, reason="printed_region_conflicts_with_folder", printed_region=region_in_title, folder_region=doc["region"]))
                continue
            header = clean(" ".join(str(v or "") for v in table["rows"][0]))
            heading = clean(values[0].get("calendar_label_raw") or header)
            printed_crop = crop_name(heading)
            title_match = re.search(r"Crop\s+Weather\s+Cal[ea]ndar\s+of\s+(.+?)(?::|Region)", clean(page["text"][:600]), re.I)
            title_crop = crop_name(title_match.group(1)) if title_match else None
            folder_crop = crop_name(doc["crop_folder"])
            if printed_crop and title_crop and printed_crop != title_crop:
                excluded.append(dict(context, reason="printed_crop_labels_conflict", header_crop=printed_crop, title_crop=title_crop))
                continue
            crop = printed_crop or title_crop or folder_crop
            if not crop:
                excluded.append(dict(context, reason="unrecognized_crop"))
                continue
            if crop != folder_crop:
                if printed_crop == title_crop:
                    corrections.append(dict(context, correction="crop_from_agreeing_printed_labels", crop=crop, folder_crop=folder_crop))
                else:
                    excluded.append(dict(context, reason="crop_conflicts_with_folder_without_confirmation"))
                    continue
            season = season_name(heading)
            title_season = season_name(title_match.group(1)) if title_match else "Unspecified"
            if season != "Unspecified" and title_season != "Unspecified" and season != title_season:
                if not (season.startswith("Kharif") and title_season.startswith("Kharif")):
                    excluded.append(dict(context, reason="printed_season_labels_conflict", header_season=season, title_season=title_season))
                    continue
            if season == "Unspecified":
                season = title_season
            if season == "Unspecified":
                season = season_name(doc["crop_folder"])
            elif season == "Kharif" and season_name(doc["crop_folder"]).startswith("Kharif-"):
                season = season_name(doc["crop_folder"])
            lo, hi = duration(header)
            stage_cells = stages(table, values)
            groups = collections.defaultdict(list)
            for value in values:
                groups[value["calendar_column"]].append(value)
            seen_calendar_weeks = set()
            for column, observations in groups.items():
                counts["calendar_columns_examined"] += 1
                first = observations[0]
                if first["standard_week"] is None:
                    excluded.append(dict(context, calendar_column=column, reason="ambiguous_or_compressed_week_label", label=first["week_label_raw"]))
                    continue
                if first["standard_week"] in seen_calendar_weeks and hi is not None and hi <= 366:
                    excluded.append(dict(context, calendar_column=column, reason="repeated_week_in_single_season_calendar", standard_week=first["standard_week"]))
                    continue
                seen_calendar_weeks.add(first["standard_week"])
                week_box = cell_map[first["week_cell_id"]]["bbox"]
                row = {"crop": crop, "season": season, "region": doc["region"],
                       "district_coverage": "; ".join(REGION_DISTRICTS[doc["region"]]),
                       "standard_week": first["standard_week"], "month": clean(first["month_label_raw"]),
                       "growth_stage": stage_for_week(stage_cells, week_box),
                       "duration_min_days": lo, "duration_max_days": hi,
                       **{field: None for field in MEASURES.values()}, **context}
                for obs in observations:
                    if obs["metric"] in MEASURES:
                        row[MEASURES[obs["metric"]]] = obs["value_numeric"]
                why = invalid_reason(row)
                humidity = {obs["metric"]: obs["value_numeric"] for obs in observations if "relative_humidity" in obs["metric"]}
                hmin = humidity.get("minimum_relative_humidity")
                hmax = humidity.get("maximum_relative_humidity")
                hmean = row["humidity_mean_pct"]
                if not why and None not in (hmin, hmean, hmax) and not hmin <= hmean <= hmax:
                    why = "inconsistent_humidity_order"
                if why:
                    excluded.append(dict(context, calendar_column=column, standard_week=row["standard_week"], reason=why))
                else:
                    rows.append(row)
    # Identical analytical records are not separate evidence merely because two
    # folders contain them. Different printed values are never averaged away.
    unique, seen_rows = [], set()
    for row in rows:
        key = tuple(row[k] for k in FIELDS if k not in ("source_pdf", "source_page"))
        if key in seen_rows:
            counts["identical_rows_removed"] += 1
            continue
        seen_rows.add(key)
        unique.append(row)
    rows = sorted(unique, key=lambda r: (r["crop"], r["region"], r["season"], r["source_pdf"], r["source_page"], r["standard_week"]))
    assert rows
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    mapping_fields = ["bamis_region", "district", "administrative_division", "mapping_status", "source_basis"]
    mapping_rows = [
        {"bamis_region": region, "district": district,
         "administrative_division": REGION_DIVISIONS[region],
         "mapping_status": "source_normalized",
         "source_basis": "normalized consensus of district lists printed in BAMIS source PDF titles"}
        for region in sorted(REGION_DISTRICTS)
        for district in REGION_DISTRICTS[region]
    ]
    with DISTRICT_MAP_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=mapping_fields)
        writer.writeheader()
        writer.writerows(mapping_rows)
    wb = Workbook()
    ws = wb.active
    ws.title = "Crop planning"
    ws.append(FIELDS)
    for row in rows:
        ws.append([row[k] for k in FIELDS])
    ws.freeze_panes = "E2"
    ws.sheet_view.zoomScale = 85
    table = Table(displayName="CropPlanningData", ref=ws.dimensions)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium4", showRowStripes=True)
    ws.add_table(table)
    widths = [19, 15, 18, 70, 16, 23, 45, 20, 20, 17, 16, 16, 17, 23, 21, 21, 65, 14]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = width
    ws.row_dimensions[1].height = 30
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="24664D")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2, min_col=9, max_col=15):
        for cell in row:
            cell.number_format = "0.0#"
    wb.save(XLSX_PATH)
    # Check actual generated workbook values and types, plus CSV shape and limits.
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        readback = list(csv.DictReader(stream))
    assert len(readback) == len(rows)
    assert len(rows) < 1048576 and len(FIELDS) < 16384
    max_chars = max(len(str(v)) for r in rows for v in r.values() if v is not None)
    assert max_chars < 32767
    assert all("\n" not in str(v) and "\r" not in str(v) for r in rows for v in r.values())
    assert all(invalid_reason(r) is None for r in rows)
    assert len(mapping_rows) == 64
    assert len({r["district"] for r in mapping_rows}) == 64
    assert len({r["administrative_division"] for r in mapping_rows}) == 8
    assert all(r["district_coverage"] for r in rows)
    check_wb = load_workbook(XLSX_PATH, read_only=True, data_only=True)
    saved = check_wb.active
    assert saved.max_row == len(rows)+1 and saved.max_column == len(FIELDS)
    for expected, actual in zip(rows, saved.iter_rows(min_row=2, values_only=True)):
        for key, value in zip(FIELDS, actual):
            target = expected[key]
            assert value == target or (target == "" and value is None), (key, value, target)
    check_wb.close()
    source_refs = {(r["source_pdf"], r["source_page"]) for r in rows}
    summary = {"rows": len(rows), "columns": len(FIELDS), "column_names": FIELDS,
               "csv_bytes": CSV_PATH.stat().st_size, "xlsx_bytes": XLSX_PATH.stat().st_size,
               "district_mapping_file": DISTRICT_MAP_PATH.name,
               "district_mapping_rows": len(mapping_rows),
               "districts_mapped": len({r["district"] for r in mapping_rows}),
               "administrative_divisions_mapped": len({r["administrative_division"] for r in mapping_rows}),
               "max_cell_characters": max_chars, "checks": "passed: Excel cell/row/column limits, single-line cells, workbook reopening and all values, numeric core fields and physical range checks",
               "crops": sorted({r["crop"] for r in rows}), "regions": sorted({r["region"] for r in rows}),
               "seasons": dict(collections.Counter(r["season"] for r in rows)),
               "source_documents_represented": len({r["source_pdf"] for r in rows}), "source_pages_represented": len(source_refs),
               "missing_values": {k: sum(r[k] is None or r[k] == "" for r in rows) for k in FIELDS},
               "processing_counts": dict(counts), "excluded_by_reason": dict(collections.Counter(r["reason"] for r in excluded)),
               "excluded_records": excluded, "label_corrections": corrections,
               "meaning": "Printed BAMIS crop-calendar weather normals for crop/season/week context. These values are not favorable-weather requirements, actual crop outcomes, yield, or suitability labels.",
               "project_fit": "Soil to Stars crop calendar and regional climate features. No frontend demo scores were used. Soil pH, salinity, irrigation capacity, crop-family sequence rules, outcomes and NASA historical series require separate evidence.",
               "missingness": "Blank = not unambiguously supplied by the source; never zero-filled. Unspecified season = no explicit season label. Stage follows the printed calendar geometry; not an independent agronomic validation.",
               "training_split": "Group by region and source calendar when splitting. Multiple crop calendars repeat regional weather normals; a random row split can leak this shared context.",
               "retained_source_archive": "BAMIS_Dataset contains raw extraction for review, excluded details, and future use."}
    (ROOT/"crop_planning_dataset_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    guide = ["# Crop planning dataset", "", f"{len(rows):,} rows × {len(FIELDS)} columns. One row is one crop, region, printed season and standard calendar week.", "",
             "Open crop_planning_dataset.xlsx in Excel. crop_planning_dataset.csv contains the identical flat data for Python/R/imports.",
             "bamis_region_district_mapping.csv maps the 14 BAMIS calendar regions to all 64 districts and their eight current administrative divisions.",
             "", "Columns: "+", ".join(FIELDS)+".", "",
             "Weather values are printed calendar normals, not required crop thresholds or yield/suitability outcomes. Durations are printed calendar durations, not assumed plantation lifespans. Sunshine hours are retained as printed for the calendar period; no conversion is inferred.",
             "", "district_coverage is a normalized BAMIS region coverage list derived from the source PDF titles; it does not turn regional weather normals into district measurements. Blank means missing; Unspecified means no explicit season label. Stage labels use the original calendar's spatial alignment. Source references allow checking each row.",
             "", "Conflicting coverage labels are handled explicitly: three copied district headers are corrected from agreeing region labels and repeated regional weather rows; one ambiguous Mymensingh/Cumilla onion calendar is excluded. See crop_planning_dataset_report.json.",
             "", "Conflicting crop/region labels, ambiguous compressed week columns, a low resolution scan, implausible numeric values and duplicate records are excluded or explicitly corrected from agreeing printed labels. See crop_planning_dataset_report.json for the exact audit.",
             "", "The website also requires soil, irrigation and source-backed rotation rules, which these weather calendars cannot establish. No illustrative website scores, invented pH values or success labels were included.",
             "", "For modeling, keep source calendars/regions grouped when splitting data because regional weather values recur across crops. A supervised yield/rotation-success target needs separate measured labels.", "",
             "Rebuild: python scripts/build_planning_dataset.py (requires openpyxl and the existing BAMIS_Dataset/documents extraction).", ""]
    (ROOT/"crop_planning_dataset_README.md").write_text("\n".join(guide), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("excluded_records",)}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    build()
