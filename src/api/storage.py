"""Local SQLite evidence catalogue and immutable anonymous assessment records."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3

from src.compute.metric_contract import METRICS, canonical_observation
INDEX_VERSION='local-evidence-index.v4'

ROOT = Path(__file__).resolve().parents[2]
CATALOG_FILES = ['crops.json','regions.json','district_memberships.json','calendars.json','entries.jsonl','weather_normals.jsonl','source_artifacts.json','weather_definitions.json','candidate_evidence.json','rule_compatibility.json','source_reviews.json','quarantine.json']

def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def fingerprint(value):
    return hashlib.sha256(dumps(value).encode()).hexdigest()

def paths(root):
    base = root / 'data/catalog/normalized'
    return [base/name for name in CATALOG_FILES] + [root/'prototype/public/data/climate-history.json', root/'data/rules/registry.json', root/'data/integration/crop_aliases.json', root/'data/climate/ui_climate_receipt.json', base/'receipt.json', root/'data/climate/recent/receipt.json', root/'data/climate/recent/power-recent.jsonl.gz', root/'data/rules/exposure_references.json']

def source_identity(root=ROOT):
    base=root/'data/catalog/normalized'
    receipt=json.loads((base/'receipt.json').read_text())
    for name in CATALOG_FILES:
        actual=hashlib.sha256((base/name).read_bytes()).hexdigest()
        if actual!=receipt['outputs'][name]:raise ValueError('Crop evidence checksum mismatch: '+name)
    weather_receipt=json.loads((root/'data/climate/ui_climate_receipt.json').read_text())
    if hashlib.sha256((root/'prototype/public/data/climate-history.json').read_bytes()).hexdigest()!=weather_receipt['payload_sha256']:raise ValueError('Climate payload checksum mismatch')
    return fingerprint({'index_version':INDEX_VERSION,'artifacts':{str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths(root)}})

def connect(path=None):
    path = Path(path or os.environ.get('STS_DB_PATH', ROOT/'cache/application/soil-to-stars.sqlite3')).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(path, timeout=20)
    os.chmod(path, 0o600)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS crops(id TEXT PRIMARY KEY,label TEXT NOT NULL,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS crop_aliases(intake_id TEXT PRIMARY KEY,crop_id TEXT REFERENCES crops(id),payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS regions(id TEXT PRIMARY KEY,label TEXT NOT NULL,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS districts(id TEXT PRIMARY KEY,region_id TEXT REFERENCES regions(id),payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS calendars(id TEXT PRIMARY KEY,crop_id TEXT REFERENCES crops(id),region_id TEXT REFERENCES regions(id),source_id TEXT REFERENCES sources(id),payload TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS calendar_region_crop ON calendars(region_id,crop_id);
    CREATE TABLE IF NOT EXISTS calendar_entries(id TEXT PRIMARY KEY,calendar_id TEXT REFERENCES calendars(id),payload TEXT NOT NULL,weather_payload TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS entry_calendar ON calendar_entries(calendar_id);
    CREATE TABLE IF NOT EXISTS crop_observations(entry_id TEXT NOT NULL REFERENCES calendar_entries(id),metric_id TEXT NOT NULL,value REAL,unit TEXT NOT NULL,nasa_parameter TEXT,definition_id TEXT NOT NULL,source_id TEXT NOT NULL REFERENCES sources(id),missing_reason TEXT,usable_as_threshold INTEGER NOT NULL CHECK(usable_as_threshold=0),PRIMARY KEY(entry_id,metric_id));
    CREATE INDEX IF NOT EXISTS crop_observation_metric ON crop_observations(metric_id,entry_id);
    CREATE TABLE IF NOT EXISTS rule_candidates(id TEXT PRIMARY KEY,activation_status TEXT NOT NULL,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS rules(id TEXT PRIMARY KEY,activation_status TEXT NOT NULL,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS weather_grids(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS weather_annual(grid_id TEXT NOT NULL REFERENCES weather_grids(id),parameter TEXT NOT NULL,year INTEGER NOT NULL,value REAL,unit TEXT NOT NULL,statistic TEXT NOT NULL,chart_sha256 TEXT NOT NULL,PRIMARY KEY(grid_id,parameter,year));
    CREATE TABLE IF NOT EXISTS submissions(id TEXT PRIMARY KEY,created_at_utc TEXT NOT NULL,input_fingerprint TEXT NOT NULL,intake_json TEXT NOT NULL,kind TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS results(id TEXT PRIMARY KEY,submission_id TEXT NOT NULL REFERENCES submissions(id),created_at_utc TEXT NOT NULL,result_fingerprint TEXT NOT NULL,result_json TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS result_submission ON results(submission_id);
    ''')
    return db

def seed(db,root=ROOT):
    identity=source_identity(root)
    base=root/'data/catalog/normalized'
    load=lambda name:json.loads((base/name).read_text())
    db.execute('BEGIN IMMEDIATE')
    try:
        old=db.execute("SELECT value FROM meta WHERE key='source_identity'").fetchone()
        if old and old['value']==identity:
            db.rollback();return identity
        weather=json.loads((root/'prototype/public/data/climate-history.json').read_text())
        old_weather=metadata(db,'weather_metadata')
        same_weather=bool(old_weather and old_weather.get('archive_sha256')==weather.get('archive_sha256') and {r[0] for r in db.execute('SELECT id FROM weather_grids')}==set(weather['grids']))
        # Preserve independently identified daily data when only crop/catalogue metadata changes.
        # Submitted inputs/results are immutable in either case.
        if not same_weather and db.execute("SELECT 1 FROM sqlite_master WHERE name='weather_daily'").fetchone():
            db.execute('DELETE FROM weather_daily');db.execute('DELETE FROM weather_daily_partitions');db.execute('DELETE FROM weather_raw_sources');db.execute("DELETE FROM meta WHERE key='daily_index_identity'")
        for table in ['crop_observations','weather_annual','rule_candidates','calendar_entries','calendars','districts','rules']+([] if same_weather else ['weather_grids'])+['sources','regions','crop_aliases','crops']:
            db.execute('DELETE FROM '+table)
        crops,regions=load('crops.json'),load('regions.json')
        db.executemany('INSERT INTO crops VALUES(?,?,?)',[(x['crop_id'],x['original_label'],dumps(x)) for x in crops])
        db.executemany('INSERT INTO regions VALUES(?,?,?)',[(x['region_id'],x['original_label'],dumps(x)) for x in regions])
        aliases=json.loads((root/'data/integration/crop_aliases.json').read_text())['rows']
        db.executemany('INSERT INTO crop_aliases VALUES(?,?,?)',[(x['intake_id'],x['source_crop_id'],dumps(x)) for x in aliases])
        sources=load('source_artifacts.json')
        db.executemany('INSERT INTO sources VALUES(?,?)',[(x.get('source_id') or 'artifact-'+fingerprint(x['path'])[:20],dumps(x)) for x in sources])
        weather=json.loads((root/'prototype/public/data/climate-history.json').read_text())
        memberships=load('district_memberships.json')
        for d in weather['districts']:
            match=[m for m in memberships if m['district']==d['en']]
            if len(match)!=1:raise ValueError('District must resolve to one preserved BAMIS membership')
            db.execute('INSERT INTO districts VALUES(?,?,?)',(d['id'],match[0]['region_id'],dumps({**d,'membership':match[0]})))
        calendars=load('calendars.json')
        db.executemany('INSERT INTO calendars VALUES(?,?,?,?,?)',[(c['calendar_id'],c['crop_id'],c['region_id'],c['source_id'],dumps(c)) for c in calendars])
        normals={x['entry_id']:x for x in map(json.loads,(base/'weather_normals.jsonl').read_text().splitlines())}
        entries=list(map(json.loads,(base/'entries.jsonl').read_text().splitlines()))
        db.executemany('INSERT INTO calendar_entries VALUES(?,?,?,?)',[(x['entry_id'],x['calendar_id'],dumps(x),dumps(normals[x['entry_id']])) for x in entries])
        calendar_sources={c['calendar_id']:c['source_id'] for c in calendars}
        observations=[]
        for entry in entries:
            normal=normals[entry['entry_id']]
            for field,value in normal['values'].items():
                unit={'rainfall_mm':'mm','temp_min_c':'degC','temp_max_c':'degC','temp_mean_c':'degC','humidity_mean_pct':'%','sunshine_hours':'hours','wind_speed_kmh':'km/hour'}[field]
                source=calendar_sources[entry['calendar_id']]
                observation=canonical_observation(field,value,unit,source)
                observations.append((entry['entry_id'],observation['metric_id'],observation['value'],observation['unit'],observation['nasa_parameter'],normal['definition_set_id'],source,None if value is not None else 'not_reported_in_source',0))
        db.executemany('INSERT INTO crop_observations VALUES(?,?,?,?,?,?,?,?,?)',observations)
        db.executemany('INSERT INTO rule_candidates VALUES(?,?,?)',[(c['rule_evidence_id'],c['activation_status'],dumps(c)) for c in load('candidate_evidence.json')])
        registry=json.loads((root/'data/rules/registry.json').read_text())
        if registry.get('schema_version')!='crop-rules.v1':raise ValueError('Unsupported rule registry')
        for rule in registry['rules']:
            db.execute('INSERT INTO rules VALUES(?,?,?)',(rule['rule_id'],rule.get('activation_status','inactive'),dumps(rule)))
        db.executemany('INSERT INTO weather_grids VALUES(?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',[(key,dumps(value)) for key,value in weather['grids'].items()])
        for grid_id,grid in weather['grids'].items():
            for parameter,metric in grid['metrics'].items():
                db.executemany('INSERT INTO weather_annual VALUES(?,?,?,?,?,?,?)',[(grid_id,parameter,year['year'],year['value'],metric['unit'],metric['statistic'],metric['chart_sha256']) for year in metric['annual']])
        meta_values={'source_identity':identity,'weather_metadata':{k:v for k,v in weather.items() if k not in ['grids','districts']},'weather_definitions':load('weather_definitions.json'),'candidate_evidence':load('candidate_evidence.json'),'rule_compatibility':load('rule_compatibility.json'),'source_reviews':load('source_reviews.json'),'rule_registry':registry,'quarantine':load('quarantine.json'),'schema_version':2}
        db.executemany('INSERT OR REPLACE INTO meta VALUES(?,?)',[(key,dumps(value)) for key,value in meta_values.items()])
        # Identity is stored as plain text so startup comparisons do not depend on JSON quoting.
        db.execute("UPDATE meta SET value=? WHERE key='source_identity'",(identity,))
        db.commit();return identity
    except Exception:
        db.rollback();raise

def metadata(db,key):
    row=db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
    return json.loads(row['value']) if row else None

def counts(db):
    result={name:db.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in ['crops','crop_aliases','regions','districts','calendars','calendar_entries','crop_observations','rule_candidates','rules','weather_grids','weather_annual','submissions','results']}
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='weather_daily'").fetchone():result['weather_daily']=db.execute('SELECT COUNT(*) FROM weather_daily').fetchone()[0]
    return result
