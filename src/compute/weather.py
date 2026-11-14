"""Exact historical weather windows; future dates and missing days stay unavailable."""
from datetime import date
from statistics import median
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


def comparable_season(db, grid_id, start, end):
    """Summarize the same calendar dates in each complete archive year."""
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if not 0 <= (last - first).days < 366:
        return {'status': 'unavailable', 'reason': 'window_exceeds_one_year'}
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='weather_daily'").fetchone():
        return {'status': 'unavailable', 'reason': 'daily_archive_not_indexed'}

    samples = []
    year_offset = last.year - first.year
    for year in range(2001, 2026 - year_offset):
        try:
            left = first.replace(year=year)
            right = last.replace(year=year + year_offset)
        except ValueError:
            # An exact February 29 endpoint exists only in leap years.
            continue
        record = db.execute("""
            SELECT COUNT(*), COUNT(t2m_max), COUNT(t2m_min), COUNT(precipitation_mm_day),
                   MAX(t2m_max), MIN(t2m_min), SUM(precipitation_mm_day)
            FROM weather_daily WHERE grid_id=? AND date BETWEEN ? AND ?
            """, (grid_id, left.isoformat(), right.isoformat())).fetchone()
        expected = (right - left).days + 1
        if all(record[i] == expected for i in range(4)):
            samples.append({'year': year, 'start': left.isoformat(), 'end': right.isoformat(),
                            'high_c': record[4], 'low_c': record[5], 'rain_mm': round(record[6], 2)})
    if not samples:
        return {'status': 'unavailable', 'reason': 'no_complete_historical_windows'}
    return {
        'status': 'available', 'start': start, 'end': end,
        'reference_years': [2001, 2025], 'grid_id': grid_id,
        'source_id': 'nasa-power-regional-2001-2025', 'time_standard': 'LST',
        'years_used': len(samples), 'samples': samples,
        'median': {key: round(median(sample[key] for sample in samples), 2)
                   for key in ('high_c', 'low_c', 'rain_mm')},
    }
