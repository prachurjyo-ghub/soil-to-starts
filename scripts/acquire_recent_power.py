"""Explicit pre-cache job for a bounded recent POWER period. Never called by the website."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import gzip,hashlib,io,json,math,sys,urllib.parse,urllib.request
ROOT=Path(__file__).resolve().parents[1]
PARAMS=['T2M','T2M_MIN','T2M_MAX','PRECTOTCORR']

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--start',required=True);parser.add_argument('--end',required=True);args=parser.parse_args()
    start=datetime.strptime(args.start,'%Y%m%d').date();end=datetime.strptime(args.end,'%Y%m%d').date()
    if start>end or start.year!=end.year or start.year<=2025:raise SystemExit('Use one explicit recent year after the sealed archive')
    weather=json.loads((ROOT/'prototype/public/data/climate-history.json').read_text());wanted=set(weather['grids'])
    def download(parameter):
        query={'parameters':parameter,'community':'AG','latitude-min':'20.090609','latitude-max':'27.134513','longitude-min':'87.383628','longitude-max':'93.305257','start':args.start,'end':args.end,'format':'JSON','time-standard':'LST','units':'metric'}
        url='https://power.larc.nasa.gov/api/temporal/daily/regional?'+urllib.parse.urlencode(query)
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Soil-to-Stars-precache/1.0'}),timeout=90) as response:raw=response.read();status=response.status
        path=ROOT/f'cache/qa/recent-{parameter}-{args.start}-{args.end}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);data=json.loads(raw)
        if data['header']['time_standard']!='LST':raise ValueError('Unexpected time standard')
        series={}
        for feature in data['features']:
            lon,lat=feature['geometry']['coordinates'][:2];key=f'{float(lon)}-{float(lat)}'
            if key in wanted:series[key]=feature['properties']['parameter'][parameter]
        if set(series)!=wanted:raise ValueError('Recent regional grid differs from pinned representative points')
        print('Downloaded',parameter,len(raw),'bytes',flush=True)
        return parameter,data,series,{'url':url,'http_status':status,'raw_sha256':hashlib.sha256(raw).hexdigest(),'api':data['header']['api'],'sources':data['header'].get('sources',[]),'unit':data['parameters'][parameter]['units']}
    results=list(ThreadPoolExecutor(max_workers=2).map(download,PARAMS));indexed={p:(data,series,meta) for p,data,series,meta in results}
    dates=sorted(next(iter(indexed['T2M'][1].values())))
    expected=(end-start).days+1
    if len(dates)!=expected:raise ValueError('Recent date coverage mismatch')
    rows=[];latest=[]
    for grid in sorted(wanted):
        usable=[]
        for day in dates:
            values={};missing={}
            for p in PARAMS:
                data,series,meta=indexed[p]
                if meta['unit']!=('mm/day' if p=='PRECTOTCORR' else 'C'):raise ValueError('Unexpected source unit')
                value=series[grid].get(day)
                if value==data['header']['fill_value'] or value is None:values[p]=None;missing[p]='source_fill'
                elif not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('Non-finite observation')
                else:values[p]=value
            if all(v is not None for v in values.values()):
                if not values['T2M_MIN']<=values['T2M']<=values['T2M_MAX']:raise ValueError('Temperature-order source check failed')
                usable.append(day)
            rows.append({'grid_id':grid,'date':day[:4]+'-'+day[4:6]+'-'+day[6:],'values':values,'missing_reasons':missing})
        if not usable:raise ValueError('No complete recent observations at a mapped point')
        latest.append(max(usable))
    output=ROOT/'data/climate/recent';output.mkdir(parents=True,exist_ok=True)
    target=output/'power-recent.jsonl.gz';buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode='wb',mtime=0,filename='') as stream:
        for row in rows:stream.write((json.dumps(row,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
    raw=buffer.getvalue();target.write_bytes(raw);last=min(latest)
    receipt={'schema':'recent-power.v1','start':start.isoformat(),'end':end.isoformat(),'last_complete_date':last[:4]+'-'+last[4:6]+'-'+last[6:],'time_standard':'LST','grid_ids':sorted(wanted),'rows':len(rows),'payload_sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'sources':{p:meta for p,data,series,meta in results},'limitations':['Recent POWER observations are regional meteorological context, not field sensors or forecasts. Source fill values remain missing.']}
    (output/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print('Prepared',len(rows),'real recent rows;',len(raw),'compressed bytes; complete through',receipt['last_complete_date'],flush=True)
if __name__=='__main__':main()
