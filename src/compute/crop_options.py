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
    """Return up to three distinct crops with an upcoming seasonal calendar."""
    ready = date.fromisoformat(intake['availability']['end'])
    if ready.year == 9999:
        return []
    current = intake['current'].get('crop_id')
    entries = {}
    for row in db.execute(
        'SELECT e.calendar_id,e.payload FROM calendar_entries e JOIN calendars c ON c.id=e.calendar_id WHERE c.region_id=?',
        (context['region_id'],),
    ):
        entries.setdefault(row[0], []).append(json.loads(row[1]))
    candidates = []
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
            end_year, end_month = year + end_offset // 12, end_offset % 12 + 1
            if end_year > 9999:
                continue
            start = date(year, month, 1)
            end = date(end_year, end_month, monthrange(end_year, end_month)[1])
            candidates.append({
                **record, 'crop_id': crop['crop_id'], 'crop_label': labels.get(crop['intake_crop_id'], crop['crop_label']),
                'region': context['region_label'], 'calendar_start': start.isoformat(),
                'calendar_end': end.isoformat(), 'different_from_current': bool(current and crop['intake_crop_id'] != current),
                'first_month_overlaps_field_ready': year == ready.year and month == ready.month,
            })
    candidates.sort(key=lambda item: (
        bool(current) and not item['different_from_current'], item['calendar_start'], item['id']))
    distinct = {}
    for option in candidates:
        distinct.setdefault(option['crop_id'], option)
        if len(distinct) == 3:
            break
    return list(distinct.values())
