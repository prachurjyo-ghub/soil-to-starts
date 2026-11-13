"""Reproducible, explicitly labeled visual transcription of the sole scanned PDF.

Coordinates below are pixels in its original 826 x 959 image. No image is copied
to the final dataset. Original spelling and numbers are retained.
"""
from pathlib import Path
import hashlib
import json
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "BAMIS_All_Crops/Wheat/Sylhet/2060.pdf"
DOCID = "bamis_2060_b0ae6e30"
with fitz.open(SOURCE) as doc:
    image_bbox = doc[0].get_image_info()[0]["bbox"]


def bbox(x0, y0, x1, y1):
    a, b, c, d = image_bbox
    return [a+x0/826*(c-a), b+y0/959*(d-b), a+x1/826*(c-a), b+y1/959*(d-b)]


def table():
    return {"bbox": None, "rows": [], "cell_bboxes": []}


def add(t, y0, y1, bounds, values):
    assert len(bounds) == len(values)+1
    t["rows"].append(values)
    t["cell_bboxes"].append([bbox(bounds[i], y0, bounds[i+1], y1) for i in range(len(values))])


tables = []
t = table()
add(t, 48, 84, [22, 125, 560, 813], ["Region:\nSylhet", "Wheat", "Duration: 119 days"])
add(t, 84, 99, [22, 125, 248, 410, 560, 732, 813], ["Months", "November", "December", "January", "February", "March"])
xs = [22, 125, 162, 205, 248, 291, 334, 372, 410, 447, 485, 523, 560, 603, 646, 689, 732, 775, 813]
rows = [
    ("Std.Week/Normal", "46 47 48 49 50 51 52 1 2 3 4 5 6 7 8 9 10"),
    ("Rainfall (mm)", "8.5 0.5 7.0 0.5 4.5 1.0 4.0 0.0 0.5 0.5 1.0 2.5 4.0 8.0 11.5 11.0 10.5"),
    ("Max. Temp. (°C)", "29.6 29.0 28.2 27.8 26.9 26.1 25.7 25.3 24.7 25.1 25.8 26.5 27.2 28.2 28.9 30.0 31.0"),
    ("Min. Temp. (°C)", "17.3 16.6 15.3 14.3 13.7 12.6 12.0 11.4 11.3 11.3 11.1 12.1 12.6 13.7 14.4 15.4 16.7"),
    ("Mean Temp. (°C)", "23.5 22.8 21.7 21.1 20.3 19.3 18.8 18.3 18.0 18.2 18.4 19.3 19.9 21.0 21.6 22.7 23.8"),
    ("RHmax (%)", "95.2 95.3 95.5 94.7 95.7 95.3 96.1 95.8 96.1 95.5 94.9 94.3 92.9 92.8 92.5 91.7 90.9"),
    ("RHMin (%)", "56.2 54.4 53.5 51.4 53.6 53.0 52.7 53.5 53.9 50.7 48.1 45.8 42.3 42.5 41.7 40.8 41.1"),
    ("RHmean (%)", "75.7 74.9 74.5 73.0 74.6 74.2 74.4 74.6 75.0 73.1 71.5 70.1 67.6 67.7 67.1 66.2 66.0"),
    ("SShr (hrs)", "55.5 56.5 56.0 55.5 50.5 51.5 50.5 51.0 45.0 48.0 51.0 50.5 55.0 53.5 55.5 56.0 55.0"),
    ("WD (deg)", "180 184 190 177 186 191 203 200 211 213 219 213 218 217 208 219 203"),
    ("WS(Km/hr)", "4.3 4.6 4.3 4.2 4.5 4.5 4.3 4.6 4.9 5.1 4.8 6.1 6.5 6.9 7.1 6.8 6.8"),
]
ys = [99, 117, 132, 147, 162, 178, 193, 208, 223, 238, 253, 269]
for i, (label, values) in enumerate(rows):
    vals = values.split()
    assert len(vals) == 17
    add(t, ys[i], ys[i+1], xs, [label]+vals)
add(t, 377, 406, [22, 125, 248, 372, 560, 603, 732, 813],
    ["", "sowing", "Germination", "Vegetative Growth", "Flowe\nring", "Grain Formation", "Maturity to\nHarvesting"])
t["bbox"] = bbox(22, 48, 813, 406)
tables.append(t)

xs = [22, 248, 372, 560, 603, 732, 813]
t = table()
add(t, 406, 421, [22, 813], ["Favourable Weather Conditions"])
for y0, y1, values in [
    (421, 437, ["Minimum temperature", "3 to 4.5°C", "", "", "", "cooler nights"]),
    (437, 454, ["Optimum temperature", "Around 25°C", "", "", "", ""]),
    (454, 470, ["Maximum Cardinal temperature", "30-32°C", "", "", "", ""]),
    (470, 503, ["Mean Daily Temperature", "", "15 to 20°C", "15 to\n20° C", "", ""]),
    (503, 520, ["Soil Moisture", "High", "", "", "", "dryness"]),
    (520, 552, ["Solar radiation", "", "", "", "", "Bright sunny\ndays"]),
    (552, 601, ["daily consumptive water use", "", "0.17 to 0.87", "0.17\nto\n0.87", "0.17 to 0.87", ""]),
    (601, 633, ["Normal Phase wise water requirement\n(mm)", "47", "128", "77", "137", "39"]),
]:
    add(t, y0, y1, xs, values)
t["bbox"] = bbox(22, 406, 813, 633)
tables.append(t)

t = table()
add(t, 633, 651, [22, 813], ["Congenial Weather Condition for Pests & Diseases"])
add(t, 651, 668, [22, 248, 372, 732, 813], ["Leaf rust", "", "Temperature 15-25°C, rain and high dew", ""])
add(t, 668, 764, [22, 248, 372, 560, 603, 732, 813],
    ["Stem borer", "", "Maximum, minimum and average temperature ranged from 31.9-33.9°C, 22.2-26.3°C and 26.9-29.5°C, respectively. Average relative humidity of 80 per cent and rainfall", "", "", ""])
add(t, 764, 813, [22, 248, 372, 732, 813],
    ["Aphid", "", "Mean temperature 18.7°C and relative humidity percentage 71.0%, mean weekly temperature 29.1°C and relative humidity 55%", ""])
t["bbox"] = bbox(22, 633, 813, 813)
tables.append(t)

t = table()
add(t, 813, 830, [22, 813], ["Weather Warning"])
for y0, y1, values in [
    (830, 847, ["Rainfall", ">50 mm/day", ">100mm/day", ">100mm/day"]),
    (847, 863, ["Duration of wet spell", ">50 mm for 3-4 days", ">75 mm for 3-4 days", ">50mm for 3-4 days"]),
    (863, 880, ["Cloudy Weather", "", "Cloudy Weather", "Cloudy Weather"]),
    (880, 897, ["Drought", "20 days", "20 days", "20 days"]),
    (897, 913, ["High wind", ">50 km/hr", ">50 km/hr", ">50 km/hr"]),
    (913, 930, ["Maximum Temperature", ">30°C", ">30°C", ">30°C"]),
    (930, 950, ["Minimum Temperature", "<15°C", "<15°C", "<15°C"]),
]:
    add(t, y0, y1, [22, 248, 372, 603, 813], values)
t["bbox"] = bbox(22, 813, 813, 950)
tables.append(t)

title = "Crop Weather Calendar of Wheat: Sylhet Region (Districts: Sylhet, Moulvibazar, Sunamganj, Habiganj) Bangladesh"
text = title+"\n\n"+"\n\n".join("\n".join(" | ".join(v.replace("\n", " ") for v in row) for row in t["rows"]) for t in tables)
result = {"document_id": DOCID, "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "method": "visual_transcription", "review_required": True,
          "notes": "Transcribed from the original embedded 826x959 scan, not inferred from another region. Degree symbols rendered as Unicode. Source spelling/values retained. Review scan before accuracy-sensitive use.",
          "text": text, "tables": tables}
out = ROOT / "scripts/transcriptions" / (DOCID+".json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(out)
