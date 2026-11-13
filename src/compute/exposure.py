"""Observed weather exceedances against explicitly transcribed publisher warnings."""
from datetime import date,timedelta
import json
from src.api.storage import ROOT,metadata

def assess_exposure(db,intake,region_id,today=None):
    today=today or date.today()
    unavailable=lambda reason:{'status':'unavailable','reason':reason,'indicators':[],'meaning':'No crop damage or probability inferred.'}
    if intake['current']['state']!='growing':return unavailable('no_current_crop')
    start=intake['current'].get('sown_on')
    if not start:return unavailable('sowing_date_required; growth stage is not inferred')
    reference=next((r for r in json.loads((ROOT/'data/rules/exposure_references.json').read_text())['references'] if r['crop_id']==intake['current']['crop_id'] and r['region_id']==region_id),None)
    if not reference:return unavailable('no_source_verified_warning_reference_for_this_crop_and_source_region')
    district=json.loads(db.execute('SELECT payload FROM districts WHERE id=?',(intake['location']['district_id'],)).fetchone()[0]);grid=district['grid']
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='weather_daily'").fetchone():return unavailable('daily_weather_not_installed')
    latest=db.execute('SELECT MAX(date) FROM weather_daily WHERE grid_id=? AND t2m IS NOT NULL AND t2m_min IS NOT NULL AND t2m_max IS NOT NULL AND precipitation_mm_day IS NOT NULL',(grid,)).fetchone()[0]
    if not latest:return unavailable('no_complete_observed_weather')
    end=min(intake['availability']['end'],latest,(today-timedelta(days=1)).isoformat())
    first,last=date.fromisoformat(start),date.fromisoformat(end)
    if first>last:return unavailable('crop_window_has_no_cached_observations; future_weather_not_predicted')
    expected=(last-first).days+1
    observations=db.execute('SELECT date,t2m_max,t2m_min,precipitation_mm_day FROM weather_daily WHERE grid_id=? AND date>=? AND date<=? ORDER BY date',(grid,start,end)).fetchall()
    indicators=[]
    for condition in reference['conditions']:
        valid=[r for r in observations if r[condition['column']] is not None]
        hit=[r['date'] for r in valid if (r[condition['column']]>condition['threshold'] if condition['operator']=='>' else r[condition['column']]<condition['threshold'])]
        complete=len(valid)==expected
        indicators.append({k:v for k,v in condition.items() if k!='column'}|{'status':'complete' if complete else 'incomplete','exceedance_days':len(hit) if complete else None,'observed_exceedance_days':len(hit),'valid_days':len(valid),'expected_days':expected,'dates':hit,'missing_days':expected-len(valid)})
    return {'status':'complete' if all(i['status']=='complete' for i in indicators) else 'incomplete','start':start,'end':end,'as_of':latest,'grid_id':grid,'time_standard':'LST','spatial_support':'district-anchor NASA grid, not field measurements','indicators':indicators,'reference':reference,'weather_source_ids':['nasa-power-regional-2001-2025']+(['nasa-power-recent-2026'] if end>'2025-12-31' else []),'meaning':'Observed warning-level exceedance counts, not a vulnerability score, diagnosis, crop loss or forecast.'}
