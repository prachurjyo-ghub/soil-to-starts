"""Download official Tesseract language models for local OCR."""
from pathlib import Path
import hashlib
import json
import urllib.request

root = Path(__file__).resolve().parents[1] / "extraction_work/tessdata"
root.mkdir(parents=True, exist_ok=True)
models = []
for language in ("eng", "ben"):
    path = root / (language+".traineddata")
    url = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/"+path.name
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    models.append({"language": language, "source_url": url,
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
(root/"models.json").write_text(json.dumps(models, indent=2), encoding="utf-8")
print(json.dumps(models, indent=2))
