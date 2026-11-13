"""Exact historical weather windows; future dates and missing days stay unavailable."""
from datetime import date
from src.compute.rule_engine import inclusive_indicator
PARAMETERS={'T2M':('t2m','degC','mean'),'T2M_MIN':('t2m_min','degC','minimum'),'T2M_MAX':('t2m_max','degC','maximum'),'PRECTOTCORR':('precipitation_mm_day','mm','sum')}

def historical_window(db,grid_id,start,end,parameter):
    first,last=date.fromisoformat(start),date.fromisoformat(end)
    if last<first:raise ValueError('Reversed historical window')
    if parameter not in PARAMETERS:raise ValueError('Unsupported weather metric')
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='weather_daily'").fetchone():return {'status':'unavailable','value':None,'reason':'daily_archive_not_indexed'}
    coverage=db.execute('SELECT MIN(date),MAX(date) FROM weather_daily WHERE grid_id=?',(grid_id,)).fetchone()
    if first<date(2001,1,1) or end>max('2025-12-31',coverage[1] or '2025-12-31') or last>=date.today():return {'status':'unavailable','value':None,'reason':'outside_cached_observation_period; no forecast or extrapolation','cached_start':coverage[0],'cached_end':coverage[1]}
    column,unit,statistic=PARAMETERS[parameter]
    rows=db.execute('SELECT date,'+column+' FROM weather_daily WHERE grid_id=? AND date>=? AND date<=? ORDER BY date',(grid_id,start,end)).fetchall()
    result=inclusive_indicator([r[1] for r in rows],(last-first).days+1,statistic)
    return {**result,'parameter':parameter,'unit':unit,'statistic':statistic,'start':start,'end':end,'grid_id':grid_id,'time_standard':'LST','threshold_inferred':False,'meaning':'historical weather window, not crop suitability or a future prediction'}
