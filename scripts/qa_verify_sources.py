"""Optional live publisher verification of a small predeclared weather sample and one crop PDF."""
from pathlib import Path
import hashlib,json,sys,time,urllib.request,urllib.parse
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.api.storage import connect,seed,dumps
DATES=['20010101','20200615','20251231']
PARAMETERS={'T2M':'t2m','PRECTOTCORR':'precipitation_mm_day'}
def fetch(url,destination):
    req=urllib.request.Request(url,headers={'User-Agent':'Soil-to-Stars-source-QA/1.0'})
    with urllib.request.urlopen(req,timeout=35) as response:
        data=response.read();status=response.status
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    return data,status

def main():
    if '--live' not in sys.argv:raise SystemExit('Use --live for explicitly requested public publisher checks; never called by the app.')
    db=connect();seed(db);out={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'method':'predeclared dates; original regional bbox; exact mapped coordinates; raw daily values; tolerance 0.001','sample_scope':'publisher consistency sample only, not station/field validation','checks':[]}
    for day in DATES:
        for parameter,column in PARAMETERS.items():
            params={'parameters':parameter,'community':'AG','latitude-min':'20.090609','latitude-max':'27.134513','longitude-min':'87.383628','longitude-max':'93.305257','start':day,'end':day,'format':'JSON','time-standard':'LST','units':'metric'}
            url='https://power.larc.nasa.gov/api/temporal/daily/regional?'+urllib.parse.urlencode(params)
            item={'provider':'NASA POWER','date':day,'parameter':parameter,'url':url}
            try:
                raw,status=fetch(url,ROOT/f'cache/qa/power-{parameter}-{day}.json');data=json.loads(raw);matched=0;differences=[];seen=0
                for feature in data.get('features',[]):
                    lon,lat=feature['geometry']['coordinates'][:2];grid=f'{float(lon)}-{float(lat)}'
                    row=db.execute('SELECT '+column+' FROM weather_daily WHERE grid_id=? AND date=?',(grid,day[:4]+'-'+day[4:6]+'-'+day[6:])).fetchone()
                    if row is None:continue
                    seen+=1;value=feature['properties']['parameter'][parameter].get(day)
                    if value is not None and row[0] is not None and abs(value-row[0])<=0.001:matched+=1
                    else:differences.append({'grid_id':grid,'archived':row[0],'publisher':value})
                item.update({'http_status':status,'response_sha256':hashlib.sha256(raw).hexdigest(),'points_compared':seen,'matches':matched,'differences':differences,'publisher_api':data.get('header',{}).get('api'),'status':'passed' if seen==42 and matched==42 else 'needs_review'})
            except Exception as exc:item.update({'status':'unavailable','error':type(exc).__name__+': '+str(exc)})
            out['checks'].append(item);print(parameter,day,item['status'],flush=True)
    url='https://www.bamis.gov.bd/res/public/calendars/2019/12/30/10981.pdf';item={'provider':'BAMIS','source_id':'bamis_10981_5d1020fa','url':url}
    try:
        raw,status=fetch(url,ROOT/'cache/qa/mustard-dhaka.pdf');actual=hashlib.sha256(raw).hexdigest();expected='3bec21011db94f0154fa828e1fa4447ec97f373efd7186c3dc02ac51a7e08c7c';item.update({'http_status':status,'sha256':actual,'archive_source_sha256':expected,'status':'passed' if actual==expected else 'needs_review'})
    except Exception as exc:item.update({'status':'unavailable','error':type(exc).__name__+': '+str(exc)})
    out['checks'].append(item);db.close();p=ROOT/'data/qa/publisher_verification.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Saved publisher verification receipt',flush=True)
if __name__=='__main__':main()
