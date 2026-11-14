"""Single-request JSON bridge for the Next.js server; Python stdlib only, no HTTP port."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from datetime import datetime,timezone
import json
import uuid
from src.api.storage import connect,seed,dumps,fingerprint,counts
from src.compute.assessment import assess,VERSION


def now():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def uuid_value(value):
    try:return str(uuid.UUID(value))==value
    except (ValueError,TypeError,AttributeError):return False

def validate_shape(intake,db):
    """Defence in depth. The HTTP bridge first runs the shared full intake validator."""
    if not isinstance(intake,dict) or intake.get('schema_version')!='farmer-intake.v2':raise ValueError('Invalid intake schema')
    if not db.execute('SELECT 1 FROM districts WHERE id=?',(intake.get('location',{}).get('district_id'),)).fetchone():raise ValueError('Unsupported district')
    if intake.get('priority') not in ['water','soil_rotation','balanced']:raise ValueError('Invalid priority')
    if intake.get('irrigation',{}).get('access') not in ['rainfed','limited','reliable']:raise ValueError('Invalid water access')
    if intake.get('current',{}).get('state') not in ['growing','fallow']:raise ValueError('Invalid current crop')
    current=intake.get('current',{})
    if current['state']=='growing' and not db.execute('SELECT 1 FROM crop_aliases WHERE intake_id=?',(current.get('crop_id'),)).fetchone():raise ValueError('Unmapped crop identity')
    from datetime import date
    dates=intake.get('availability',{});start=date.fromisoformat(dates['start']);end=date.fromisoformat(dates['end'])
    if end<start or dates.get('kind') not in ['date','window']:raise ValueError('Invalid availability')
    for k in ['crop_history','baseline']:
        if not isinstance(intake.get(k),dict):raise ValueError('Missing input group')
    dumps(intake)

def handle(message,db_path=None):
    operation=message.get('operation');db=connect(db_path)
    try:
        try:identity=seed(db)
        except Exception:
            return {'http_status':503,'body':{'status':'error','reason':'Local evidence integrity/setup check failed. Rebuild or verify the packaged data before retrying.','recoverable':False}}
        if operation=='health':return {'http_status':200,'body':{'status':'ok','service':'local-evidence-api.v1','database':'SQLite local file','source_identity':identity,'counts':counts(db),'scientific_planning':'incomplete: reviewed executable rules required','model_training':'not performed; no labelled crop outcomes'}}
        if operation in ['result','submission']:
            key=message.get('id')
            if not uuid_value(key):return {'http_status':404,'body':{'status':'not_found'}}
            sql='SELECT r.result_json,s.intake_json,s.id AS sid FROM results r JOIN submissions s ON s.id=r.submission_id WHERE '+('r.id=?' if operation=='result' else 's.id=? ORDER BY r.created_at_utc DESC LIMIT 1')
            row=db.execute(sql,(key,)).fetchone()
            if not row:return {'http_status':404,'body':{'status':'not_found'}}
            result = json.loads(row['result_json'])
            body = {'intake':json.loads(row['intake_json']), 'result':result, 'submission_id':row['sid']}
            if result.get('versions', {}).get('method') != VERSION or result.get('versions', {}).get('catalogue') != identity:
                body['refresh_required'] = True
            return {'http_status':200,'body':body}
        if operation not in ['plan','climate','current_crop']:return {'http_status':400,'body':{'status':'invalid_input','reason':'Unsupported operation'}}
        intake=message.get('intake');validate_shape(intake,db)
        output=assess(db,intake,identity)
        if operation=='climate':return {'http_status':200,'body':output['climate']}
        if operation=='current_crop':return {'http_status':200,'body':{**output['current_crop_assessment'],'sources':output['sources'],'data_mode':'local_evidence'}}
        timestamp=now();submission_id=str(uuid.uuid4());result_id=str(uuid.uuid4());input_hash=fingerprint(intake)
        result_hash=fingerprint({'intake':intake,'analysis':output})
        output.update({'input_fingerprint':input_hash,'result_fingerprint':result_hash,'generated_at_utc':timestamp,'submission_id':submission_id,'result_id':result_id,'result_url':'/api/results/'+result_id,'persistence':{'status':'saved','storage':'local_sqlite','anonymous':True,'account_required':False}})
        with db:
            db.execute('INSERT INTO submissions VALUES(?,?,?,?,?)',(submission_id,timestamp,input_hash,dumps(intake),message.get('kind','field')))
            db.execute('INSERT INTO results VALUES(?,?,?,?,?)',(result_id,submission_id,timestamp,result_hash,dumps(output)))
        return {'http_status':200,'body':output}
    except (ValueError,KeyError,TypeError) as exc:
        return {'http_status':422,'body':{'status':'invalid_input','reason':str(exc)}}
    finally:db.close()

if __name__=='__main__':
    try:
        raw=sys.stdin.buffer.read(131073)
        if len(raw)>131072:raise ValueError('Request exceeds local service limit')
        result=handle(json.loads(raw))
    except Exception:
        # Do not emit traces, coordinates, inputs or database paths to the HTTP client.
        result={'http_status':503,'body':{'status':'error','reason':'The local evidence service could not initialise. Check the local database/data setup.','recoverable':True}}
    sys.stdout.write(dumps(result))
