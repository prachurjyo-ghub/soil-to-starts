"""Build small local UI history from the checksum-pinned climate archive. No network."""
from pathlib import Path
import hashlib, json, tarfile, csv, io
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'data/climate/packages/v1.0.0/soil-to-stars-climate-bgd-v1.0.0.tar.gz'
OUTPUT = ROOT / 'prototype/public/data/climate-history.json'
RECEIPT = ROOT / 'data/climate/ui_climate_receipt.json'

def sha(data): return hashlib.sha256(data).hexdigest()
# Keep statistical calculations in the deterministic science boundary.
import sys
sys.path.insert(0, str(ROOT))
from src.compute.climate_history import aggregate, seasonal_profile

def build():
    expected = ARCHIVE.with_name(ARCHIVE.name+'.sha256').read_text().split()[0]
    actual = sha(ARCHIVE.read_bytes())
    if actual != expected: raise ValueError('Climate archive checksum mismatch')
    diagnostics_path=ROOT/'data/climate/regional_district_extraction_diagnostics.json'
    diagnostics=json.loads(diagnostics_path.read_text())
    registry={r['district_id']:r for r in csv.DictReader(io.StringIO((ROOT/'data/climate/district_sampling_registry.csv').read_text()))}
    out={'schema':'ui-climate-history.v1','source':'NASA POWER','collection_id':'nasa-power-daily-regional-bgd-v1','archive_sha256':actual,'mapping_sha256':sha(diagnostics_path.read_bytes()),'time_standard':'LST','period':'2001–2025','method':'Annual precipitation = sum of complete monthly totals; annual temperature = day-weighted monthly mean. Compare mean annual values of equal 10-year periods 2001–2010 and 2016–2025. Missing years prevent period comparison. Descriptive differences, not attribution, significance or forecasts.','limitations':'Representative grid-point context selected for a district anchor, not district/farm averages. Different districts may share a grid point. Crop suitability and live vulnerability are not computed.','source_url':'https://power.larc.nasa.gov/docs/services/api/temporal/daily/','districts':[],'grids':{}}
    with tarfile.open(ARCHIVE) as archive:
        members={m.name:m for m in archive.getmembers()}
        prefix='soil-to-stars-climate-bgd-v1.0.0/cache/nasa_power_regional/prepared-v1/'
        for d in diagnostics['districts']:
            lon,lat=d['diagnostic_output_longitude'],d['diagnostic_output_latitude']
            key=f'{float(lon)}-{float(lat)}'
            out['districts'].append({'id':d['district_id'],'en':d['district_name'],'bn':registry[d['district_id']]['district_name_bn'],'grid':key,'distance_km':round(d['distance_km'],2),'anchor_latitude':d['anchor_latitude'],'anchor_longitude':d['anchor_longitude']})
            if key in out['grids']: continue
            grid={'latitude':lat,'longitude':lon,'metrics':{}}
            for param in ['T2M','PRECTOTCORR']:
                path=prefix+f'chart-{key}-{param}.json'
                raw=archive.extractfile(members[path]).read();chart=json.loads(raw)
                if chart['parameter']!=param or chart['time_standard']!='LST': raise ValueError('Unexpected chart identity')
                grid['metrics'][param]={'unit':'°C' if param=='T2M' else 'mm/year','statistic':'annual mean 2m air temperature' if param=='T2M' else 'annual precipitation total','chart_path':path,'chart_sha256':sha(raw),'seasonal_profile':seasonal_profile(chart['series'],param),**aggregate(chart['series'],param)}
            out['grids'][key]=grid
    out['districts'].sort(key=lambda d:d['en'])
    return (json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
if __name__=='__main__':
    import sys
    data=build()
    receipt=(json.dumps({'schema':'ui-climate-receipt.v1','payload_sha256':sha(data),'source_archive_sha256':json.loads(data)['archive_sha256'],'build_script_sha256':sha(Path(__file__).read_bytes()),'compute_sha256':sha((ROOT/'src/compute/climate_history.py').read_bytes())},sort_keys=True,indent=2)+'\n').encode()
    if '--check' in sys.argv:
        if not OUTPUT.exists() or OUTPUT.read_bytes()!=data or not RECEIPT.exists() or RECEIPT.read_bytes()!=receipt: raise SystemExit('UI climate payload is stale; run python3 scripts/build_ui_climate.py')
        print('PASS: UI climate payload reproduces from pinned local archive')
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_bytes(data);RECEIPT.write_bytes(receipt);print(f'Wrote {OUTPUT.name}: {len(data)} bytes')
