"""One-time offline indexing of prepared NASA daily records; no downloads or extraction."""
import gzip,hashlib,json,math,tarfile
from pathlib import Path
from src.api.storage import ROOT,dumps,fingerprint

VERSION='power-daily-sql.v1'
PARAMETERS=['T2M','T2M_MIN','T2M_MAX','PRECTOTCORR']

def schema(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS weather_daily(grid_id TEXT NOT NULL REFERENCES weather_grids(id),date TEXT NOT NULL,t2m REAL,t2m_min REAL,t2m_max REAL,precipitation_mm_day REAL,missing_reasons TEXT NOT NULL,PRIMARY KEY(grid_id,date));
    CREATE TABLE IF NOT EXISTS weather_daily_partitions(year INTEGER PRIMARY KEY,artifact_path TEXT NOT NULL,sha256 TEXT NOT NULL,archive_sha256 TEXT NOT NULL,selected_rows INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS weather_raw_sources(year INTEGER NOT NULL,parameter TEXT NOT NULL,sha256 TEXT NOT NULL,unit TEXT NOT NULL,time_standard TEXT NOT NULL,PRIMARY KEY(year,parameter));
    ''')

def records_to_sql(record,allowed_grids):
    from datetime import date
    grid=f"{float(record['output_longitude'])}-{float(record['output_latitude'])}"
    if grid not in allowed_grids:return None
    day=record['date'];date.fromisoformat(day)
    if record['time_standard']!='LST':raise ValueError('Unsupported time standard')
    values=record['values'];units=record['units']
    for parameter in PARAMETERS:
        if units[parameter]!=('mm/day' if parameter=='PRECTOTCORR' else 'C'):raise ValueError('Unexpected prepared weather unit')
        value=values[parameter]
        if value is not None and (not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value==-999):raise ValueError('Invalid prepared weather value')
    return (grid,day,*[values[p] for p in PARAMETERS],dumps(record['missing_reasons']))

def install(db,root=ROOT,progress=None):
    schema(db)
    archive_path=root/'data/climate/packages/v1.0.0/soil-to-stars-climate-bgd-v1.0.0.tar.gz'
    expected=archive_path.with_name(archive_path.name+'.sha256').read_text().split()[0]
    archive_hash=hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if archive_hash!=expected:raise ValueError('Sealed archive checksum mismatch')
    grids={r[0] for r in db.execute('SELECT id FROM weather_grids')}
    identity=fingerprint({'archive':archive_hash,'grids':sorted(grids),'version':VERSION})
    old=db.execute("SELECT value FROM meta WHERE key='daily_index_identity'").fetchone()
    if old and old[0]==identity:
        return {'status':'already_indexed','daily_rows':db.execute('SELECT COUNT(*) FROM weather_daily').fetchone()[0],'identity':identity,'annual_parity':verify_annual_parity(db)}
    db.execute('BEGIN IMMEDIATE')
    try:
        for name in ['weather_daily','weather_daily_partitions','weather_raw_sources']:db.execute('DELETE FROM '+name)
        imported=[]
        # Stream forward through gzip once, rather than repeatedly decompressing the archive.
        with tarfile.open(archive_path,'r|gz') as archive:
            for member in archive:
                if '/prepared-v1/' not in member.name or not member.name.endswith('.wide-replay.jsonl.gz') or not Path(member.name).name.split('.')[0].isdigit():continue
                year=int(Path(member.name).name.split('.')[0]);raw=archive.extractfile(member).read();compressed_hash=hashlib.sha256(raw).hexdigest()
                import io
                batch=[];selected=0;sources={}
                with gzip.open(io.BytesIO(raw),'rt',encoding='utf8') as stream:
                    for line in stream:
                        record=json.loads(line);row=records_to_sql(record,grids)
                        if row is None:continue
                        if int(row[1][:4])!=year:raise ValueError('Weather partition year mismatch')
                        batch.append(row);selected+=1
                        for parameter in PARAMETERS:
                            item=(record['raw_artifacts'][parameter],record['units'][parameter],record['time_standard'])
                            if parameter in sources and sources[parameter]!=item:raise ValueError('Raw source identity changed within annual partition')
                            sources[parameter]=item
                        if len(batch)>=4000:db.executemany('INSERT INTO weather_daily VALUES(?,?,?,?,?,?,?)',batch);batch=[]
                if batch:db.executemany('INSERT INTO weather_daily VALUES(?,?,?,?,?,?,?)',batch)
                db.execute('INSERT INTO weather_daily_partitions VALUES(?,?,?,?,?)',(year,member.name,compressed_hash,archive_hash,selected))
                db.executemany('INSERT INTO weather_raw_sources VALUES(?,?,?,?,?)',[(year,param,*value) for param,value in sources.items()])
                imported.append(year)
                if progress:progress(year,selected)
        if sorted(imported)!=list(range(2001,2026)):raise ValueError('Daily archive does not contain exactly 2001–2025')
        from datetime import date
        expected_days=(date(2026,1,1)-date(2001,1,1)).days
        for grid in grids:
            n=db.execute('SELECT COUNT(*) FROM weather_daily WHERE grid_id=?',(grid,)).fetchone()[0]
            if n!=expected_days:raise ValueError('Daily date coverage mismatch')
        verification=verify_annual_parity(db)
        db.execute("INSERT OR REPLACE INTO meta VALUES('daily_index_identity',?)",(identity,));db.commit()
        return {'status':'indexed','annual_parity':verification,'daily_rows':len(grids)*expected_days,'identity':identity,'time_standard':'LST','units':{'temperature':'degC (source C)','precipitation':'mm/day'}}
    except Exception:db.rollback();raise


def verify_annual_parity(db):
    annual={(row['grid_id'],row['year'],row['parameter']):row['value'] for row in db.execute('SELECT grid_id,year,parameter,value FROM weather_annual')}
    checked=0
    for row in db.execute("SELECT grid_id,CAST(substr(date,1,4) AS INTEGER) AS year,AVG(t2m) AS temperature,SUM(precipitation_mm_day) AS precipitation,COUNT(*) AS days,COUNT(t2m) AS temperature_days,COUNT(precipitation_mm_day) AS rain_days FROM weather_daily WHERE date < '2026-01-01' GROUP BY grid_id,substr(date,1,4)"):
        from datetime import date
        days=(date(row['year']+1,1,1)-date(row['year'],1,1)).days
        for parameter,key,count_key in [('T2M','temperature','temperature_days'),('PRECTOTCORR','precipitation','rain_days')]:
            expected=annual[(row['grid_id'],row['year'],parameter)]
            if row['days']!=days or row[count_key]!=days or expected is None or abs(row[key]-expected)>0.001:raise ValueError('Daily/annual weather parity failed')
            checked+=1
    if checked!=len(annual):raise ValueError('Annual index coverage differs from daily archive')
    return {'status':'passed','annual_comparisons':checked,'absolute_tolerance':0.001}
