"""Shortlist regional crop calendars by their printed month spans."""

from calendar import monthrange
from datetime import date
import json

# Source spellings retained in the catalogue, normalized only for month matching.
MONTHS = {name: n for n, name in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}
MONTHS.update({name[:3]: n for name, n in tuple(MONTHS.items())})
MONTHS.update({'marh': 3, 'ocotober': 10, 'dce': 12})


def month_span(entries):
    months = []
    previous = None
    for entry in sorted(entries, key=lambda item: item['sequence_index']):
        label = (entry.get('month') or '').casefold().replace(' ', '').strip('.')
        if label == previous:
            continue
        previous = label
        parts = label.split('-')
        if len(parts) > 2 or any(part not in MONTHS for part in parts):
            return None
        first, last = MONTHS[parts[0]], MONTHS[parts[-1]]
        for offset in range((last - first) % 12 + 1):
            month = (first + offset - 1) % 12 + 1
            if months and month == months[-1]:
                continue
            if months and month != months[-1] % 12 + 1:
                return None
            months.append(month)
    return (months[0], len(months)) if 1 < len(months) <= 12 else None


def calendar_options(db, context, intake, labels):
    """Return the next three crops and up to two non-overlapping calendar sequences."""
    ready = date.fromisoformat(intake['availability']['end'])
    if ready.year == 9999:
        return [], None
    current = intake['current'].get('crop_id')
    entries = {}
    for row in db.execute(
        'SELECT e.calendar_id,e.payload FROM calendar_entries e JOIN calendars c ON c.id=e.calendar_id WHERE c.region_id=?',
        (context['region_id'],),
    ):
        entries.setdefault(row[0], []).append(json.loads(row[1]))
    candidates = []
    occurrences = []
    for crop in context['regional_catalogue']:
        for record in crop['calendars']:
            if record['season'] not in {'Rabi', 'Kharif-1', 'Kharif', 'Aus', 'Aman', 'Boro'}:
                continue
            span = month_span(entries.get(record['id'], []))
            if span is None:
                continue
            month, duration = span
            # An ongoing calendar might already be beyond its establishment phase.
            # Use its next first month, or the current one when the land is ready within it.
            year = ready.year + (month < ready.month)
            end_offset = month - 1 + duration - 1
            end_month = end_offset % 12 + 1
            for occurrence_year in range(year, min(year + 2, 10000)):
                end_year = occurrence_year + end_offset // 12
                if end_year > 9999:
                    continue
                start = date(occurrence_year, month, 1)
                end = date(end_year, end_month, monthrange(end_year, end_month)[1])
                occurrence = {
                    **record, 'crop_id': crop['crop_id'], 'crop_label': labels.get(crop['intake_crop_id'], crop['crop_label']),
                    'region': context['region_label'], 'calendar_start': start.isoformat(),
                    'calendar_end': end.isoformat(), 'different_from_current': bool(current and crop['intake_crop_id'] != current),
                    'first_month_overlaps_field_ready': occurrence_year == ready.year and month == ready.month,
                }
                occurrences.append(occurrence)
                if occurrence_year == year:
                    candidates.append(occurrence)
    candidates.sort(key=lambda item: (
        bool(current) and not item['different_from_current'], item['calendar_start'], item['id']))
    distinct = {}
    for option in candidates:
        distinct.setdefault(option['crop_id'], option)
        if len(distinct) == 3:
            break
    horizon_month = (ready.month - 2) % 12 + 1
    horizon_year = min(9999, ready.year + (1 if ready.month == 1 else 2))
    horizon_end = date(horizon_year, horizon_month, monthrange(horizon_year, horizon_month)[1]).isoformat()
    scenarios = rotation_sequences(occurrences, horizon_end, current)
    return list(distinct.values()), {
        'start': ready.isoformat(), 'end': horizon_end, 'sequences': scenarios,
    }


def rotation_sequences(occurrences, horizon_end, current):
    eligible = sorted(
        (item for item in occurrences if item['calendar_end'] <= horizon_end),
        key=lambda item: (item['calendar_start'], item['calendar_end'], item['id']),
    )
    best = {}
    for first in eligible:
        for second in eligible:
            if second['calendar_start'] <= first['calendar_end'] or second['crop_id'] == first['crop_id']:
                continue
            for third in eligible:
                key = (first['crop_id'], second['crop_id'], third['crop_id'])
                if third['calendar_start'] <= second['calendar_end'] or len(set(key)) != 3:
                    continue
                score = (
                    bool(current) and not first['different_from_current'],
                    first['calendar_start'], third['calendar_end'],
                    tuple(item['id'] for item in (first, second, third)),
                )
                if key not in best or score < best[key][0]:
                    best[key] = (score, (first, second, third))
    ranked = sorted(best.values(), key=lambda item: item[0])
    return [{'steps': steps} for _, steps in ranked[:2]]
