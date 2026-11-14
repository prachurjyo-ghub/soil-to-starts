"""Descriptive historical summaries only; no crop suitability, attribution or forecast."""

from math import fsum


def aggregate(rows, parameter):
    by_year = {}
    for row in rows:
        year, month = map(int, row['date'].split('-'))
        by_year.setdefault(year, []).append(row)
    annual = []
    for year in range(2001, 2026):
        months = by_year.get(year, [])
        complete = len(months) == 12 and len({m['date'] for m in months}) == 12 and all(m['coverage'] == 'complete' and m['value'] is not None and m['valid_days'] == m['expected_days'] for m in months)
        value = None
        if complete:
            value = fsum(m['value'] for m in months) if parameter == 'PRECTOTCORR' else fsum(m['value'] * m['valid_days'] for m in months) / sum(m['valid_days'] for m in months)
        annual.append({'year': year, 'value': round(value, 4) if value is not None else None})
    periods = []
    for start,end in [(2001,2010),(2016,2025)]:
        years = [y for y in annual if start <= y['year'] <= end]
        usable = [y['value'] for y in years if y['value'] is not None]
        periods.append({'start':start,'end':end,'valid_years':len(usable),'mean':round(fsum(usable)/10,4) if len(usable)==10 else None})
    return {'annual':annual,'periods':periods,'difference':round(periods[1]['mean']-periods[0]['mean'],4) if all(p['mean'] is not None for p in periods) else None}


def seasonal_profile(rows, parameter):
    """Compare complete monthly values in equal ten-year periods, never fill gaps."""
    result=[]
    for month in range(1,13):
        periods=[]
        for start,end in [(2001,2010),(2016,2025)]:
            selected=[r for r in rows if start<=int(r['date'][:4])<=end and int(r['date'][5:7])==month]
            usable=[r for r in selected if r['coverage']=='complete' and r['value'] is not None and r['valid_days']==r['expected_days']]
            complete=len(usable)==10 and len({r['date'] for r in usable})==10
            periods.append({'start':start,'end':end,'valid_months':len(usable),'mean':round(fsum(r['value'] for r in usable)/10,4) if complete else None})
        result.append({'month':month,'periods':periods})
    return result
