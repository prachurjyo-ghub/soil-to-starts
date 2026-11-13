"""Freeze an existing local extraction without changing its sources (stdlib only).

python scripts/import_crop_evidence.py --source-root PATH
Run only when intentionally refreshing the source snapshot; review resulting diffs.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/catalog/evidence_inputs"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root.resolve()
    old = list(csv.DictReader((source / "crop_planning_dataset.csv").open(encoding="utf-8-sig")))
    current = list(csv.DictReader((ROOT / "assets/crop_planning_dataset.csv").open(encoding="utf-8-sig")))
    if len(old) != len(current):
        raise ValueError("Row counts changed: reconcile explicitly before import")
    corrections, aliases = [], {}
    for n, (a, b) in enumerate(zip(old, current), 2):
        changed = [key for key in a if a[key] != b[key]]
        if changed and changed != ["month"]:
            raise ValueError(f"Non-month change at CSV line {n}: {changed}")
        if changed:
            if a["month"] in aliases and aliases[a["month"]] != b["month"]:
                raise ValueError("Conflicting month mapping")
            aliases[a["month"]] = b["month"]
            corrections.append(dict(csv_line=n, source_pdf=b["source_pdf"], source_page=b["source_page"],
                                    standard_week=b["standard_week"], original_value=a["month"],
                                    corrected_value=b["month"], field="month",
                                    reason="Preserve existing repository exact-label normalization; no week inference",
                                    evidence="assets/crop_planning_dataset_README.md; paired external/repository row"))
    DEST.mkdir(parents=True, exist_ok=True)
    artifacts = []
    with (DEST / "documents.jsonl.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream:
            for path in sorted((source / "BAMIS_Dataset/documents").glob("*.json")):
                doc = json.loads(path.read_text(encoding="utf-8"))
                pdf = source / doc["source_pdf"]
                actual = sha(pdf)
                if actual != doc["source_sha256"]:
                    raise ValueError("Source PDF checksum mismatch: " + str(pdf))
                stream.write((json.dumps(doc, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode())
                artifacts.append(dict(source_id=doc["document_id"], path=doc["source_pdf"],
                                      sha256=actual, bytes=pdf.stat().st_size,
                                      extraction_path="BAMIS_Dataset/documents/" + path.name,
                                      extraction_sha256=sha(path),
                                      source_url=None, acquisition_date=None,
                                      rights="unreviewed; do not assume redistribution permission",
                                      acquisition="Existing user-provided local archive; original download log unavailable"))
    vendor = ROOT / "scripts/vendor/bamis"
    vendor.mkdir(parents=True, exist_ok=True)
    for name in ("build_planning_dataset.py", "extract_dataset.py", "validate_dataset.py",
                 "prepare_scanned_transcription.py", "prepare_ocr_models.py"):
        original = source / "scripts" / name
        (vendor / name).write_bytes(original.read_bytes())
        artifacts.append(dict(path="scripts/" + name, sha256=sha(original), role="Unmodified external script"))
    # Scanned transcription is an explicit upstream input, not a newly verified scan.
    for path in sorted((source / "scripts/transcriptions").glob("*.json")):
        target = vendor / "transcriptions" / path.name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(path.read_bytes())
    for name, value in (("source_artifacts.json", artifacts), ("month_aliases.json", aliases),
                        ("month_corrections.json", corrections)):
        (DEST / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(artifacts)} source/script artifacts; preserved {len(corrections)} month corrections")


if __name__ == "__main__":
    main()
