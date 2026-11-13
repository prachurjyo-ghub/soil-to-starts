"""Build a source-preserving BAMIS corpus. Run from any directory; see README.md."""
from __future__ import annotations

import argparse
import collections
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import traceback

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1.0.0"
ALIASES = {"Mazie (Rabi)": "Maize (Rabi)", "Ground nut (Robi)": "Groundnut (Rabi)",
           "Groundnut (Kharif - 1)": "Groundnut (Kharif-1)",
           "Green Gram (Robi)": "Green Gram (Rabi)",
           "Green Gram (Kharif 1)": "Green Gram (Kharif-1)",
           "Maize (kharif-1)": "Maize (Kharif-1)"}
METRICS = {"rainfall": ("rainfall", "mm"), "maxtemp": ("maximum_temperature", "degC"),
           "mintemp": ("minimum_temperature", "degC"), "meantemp": ("mean_temperature", "degC"),
           "rhmax": ("maximum_relative_humidity", "%"), "rhmin": ("minimum_relative_humidity", "%"),
           "rhmean": ("mean_relative_humidity", "%"), "sshr": ("sunshine_duration", "hours"),
           "wd": ("wind_direction", "degrees"), "ws": ("wind_speed", "km/hour")}


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (fitz.Rect, fitz.Point, fitz.Quad)):
        return [json_safe(v) for v in value]
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)}
    return value


def compact(s):
    return re.sub(r"\s+", " ", s or "").strip()


def metric(label):
    key = re.sub(r"[^a-z]", "", label.lower())
    for prefix, spec in METRICS.items():
        if key.startswith(prefix):
            return spec
    return None


def numeric(s):
    s = re.sub(r"\s+", "", s or "")
    return float(s) if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", s) else None


def cell_text_from_layout(bbox, layout):
    """Keep native line order and exact glyph strings inside a physical cell."""
    lines = []
    for block in layout.get("blocks", []):
        bb = block.get("bbox", (0, 0, 0, 0))
        if bb[2] < bbox[0] or bb[0] > bbox[2] or bb[3] < bbox[1] or bb[1] > bbox[3]:
            continue
        for line in block.get("lines", []):
            lb = line["bbox"]
            if lb[2] < bbox[0] or lb[0] > bbox[2] or lb[3] < bbox[1] or lb[1] > bbox[3]:
                continue
            chars = []
            for span in line.get("spans", []):
                for char in span.get("chars", []):
                    x0, y0, x1, y1 = char["bbox"]
                    x, y = (x0+x1)/2, (y0+y1)/2
                    if bbox[0]-.1 <= x < bbox[2]-.1 and bbox[1]-.1 <= y < bbox[3]-.1:
                        chars.append(char["c"])
            if chars:
                lines.append("".join(chars))
    return "\n".join(lines)


def extract_tables(page, context, layout):
    tables = []
    finder = page.find_tables(strategy="lines_strict")
    for ti, table in enumerate(finder.tables, 1):
        tid = f"{context['page_id']}_t{ti:03d}"
        matrix = table.extract()
        cells = []
        # Null grid slots are covered by a merged cell, not missing observations.
        for ri, row in enumerate(table.rows):
            for ci, bbox in enumerate(row.cells):
                if bbox is None:
                    continue
                cell = dict(context, table_id=tid, cell_id=f"{tid}_r{ri+1:03d}_c{ci+1:03d}",
                            row_index=ri+1, column_index=ci+1, bbox=list(bbox),
                            text=matrix[ri][ci], native_text=cell_text_from_layout(bbox, layout))
                cells.append(cell)
        tables.append(dict(context, table_id=tid, extraction_method="pymupdf_lines_strict",
                           bbox=list(table.bbox), row_count=table.row_count,
                           column_count=table.col_count, rows=matrix, cells=cells,
                           header=json_safe({"bbox": table.header.bbox, "names": table.header.names,
                                             "external": table.header.external})))
    return tables


def intersect_x(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0]))


def weekly_weather(tables, issues):
    records = []
    for table in tables:
        by_row = collections.defaultdict(list)
        for cell in table["cells"]:
            by_row[cell["row_index"]].append(cell)
        week_row = next((i for i, row in by_row.items()
                         if any(re.search(r"std\.?\s*w(?:ee)?k|standard.*week", compact(c["text"]), re.I)
                                for c in row)), None)
        bengali = any("\u0980" <= c <= "\u09ff" for c in "".join(str(x or "") for row in table["rows"] for x in row))
        if week_row is None and bengali:
            # The Bengali calendars use the same 10-row meteorological block.
            # Keep this interpretation explicit; never replace original labels.
            week_row = next((i for i, row in sorted(by_row.items()) if i < 7 and
                             sum(bool(re.fullmatch(r"\d{1,2}", compact(c["text"]))) for c in row) >= 8), None)
        if week_row is None:
            continue
        first_values = [compact(c["text"]) for c in by_row[week_row] if re.search(r"\d", c["text"] or "")]
        if any(not re.fullmatch(r"[\d\s–-]+", s) for s in first_values):
            issues.append(dict(page_id=table["page_id"], severity="review", code="source_calendar_row_labels_inconsistent",
                               detail=f"{table['table_id']}: the row labeled standard week contains decimal measurements. Table retained in full; excluded from weekly view to avoid assigning misleading metrics."))
            continue
        weeks = [c for c in by_row[week_row] if re.search(r"\d", c["text"] or "")]
        months = [c for c in by_row.get(week_row-1, []) if c["text"] and compact(c["text"]).lower() != "months"]
        observed_metrics = set()
        first_header = [c for c in table["rows"][0] if c and compact(c)]
        calendar_label = first_header[1] if len(first_header) >= 3 else None
        for ri in sorted(by_row):
            row = by_row[ri]
            if ri <= week_row or ri > week_row+10 or not row:
                continue
            label_cell = min(row, key=lambda c: c["bbox"][0])
            spec = metric(compact(label_cell["text"]))
            mapping = "source_label"
            if spec is None and bengali:
                spec = list(METRICS.values())[ri-week_row-1]
                mapping = "positional_bengali_standard_block"
            if spec is None:
                continue
            observed_metrics.add(spec[0])
            values = [c for c in row if c is not label_cell and compact(c["text"])]
            for wi, week in enumerate(weeks, 1):
                center = (week["bbox"][0]+week["bbox"][2])/2
                candidates = [c for c in values if c["bbox"][0]-.2 <= center <= c["bbox"][2]+.2]
                candidates.sort(key=lambda c: intersect_x(c["bbox"], week["bbox"]), reverse=True)
                if not candidates:
                    issues.append(dict(page_id=table["page_id"], severity="review", code="weather_cell_not_matched",
                                       detail=f"{table['table_id']} {spec[0]} column {wi}"))
                    continue
                cell = candidates[0]
                month = next((m for m in months if m["bbox"][0]-.2 <= center <= m["bbox"][2]+.2), None)
                week_raw = compact(week["text"])
                week_number = int(week_raw) if re.fullmatch(r"\d+", week_raw) and 1 <= int(week_raw) <= 53 else None
                record = {k: cell[k] for k in ("document_id", "page_id", "source_pdf", "page_number", "crop", "crop_folder", "region", "table_id", "cell_id")}
                record.update(calendar_column=wi, week_label_raw=week["text"], standard_week=week_number,
                              calendar_label_raw=calendar_label, metric_mapping=mapping,
                              week_cell_id=week["cell_id"], month_label_raw=month["text"] if month else None,
                              metric=spec[0], metric_label_raw=label_cell["text"], unit=spec[1],
                              value_raw=cell["text"], value_numeric=numeric(cell["text"]),
                              bbox=cell["bbox"], extraction_method=table["extraction_method"])
                records.append(record)
                if week_number is None:
                    issues.append(dict(page_id=table["page_id"], severity="info", code="nonstandard_week_label",
                                       detail=f"{week_raw!r}: preserved without interpreting as a single week"))
        if len(observed_metrics) != 10:
            issues.append(dict(page_id=table["page_id"], severity="review", code="weather_metrics_count",
                               detail=f"Detected {len(observed_metrics)} of 10 typical metrics in {table['table_id']}"))
    return records


def read_transcription(context):
    p = ROOT / "scripts" / "transcriptions" / f"{context['document_id']}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def transcribed_tables(transcription, context):
    tables = []
    for ti, raw_table in enumerate(transcription["tables"], 1):
        tid = f"{context['page_id']}_t{ti:03d}"
        table = dict(context, table_id=tid, extraction_method="visual_transcription",
                     bbox=raw_table["bbox"], row_count=len(raw_table["rows"]),
                     column_count=max(len(r) for r in raw_table["rows"]),
                     rows=raw_table["rows"], cells=[], header=None)
        for ri, row in enumerate(raw_table["rows"], 1):
            for ci, value in enumerate(row, 1):
                if value is None:
                    continue
                bbox = raw_table["cell_bboxes"][ri-1][ci-1]
                table["cells"].append(dict(context, table_id=tid, cell_id=f"{tid}_r{ri:03d}_c{ci:03d}",
                                            row_index=ri, column_index=ci, bbox=bbox,
                                            text=value, native_text=None))
        tables.append(table)
    return tables


def process_pdf(source_str, source_root_str, tessdata_str):
    source, source_root = Path(source_str), Path(source_root_str)
    rel = source.relative_to(source_root)
    folder, region = rel.parts[0:2]
    document_id = "bamis_"+source.stem+"_"+hashlib.sha256(rel.as_posix().encode()).hexdigest()[:8]
    base = dict(document_id=document_id, source_pdf=source.relative_to(ROOT).as_posix(),
                crop_folder=folder, crop=ALIASES.get(folder, folder), region=region)
    issues, pages, layouts, vectors, tables = [], [], [], [], []
    with fitz.open(source) as doc:
        metadata = json_safe(doc.metadata)
        for index, page in enumerate(doc):
            context = dict(base, page_id=f"{document_id}_p{index+1:03d}", page_number=index+1)
            flags = fitz.TEXTFLAGS_RAWDICT & ~fitz.TEXT_PRESERVE_IMAGES
            tp = page.get_textpage(flags=flags, clip=fitz.INFINITE_RECT())
            raw_text = page.get_text("text", textpage=tp, sort=False)
            layout_text = page.get_text("text", textpage=tp, sort=True)
            layout = page.get_text("rawdict", textpage=tp, sort=False)
            image_info = page.get_image_info(hashes=True)
            drawings = page.get_drawings()
            page_issues = []
            method, text, ocr_text, transcription = "native", layout_text, None, None
            page_tables = []
            if not raw_text.strip() and not image_info:
                method = "blank"
            elif len(raw_text.strip()) < 50 and image_info:
                method = "ocr"
                try:
                    ocr_tp = page.get_textpage_ocr(language="eng", dpi=300, full=True, tessdata=tessdata_str)
                    ocr_text = page.get_text("text", textpage=ocr_tp, sort=True)
                    text = ocr_text
                    layout["ocr_blocks"] = page.get_text("rawdict", textpage=ocr_tp, sort=False)["blocks"]
                    transcription = read_transcription(context)
                    if transcription:
                        if transcription["source_sha256"] != hashlib.sha256(source.read_bytes()).hexdigest():
                            raise ValueError("Visual transcription source checksum does not match PDF")
                        method = "visual_transcription_with_ocr"
                        text = transcription["text"]
                        page_tables = transcribed_tables(transcription, context)
                    page_issues.append(dict(severity="review", code="scanned_page_transcription",
                                            detail="Low resolution scanned calendar. OCR retained; visual transcription supplied where available. Verify against source before high accuracy training."))
                except Exception as exc:
                    page_issues.append(dict(severity="error", code="ocr_failed", detail=str(exc)))
            if method not in ("blank", "ocr", "visual_transcription_with_ocr"):
                try:
                    page_tables = extract_tables(page, context, layout)
                except Exception as exc:
                    page_issues.append(dict(severity="review", code="table_extraction_failed", detail=str(exc)))
            if "\ufffd" in raw_text:
                page_issues.append(dict(severity="review", code="replacement_character", detail="Replacement glyph in native extraction"))
            if sum("\u0980" <= c <= "\u09ff" for c in raw_text) > 50:
                try:
                    ben_tp = page.get_textpage_ocr(language="ben+eng", dpi=300, full=True, tessdata=tessdata_str)
                    ocr_text = page.get_text("text", textpage=ben_tp, sort=True)
                    layout["supplementary_ocr_blocks"] = page.get_text("rawdict", textpage=ben_tp, sort=False)["blocks"]
                    method = "native_with_supplementary_ocr"
                    page_issues.append(dict(severity="review", code="bengali_font_and_ocr_review",
                                            detail="Native Bengali glyph order/font mapping may be malformed. Exact native text retained; supplementary ben+eng OCR supplied as an alternative, not a verified correction."))
                except Exception as exc:
                    page_issues.append(dict(severity="review", code="bengali_ocr_failed", detail=str(exc)))
            private_chars = sum(0xE000 <= ord(c) <= 0xF8FF for c in raw_text)
            if private_chars:
                page_issues.append(dict(severity="info", code="private_use_glyph", detail=f"{private_chars} font specific glyphs retained unchanged; e.g. degree symbols may use a private font code."))
            annotations = []
            for annot in page.annots() or []:
                annotations.append({"type": annot.type, "rect": list(annot.rect), "info": annot.info})
            pages.append(dict(context, extraction_method=method, width=page.rect.width, height=page.rect.height,
                              rotation=page.rotation, native_text=raw_text, layout_text=layout_text, text=text,
                              ocr_text=ocr_text, native_text_sha256=hashlib.sha256(raw_text.encode()).hexdigest(),
                              native_character_count=len(raw_text), text_character_count=len(text),
                              blank_page=method == "blank", table_ids=[t["table_id"] for t in page_tables],
                              skipped_image_count=len(image_info), links=json_safe(page.get_links()),
                              annotations=json_safe(annotations), issues=[i["code"] for i in page_issues]))
            layouts.append(dict(context, native_layout=layout, skipped_images=json_safe(image_info)))
            vectors.append(dict(context, drawings=json_safe(drawings)))
            tables.extend(page_tables)
            issues.extend(dict(i, page_id=context["page_id"], source_pdf=base["source_pdf"], page_number=index+1) for i in page_issues)
        weekly = weekly_weather(tables, issues)
        if not weekly:
            issues.append(dict(page_id=pages[0]["page_id"], severity="review", code="no_weekly_weather_records",
                               detail="Full text/layout retained; weekly convenience view could not be constructed."))
        title_text = pages[0]["text"]
        districts = re.search(r"Districts?\s*:\s*([^)]*)\)", title_text, re.I)
        duration = re.search(r"(?:Time\s*)?duration\s*:?\s*(\d+(?:\s*[-–]\s*\d+)?\s*days?)", title_text, re.I)
        document = dict(base, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        source_bytes=source.stat().st_size, page_count=len(doc), pdf_metadata=metadata,
                        table_of_contents=doc.get_toc(), embedded_file_names=doc.embfile_names(),
                        title=compact(title_text.splitlines()[0]) if title_text.splitlines() else "",
                        districts_raw=districts.group(1).strip() if districts else None,
                        duration_raw=duration.group(1) if duration else None,
                        full_text="\n\n".join(f"[Page {p['page_number']}]\n{p['text']}" for p in pages),
                        pages=pages, tables=tables, weekly_weather=weekly,
                        issues=issues, schema_version=SCHEMA_VERSION)
    return {"document": document, "pages": pages, "layouts": layouts, "vectors": vectors,
            "tables": tables, "weekly": weekly, "issues": issues}


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: dump(v) if isinstance(v, (list, dict)) else v for k, v in row.items() if k in fields})


def run(args):
    source_root, output = args.source.resolve(), args.output.resolve()
    if source_root == output or source_root in output.parents:
        raise ValueError("Output must be outside the source PDF folder")
    sources = sorted(source_root.rglob("*.pdf"))
    if not sources:
        raise ValueError("No source PDFs found")
    output.mkdir(parents=True, exist_ok=True)
    (output/"documents").mkdir(exist_ok=True)
    (output/"text").mkdir(exist_ok=True)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        pending = {executor.submit(process_pdf, str(p), str(source_root), str(args.tessdata.resolve())): p for p in sources}
        for future in as_completed(pending):
            path = pending[future]
            try:
                result = future.result()
            except Exception:
                print(f"FAILED {path}", flush=True)
                traceback.print_exc()
                raise
            results.append(result)
            if len(results) % 20 == 0 or len(results) == len(sources):
                print(f"Extracted {len(results)}/{len(sources)} PDFs", flush=True)
    results.sort(key=lambda r: r["document"]["source_pdf"])
    all_pages, all_tables, all_cells, all_weekly, all_issues, manifest = [], [], [], [], [], []
    streams = {name: (gzip.open(output/f"{name}.jsonl.gz", "wt", encoding="utf-8") if name in ("layout", "vectors")
                      else (output/f"{name}.jsonl").open("w", encoding="utf-8"))
               for name in ("documents", "pages", "tables", "cells", "weekly_weather", "layout", "vectors", "issues")}
    try:
        for result in results:
            document = result["document"]
            docid = document["document_id"]
            (output/"documents"/f"{docid}.json").write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
            (output/"text"/f"{docid}.txt").write_text(document["full_text"], encoding="utf-8")
            streams["documents"].write(dump(document)+"\n")
            for key, stream_name in (("pages", "pages"), ("tables", "tables"), ("weekly", "weekly_weather"),
                                      ("layouts", "layout"), ("vectors", "vectors"), ("issues", "issues")):
                for record in result[key]:
                    streams[stream_name].write(dump(record)+"\n")
            for table in result["tables"]:
                for cell in table["cells"]:
                    streams["cells"].write(dump(cell)+"\n")
                    all_cells.append(cell)
            all_pages.extend(result["pages"]); all_tables.extend(result["tables"])
            all_weekly.extend(result["weekly"]); all_issues.extend(result["issues"])
            manifest.append({k: document[k] for k in ("document_id", "source_pdf", "source_sha256", "source_bytes", "crop_folder", "crop", "region", "page_count", "title", "districts_raw", "duration_raw")})
            manifest[-1].update(table_count=len(result["tables"]), weekly_record_count=len(result["weekly"]),
                                issue_count=len(result["issues"]))
    finally:
        for stream in streams.values():
            stream.close()
    shared = ["document_id", "source_pdf", "crop_folder", "crop", "region", "page_id", "page_number"]
    write_csv(output/"manifest.csv", manifest, list(manifest[0]))
    write_csv(output/"pages.csv", all_pages, shared+["extraction_method", "blank_page", "native_character_count", "text_character_count", "text", "native_text", "layout_text", "ocr_text", "table_ids", "skipped_image_count", "issues"])
    write_csv(output/"table_cells.csv", all_cells, shared+["table_id", "cell_id", "row_index", "column_index", "bbox", "text", "native_text"])
    write_csv(output/"weekly_weather.csv", all_weekly, shared+["table_id", "cell_id", "calendar_label_raw", "calendar_column", "week_label_raw", "standard_week", "week_cell_id", "month_label_raw", "metric", "metric_label_raw", "metric_mapping", "unit", "value_raw", "value_numeric", "bbox", "extraction_method"])
    # Repeated flags are grouped without dropping the affected page references.
    unique_issues = {dump(issue): issue for issue in all_issues}
    all_issues = list(unique_issues.values())
    write_csv(output/"review_issues.csv", all_issues, ["severity", "code", "page_id", "source_pdf", "page_number", "detail"])
    duplicates = collections.defaultdict(list)
    for doc in manifest:
        duplicates[doc["source_sha256"]].append(doc["source_pdf"])
    summary = {"schema_version": SCHEMA_VERSION, "created_utc": datetime.now(timezone.utc).isoformat(),
               "source_folder": str(source_root), "documents": len(results), "pages": len(all_pages),
               "crop_season_folders": len({r["crop_folder"] for r in manifest}),
               "regions": sorted({r["region"] for r in manifest}), "tables": len(all_tables),
               "physical_table_cells": len(all_cells), "weekly_weather_records": len(all_weekly),
               "native_text_characters": sum(p["native_character_count"] for p in all_pages),
               "page_methods": dict(collections.Counter(p["extraction_method"] for p in all_pages)),
               "skipped_image_occurrences": sum(p["skipped_image_count"] for p in all_pages),
               "issues_by_severity": dict(collections.Counter(i["severity"] for i in all_issues)),
               "issues_by_code": dict(collections.Counter(i["code"] for i in all_issues)),
               "duplicate_pdf_groups": [v for v in duplicates.values() if len(v)>1],
               "dependencies": {"python": sys.version.split()[0], "pymupdf": fitz.VersionBind},
               "limitations": ["Scanned pages are transcriptions requiring source review.",
                   "Native source spelling, ambiguous numbers and private-use glyphs are preserved, not silently corrected.",
                   "Bengali pages retain native text and a supplementary OCR alternative; Bengali weather metric mapping by row order is explicitly labeled.",
                   "Detected table structure and merged cells are automatic; full native text and glyph geometry are the completeness fallback.",
                   "Photographs and embedded raster image payloads are omitted. Raster text inside otherwise native pages is not OCRed.",
                   "No calendar year is inferred. Compressed/range week labels are retained without expanding values.",
                   "The corpus is source material, not a verified or deduplicated supervised training set."]}
    (output/"quality_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT/"BAMIS_All_Crops")
    parser.add_argument("--output", type=Path, default=ROOT/"BAMIS_Dataset")
    parser.add_argument("--tessdata", type=Path, default=ROOT/"extraction_work"/"tessdata")
    parser.add_argument("--workers", type=int, default=4)
    run(parser.parse_args())
