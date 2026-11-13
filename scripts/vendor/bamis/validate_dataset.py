"""Check source/page coverage, text fidelity, references, and weather exports."""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import json
import re
import sys

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "BAMIS_Dataset"


def read_jsonl(name):
    with (OUT/name).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def no_space(s):
    return "".join(s.split())


def main():
    pages = read_jsonl("pages.jsonl")
    tables = read_jsonl("tables.jsonl")
    weather = read_jsonl("weekly_weather.jsonl")
    with (OUT/"manifest.csv").open(encoding="utf-8-sig", newline="") as f:
        manifest = list(csv.DictReader(f))
    failures, warnings = [], []
    def check(condition, message):
        if not condition:
            failures.append(message)
    source_paths = {p.relative_to(ROOT).as_posix() for p in (ROOT/"BAMIS_All_Crops").rglob("*.pdf")}
    check({r["source_pdf"] for r in manifest} == source_paths, "PDF inventory differs from manifest")
    check(len(manifest) == len(source_paths), "Duplicate/missing manifest records")
    by_pdf = collections.defaultdict(list)
    page_by_id = {p["page_id"]: p for p in pages}
    check(len(page_by_id) == len(pages), "Duplicate page IDs")
    for p in pages:
        by_pdf[p["source_pdf"]].append(p)
    source_page_count = 0
    source_glyph_count = 0
    provenance_notes = []
    region_aliases = {"barisal": "barishal", "chittagong": "chattogram", "comilla": "cumilla",
                      "bogra": "bogura", "jessore": "jashore", "rangamati": "rangamati"}
    for row in manifest:
        path = ROOT/row["source_pdf"]
        check(hashlib.sha256(path.read_bytes()).hexdigest() == row["source_sha256"], f"Source checksum mismatch: {path}")
        with fitz.open(path) as doc:
            source_page_count += len(doc)
            exported = sorted(by_pdf[row["source_pdf"]], key=lambda p: p["page_number"])
            for record in exported:
                declared = re.search(r"(?:Calendar\s+of|Calender\s+of)[^:\n]*:\s*([A-Za-z ]+?)\s+Region", record["text"], re.I)
                if declared:
                    name = declared.group(1).strip().lower()
                    canonical = region_aliases.get(name, name)
                    if canonical != row["region"].lower():
                        provenance_notes.append({"code": "folder_region_differs_from_printed_region", "page_id": record["page_id"],
                                                 "source_pdf": row["source_pdf"], "folder_region": row["region"], "printed_region": declared.group(1).strip()})
            check([p["page_number"] for p in exported] == list(range(1, len(doc)+1)), f"Missing/duplicate pages: {path}")
            for native_page, record in zip(doc, exported):
                tp = native_page.get_textpage(flags=fitz.TEXTFLAGS_RAWDICT & ~fitz.TEXT_PRESERVE_IMAGES, clip=fitz.INFINITE_RECT())
                text = native_page.get_text("text", textpage=tp, sort=False)
                check(text == record["native_text"], f"Native source text mismatch: {record['page_id']}")
                check(hashlib.sha256(text.encode()).hexdigest() == record["native_text_sha256"], f"Page text hash mismatch: {record['page_id']}")
                source_glyph_count += len(no_space(text))
                if record["extraction_method"] in ("native", "native_with_supplementary_ocr"):
                    # Sorting may change reading order, but must not drop or invent glyphs.
                    check(collections.Counter(no_space(text)) == collections.Counter(no_space(record["text"])),
                          f"Reading-order text loses glyphs: {record['page_id']}")
                if not text.strip() and native_page.get_image_info():
                    check(bool(record["text"].strip()), f"Scanned page has no transcription: {record['page_id']}")
    layout_glyph_count, layout_pages = 0, set()
    with gzip.open(OUT/"layout.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            pid = item["page_id"]
            layout_pages.add(pid)
            glyphs = "".join(c["c"] for b in item["native_layout"]["blocks"] for l in b.get("lines", []) for s in l["spans"] for c in s.get("chars", []))
            check(no_space(glyphs) == no_space(page_by_id[pid]["native_text"]), f"Native glyph layout mismatch: {pid}")
            layout_glyph_count += len(no_space(glyphs))
    check(layout_pages == set(page_by_id), "Layout page coverage incomplete")
    check(layout_glyph_count == source_glyph_count, "Glyph totals differ")
    vector_pages = set()
    with gzip.open(OUT/"vectors.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            vector_pages.add(json.loads(line)["page_id"])
    check(vector_pages == set(page_by_id), "Vector page coverage incomplete")
    cell_by_id = {}
    for t in tables:
        check(t["page_id"] in page_by_id, f"Orphan table: {t['table_id']}")
        for c in t["cells"]:
            check(c["cell_id"] not in cell_by_id, f"Duplicate cell: {c['cell_id']}")
            cell_by_id[c["cell_id"]] = c
            check(t["rows"][c["row_index"]-1][c["column_index"]-1] == c["text"], f"Cell/matrix text differs: {c['cell_id']}")
    row_keys = set()
    by_doc = collections.defaultdict(lambda: collections.defaultdict(set))
    by_calendar = collections.defaultdict(lambda: collections.defaultdict(set))
    for w in weather:
        check(w["cell_id"] in cell_by_id, f"Orphan weather value: {w['cell_id']}")
        check(w["week_cell_id"] in cell_by_id, f"Orphan week header: {w['week_cell_id']}")
        check(w["value_raw"] == cell_by_id[w["cell_id"]]["text"], f"Raw weather value changed: {w['cell_id']}")
        if w["value_numeric"] is not None:
            check(float(re.sub(r"\s+", "", w["value_raw"])) == w["value_numeric"], f"Numeric parsing changed value: {w['cell_id']}")
        key = (w["table_id"], w["calendar_column"], w["metric"])
        check(key not in row_keys, f"Duplicate weather observation: {key}")
        row_keys.add(key)
        by_doc[w["document_id"]][w["calendar_column"]].add(w["metric"])
        by_calendar[w["table_id"]][w["calendar_column"]].add(w["metric"])
    for row in manifest:
        columns = by_doc[row["document_id"]]
        if not columns:
            warnings.append({"code": "no_weekly_view", "document_id": row["document_id"]})
    for table_id, columns in by_calendar.items():
        incomplete = {str(column): sorted(metrics) for column, metrics in columns.items() if len(metrics) != 10}
        if incomplete:
            warnings.append({"code": "incomplete_weekly_convenience_view", "table_id": table_id,
                             "columns_and_available_metrics": incomplete,
                             "note": "Review original table and continuation page; all content remains in page/table/layout exports."})
    # Separate CSV files must be equivalent to JSONL, including embedded newlines.
    for name, expected in (("pages.csv", len(pages)), ("table_cells.csv", len(cell_by_id)), ("weekly_weather.csv", len(weather))):
        with (OUT/name).open(encoding="utf-8-sig", newline="") as stream:
            count = sum(1 for _ in csv.DictReader(stream))
        check(count == expected, f"CSV/JSONL row count differs: {name}")
    with (OUT/"documents.jsonl").open(encoding="utf-8") as stream:
        count = 0
        for line in stream:
            doc = json.loads(line)
            count += 1
            single = json.loads((OUT/"documents"/(doc["document_id"]+".json")).read_text(encoding="utf-8"))
            check(single == doc, f"Document JSON differs from JSONL: {doc['document_id']}")
            check(len(doc["pages"]) == doc["page_count"], f"Document page count mismatch: {doc['document_id']}")
            check((OUT/"text"/(doc["document_id"]+".txt")).read_text(encoding="utf-8") == doc["full_text"], f"Plain text export differs: {doc['document_id']}")
    check(count == len(manifest), "Document JSONL count differs")
    result = {"passed": not failures, "source_pdfs_checked": len(manifest), "source_pages_checked": source_page_count,
              "native_non_whitespace_glyphs_verified": source_glyph_count, "table_cells_checked": len(cell_by_id),
              "weather_records_checked": len(weather), "failures": failures, "warnings": warnings,
              "source_provenance_notes": provenance_notes,
              "scope": "Verifies file/page coverage, exact native text, glyph preservation, JSON/CSV consistency, source hashes, and referential integrity. It does not certify semantic accuracy of source data, table detection, or scanned transcription."}
    (OUT/"validation_report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dict(result, failures=result["failures"][:10], warnings=result["warnings"][:10],
                          failure_count=len(failures), warning_count=len(warnings)), ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
