"""Replay the preserved builder's stage geometry for import-lineage checks.

Adapted without changing the extraction algorithm from
scripts/vendor/bamis/build_planning_dataset.py (clean, STAGE, stages,
stage_for_week). This is source-column matching, not agronomic validation.
The standalone stdlib implementation keeps the normalized build independent
of the upstream builder's spreadsheet dependency.
"""
from collections import defaultdict
import re

STAGE = re.compile(r"seed|sow|transplant|germinat|tiller|vegetat|flower|grain|matur|harvest|ripen|fruit|panicle|pea\s*stage|swell|bud|root|tuber|sprout|spout|boll|squar|canopy|leaf|heading|emergen|nursery|elongat|shoot|sucker", re.I)


def clean(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return re.sub(r"\b(Flowe)\s+(ring)\b|\b(Harve)\s+(sting)\b",
                  lambda match: "".join(part for part in match.groups() if part), text, flags=re.I)


def stages(table, weather):
    ids = {obs["cell_id"] for obs in weather}
    end_row = max(cell["row_index"] for cell in table["cells"] if cell["cell_id"] in ids)
    candidates = defaultdict(list)
    for cell in table["cells"]:
        text = clean(cell["text"])
        if end_row < cell["row_index"] <= end_row + 3 and 2 < len(text) <= 135 and STAGE.search(text):
            if not re.search(r"weather|disease|temperature|rainfall|humidity|requirement", text, re.I):
                candidates[cell["row_index"]].append(cell)
    if not candidates:
        return []
    best = max(candidates.values(), key=len)
    return best if len(best) >= 2 else []


def stage_for_week(stage_cells, week_bbox):
    midpoint = (week_bbox[0] + week_bbox[2]) / 2
    matches = [cell for cell in stage_cells if cell["bbox"][0] <= midpoint <= cell["bbox"][2]]
    return clean(matches[0]["text"]) if matches else ""


def select_stage_candidates(candidates, stage_label, stage_by_column):
    """Narrow only when the original nonblank stage yields one exact match.

    Empty, unknown, conflicting or still ambiguous matches retain every numeric
    alternative. No nearest-column, fuzzy-text or first-candidate fallback.
    """
    if not stage_label:
        return candidates
    matches = [candidate for candidate in candidates if stage_by_column[candidate[0]] == stage_label]
    return matches if len(matches) == 1 else candidates
