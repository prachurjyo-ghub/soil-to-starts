"""Replay documented trials on the original observation dates."""

from datetime import date
import json

from src.api.storage import ROOT
from src.compute.weather import historical_window


def replay_trial(db, district_id, grid_id):
    trial = json.loads((ROOT / 'data/rules/rotation_trials.json').read_text())
    if district_id != trial['district_id']:
        return {
            'status': 'unavailable',
            'reason': 'The current historical rotation case is documented for Bogura.',
        }

    horizon = trial['horizon']
    for pattern in trial['patterns']:
        previous_harvest = None
        for crop in pattern['crops']:
            start, harvest = crop['start'], crop['harvest']
            if not horizon['start'] <= start <= horizon['end']:
                raise ValueError('Trial establishment outside the comparison period')
            if previous_harvest and previous_harvest >= start:
                raise ValueError('Trial crop windows overlap')
            crop['intercrop_days'] = (
                (date.fromisoformat(start) - date.fromisoformat(previous_harvest)).days - 1
                if previous_harvest else None
            )
            if harvest is None:
                crop['weather'] = {}
                continue
            if not start <= harvest <= horizon['end']:
                raise ValueError('Trial harvest outside the crop window')
            crop['weather'] = {
                parameter: historical_window(db, grid_id, start, harvest, parameter)
                for parameter in ('T2M_MAX', 'T2M_MIN', 'PRECTOTCORR')
            }
            previous_harvest = harvest
    return {
        **trial,
        'status': 'historical_case_available',
        'grid_id': grid_id,
        'source_id': 'nasa-power-regional-2001-2025',
        'reason': 'The trial uses its published dates. Weather values describe the representative NASA grid. Field preparation and clearance dates were unreported, and the trial control has an unresolved harvest date.',
    }
