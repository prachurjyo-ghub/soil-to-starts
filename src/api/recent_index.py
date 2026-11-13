"""Offline, checksum-verified recent POWER observations. Never fetches at runtime."""
import gzip,hashlib,json,math
from datetime import date,timedelta
from src.api.storage import ROOT,dumps
from src.api.daily_index import schema,PARAMETERS

def install_recent(db,root=ROOT):
    schema(db)
    folder=root/'data/climate/recent';receipt=json.loads((folder/'receipt.json').read_text())
    raw=(folder/'power-recent.jsonl.gz').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt['payload_sha256']:raise ValueError('Recent weather checksum mismatch')
    if receipt['schema']!='recent-power.v1' or receipt['time_standard']!='LST':raise ValueError('Unsupported recent weather contract')
    start,end=date.fromisoformat(receipt['start']),date.fromisoformat(receipt['end'])
    if start<date(2026,1,1) or end<start or end>=date.today():raise ValueError('Recent observations cannot replace archive or forecast future dates')
    grids={r[0] for r in db.execute('SELECT id FROM weather_grids')}
    if grids!=set(receipt['grid_ids']):raise ValueError('Recent grid coverage mismatch')
    for param in PARAMETERS:
        if receipt['sources'][param]['unit']!=('mm/day' if param=='PRECTOTCORR' else 'C'):raise ValueError('Recent weather unit mismatch')
    identity=hashlib.sha256(dumps(receipt).encode()).hexdigest()
    old=db.execute("SELECT value FROM meta WHERE key='recent_weather_identity'").fetchone()
    expected=(end-start).days+1
    if old and old[0]==identity and db.execute('SELECT COUNT(*) FROM weather_daily WHERE date>=? AND date<=?',(receipt['start'],receipt['end'])).fetchone()[0]==expected*len(grids):return {'status':'already_indexed','rows':receipt['rows'],'last_complete_date':receipt['last_complete_date']}
    batch=[];seen=set();latest_complete={}
    for line in gzip.decompress(raw).decode().splitlines():
        item=json.loads(line);grid=item['grid_id'];day=date.fromisoformat(item['date']);values=item['values'];key=(grid,item['date'])
        if grid not in grids or not start<=day<=end or key in seen:raise ValueError('Recent date/grid duplicate or out of coverage')
        seen.add(key)
        vals=[values[p] for p in PARAMETERS]
        if any(v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v==-999) for v in vals):raise ValueError('Invalid recent value')
        if all(v is not None for v in vals[:3]) and not vals[1]<=vals[0]<=vals[2]:raise ValueError('Recent temperature ordering failed')
        if vals[3] is not None and vals[3]<0:raise ValueError('Negative recent precipitation')
        if all(v is not None for v in vals):latest_complete[grid]=max(latest_complete.get(grid,''),item['date'])
        batch.append((grid,item['date'],*vals,dumps(item['missing_reasons'])))
    if len(batch)!=receipt['rows'] or len(batch)!=expected*len(grids):raise ValueError('Recent date coverage incomplete')
    if set(latest_complete)!=grids or min(latest_complete.values())!=receipt['last_complete_date']:raise ValueError('Recent complete-through receipt mismatch')
    db.execute('BEGIN IMMEDIATE')
    try:
        db.execute('DELETE FROM weather_daily WHERE date>=?',(receipt['start'],))
        db.executemany('INSERT INTO weather_daily VALUES(?,?,?,?,?,?,?)',batch)
        db.execute("INSERT OR REPLACE INTO meta VALUES('recent_weather_identity',?)",(identity,))
        db.execute("INSERT OR REPLACE INTO meta VALUES('recent_weather_receipt',?)",(dumps(receipt),))
        db.commit()
    except Exception:db.rollback();raise
    return {'status':'indexed','rows':len(batch),'last_complete_date':receipt['last_complete_date'],'identity':identity}
