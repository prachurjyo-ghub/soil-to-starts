"""Rebuild the preserved flat CSV in an isolated output directory.

Uses the frozen upstream extraction and unmodified upstream builder, then applies
the recorded exact month-label corrections. Never overwrites assets/.
Requires openpyxl==3.1.5; the normalized-package builder uses only stdlib.
"""
import argparse
import contextlib
import csv
import gzip
import importlib.util
import io
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def rebuild(output):
    inputs = ROOT / "data/catalog/evidence_inputs"
    spec = importlib.util.spec_from_file_location("bamis_upstream", ROOT / "scripts/vendor/bamis/build_planning_dataset.py")
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        documents = work / "BAMIS_Dataset/documents"
        documents.mkdir(parents=True)
        with gzip.open(inputs / "documents.jsonl.gz", "rt", encoding="utf-8") as stream:
            for line in stream:
                doc = json.loads(line)
                (documents / (doc["document_id"] + ".json")).write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        upstream.ROOT, upstream.DATA = work, work / "BAMIS_Dataset"
        for attr, name in (("CSV_PATH", "crop_planning_dataset.csv"), ("XLSX_PATH", "crop_planning_dataset.xlsx"),
                           ("DISTRICT_MAP_PATH", "bamis_region_district_mapping.csv")):
            setattr(upstream, attr, work / name)
        with contextlib.redirect_stdout(io.StringIO()):
            upstream.build()
        rows = list(csv.DictReader(upstream.CSV_PATH.open(encoding="utf-8-sig")))
        aliases = json.loads((inputs / "month_aliases.json").read_text(encoding="utf-8"))
        for row in rows:
            row["month"] = aliases.get(row["month"], row["month"])
        output.mkdir(parents=True, exist_ok=True)
        with (output / "crop_planning_dataset.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=upstream.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        expected = list(csv.DictReader((ROOT / "assets/crop_planning_dataset.csv").open(encoding="utf-8-sig")))
        if rows != expected:
            raise ValueError("Rebuild differs from preserved repository values")
    print(f"PASS: rebuilt {len(rows)} rows with recorded month corrections; all cells match assets")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    rebuild(parser.parse_args().output)
