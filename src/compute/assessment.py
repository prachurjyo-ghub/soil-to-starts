"""Source-aware local evidence assessment. No invented agronomic thresholds."""
from datetime import date, datetime, timedelta, timezone
import json
from src.api.storage import metadata, counts
from src.compute.rule_engine import executable
from src.compute.metric_contract import METRICS, canonical_observation
from src.compute.weather import comparable_season, historical_window
from src.compute.exposure import assess_exposure
from src.compute.crop_options import calendar_options
from src.compute.rotation_replay import replay_trial

VERSION='evidence-assessment.v7'

def rows(db,sql,args=()):return [dict(r) for r in db.execute(sql,args)]
def payloads(db,sql,args=()):return [json.loads(r['payload']) for r in db.execute(sql,args)]

def climate_context(db,district):
    grid=json.loads(db.execute('SELECT payload FROM weather_grids WHERE id=?',(district['grid'],)).fetchone()[0])
    meta=metadata(db,'weather_metadata');series=[];stats=[]
    for parameter,key,label in [('T2M','temperature','Annual mean 2m air temperature'),('PRECTOTCORR','precipitation','Annual rainfall total')]:
        m=grid['metrics'][parameter]
        series.append({'key':key,'parameter':parameter,'label':label,'unit':m['unit'],'statistic':m['statistic'],'labels':[str(y['year']) for y in m['annual']],'values':[y['value'] for y in m['annual']],'chart_sha256':m['chart_sha256']})
        stats.append({'metric':parameter,'window':'2001–2010 versus 2016–2025','earlier_mean':m['periods'][0]['mean'],'recent_mean':m['periods'][1]['mean'],'difference':m['difference'],'unit':m['unit'],'valid_years':[p['valid_years'] for p in m['periods']]})
    return {'status':'complete','period':{'start':'2001-01-01','end':'2025-12-31'},'time_standard':meta['time_standard'],'missingness':'Missing years remain null; period differences require ten complete years in each window.','series':series,'comparison':{'earlier':'2001–2010','recent':'2016–2025','statistics':stats,'finding':'Descriptive historical differences only; no attribution, significance or future-weather claim.'},'spatial_support':{'kind':'district_anchor_representative_point','district_id':district['id'],'latitude':grid['latitude'],'longitude':grid['longitude'],'anchor_distance_km':district['distance_km'],'farm_pin_used_for_weather':False},'source_ids':['nasa-power-regional-2001-2025'],'limitations':[meta['limitations'],'The mapped grid represents district-anchor context even when a farm pin is supplied. Independent scientific review remains pending.']}

def crop_context(db,district,current):
    membership=district['membership'];region_id=membership['region_id']
    aliases = {row['crop_id']: row['intake_id'] for row in
               rows(db, 'SELECT intake_id,crop_id FROM crop_aliases WHERE crop_id IS NOT NULL')}
    grouped=[]
    for crop in rows(db,'SELECT id,label FROM crops ORDER BY label'):
        calendars=payloads(db,'SELECT payload FROM calendars WHERE crop_id=? AND region_id=? ORDER BY id',(crop['id'],region_id))
        grouped.append({'crop_id':crop['id'],'crop_label':crop['label'],'intake_crop_id':aliases.get(crop['id']),'region_id':region_id,'calendar_count':len(calendars),'calendar_ids':[c['calendar_id'] for c in calendars],
                        'calendars': [{'id': cal['calendar_id'], 'source_id': cal['source_id'],
                                       'source_page': cal['source_page'], 'season': cal['season_label'],
                                       'rice_system': cal.get('rice_system_label'),
                                       'life_span_days': [cal['duration_min_days'], cal['duration_max_days']]}
                                      for cal in calendars],'seasons':sorted({c['season_label'] for c in calendars}),'evidence_status':'collected_context_only' if calendars else 'not_collected_for_region','recommendation_status':'not_assessed'})
    alias=db.execute('SELECT crop_id FROM crop_aliases WHERE intake_id=?',(current.get('crop_id'),)).fetchone()
    calendars=payloads(db,'SELECT payload FROM calendars WHERE crop_id=? AND region_id=? ORDER BY id',(alias['crop_id'],region_id)) if alias and alias['crop_id'] else []
    samples=[]
    for cal in calendars:
        entry=db.execute('SELECT payload,weather_payload FROM calendar_entries WHERE calendar_id=? ORDER BY id LIMIT 1',(cal['calendar_id'],)).fetchone()
        samples.append({'calendar_id':cal['calendar_id'],'source_id':cal['source_id'],'source_page':cal['source_page'],'source_table_id':cal['source_table_id'],'season_label':cal['season_label'],'rice_system_label':cal.get('rice_system_label'),'variety':cal['variety'],'printed_life_span':{'min':cal['duration_min_days'],'max':cal['duration_max_days'],'unit':'day','origin':cal['duration_origin'],'endpoint':cal['duration_endpoint'],'status':'unresolved_events_not_a_clearance_duration'},'example_source_column':{'entry_id':json.loads(entry['payload'])['entry_id'],'growth_stage':json.loads(entry['payload'])['growth_stage'],'printed_week':json.loads(entry['payload'])['week_label_raw'],'printed_month':json.loads(entry['payload'])['month_label_raw'],'printed_weather_normals':json.loads(entry['weather_payload'])['values'],'normalized_weather_context':{key:canonical_observation(key,value,{'rainfall_mm':'mm','temp_min_c':'degC','temp_max_c':'degC','temp_mean_c':'degC','humidity_mean_pct':'%','sunshine_hours':'hours','wind_speed_kmh':'km/hour'}[key],cal['source_id']) for key,value in json.loads(entry['weather_payload'])['values'].items()},'usable_as_crop_threshold':False} if entry else None})
    return {'region_id':region_id,'region_label':membership['bamis_region'],'mapping_basis':membership['source_basis'],'mapping_status':membership['mapping_status'],'scientific_applicability':'candidate source-region membership; not an agronomic approval','current_crop_calendars':samples,'regional_catalogue':grouped}

def check(key,en,bn,missing,source_ids=()):
    return {'check_id':key,'outcome':'unknown','label':{'en':en,'bn':bn},'missing_information':missing,'rule_id':None,'source_ids':list(source_ids)}

def assess(db,intake,source_identity):
    selected=db.execute('SELECT payload FROM districts WHERE id=?',(intake['location']['district_id'],)).fetchone()
    district=json.loads(selected[0]);district['id']=intake['location']['district_id']
    crop=crop_context(db,district,intake['current']);climate=climate_context(db,district)
    labels={row['intake_id']:json.loads(row['payload'])['label'] for row in db.execute('SELECT intake_id,payload FROM crop_aliases')}
    sowing = intake['current'].get('sown_on')
    latest = None
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='weather_daily'").fetchone():
        latest = db.execute(
            'SELECT MAX(date) FROM weather_daily WHERE grid_id=? AND t2m IS NOT NULL AND t2m_min IS NOT NULL AND t2m_max IS NOT NULL AND precipitation_mm_day IS NOT NULL',
            (district['grid'],),
        ).fetchone()[0]
    occupancy = {'status': 'unavailable', 'latest_observed': latest, 'start': sowing}
    if sowing and latest:
        end = min(intake['availability']['end'], latest, (date.today() - timedelta(days=1)).isoformat())
        if sowing <= end:
            occupancy = {
                'status': 'available',
                'start': sowing,
                'end': end,
                'latest_observed': latest,
                'metrics': {
                    parameter: historical_window(db, district['grid'], sowing, end, parameter)
                    for parameter in ['T2M', 'T2M_MIN', 'T2M_MAX', 'PRECTOTCORR']
                },
            }
    climate['reported_occupancy_window'] = occupancy
    climate['field_ready_season'] = comparable_season(
        db, district['grid'], intake['availability']['start'], intake['availability']['end'])
    climate['crop_season_reference'] = (
        comparable_season(db, district['grid'], sowing, intake['availability']['end'])
        if sowing and occupancy['status'] != 'available' else None
    )
    if occupancy['status'] == 'available':
        climate['crop_observed_reference'] = comparable_season(
            db, district['grid'], occupancy['start'], occupancy['end'])
    options = calendar_options(db, crop, intake, labels)
    exposure=assess_exposure(db,intake,crop['region_id'])
    source_ids=sorted({c['source_id'] for c in crop['current_crop_calendars']})
    checks=[check('heat-rule','Heat compatibility not scored','তাপমাত্রার উপযোগিতা স্কোর করা হয়নি','Reviewed crop/variety/stage temperature range and its matching daily statistic/window.',source_ids),check('water-rule','Water compatibility not scored','পানির উপযোগিতা স্কোর করা হয়নি','Reviewed stage-specific crop water requirement and irrigation treatment; printed calendar rainfall is not a tolerance.',source_ids),check('operations','Crop timing is not yet executable','ফসলের সময় এখনো গণনাযোগ্য নয়','Source-backed preparation, growth-event, harvest/collection and clearance durations plus a planting-window definition.',source_ids),check('rotation','Rotation compatibility not scored','ফসল আবর্তনের উপযোগিতা স্কোর করা হয়নি','Reviewed crop-family/sequence restrictions and applicable varieties; history alone cannot quantify nutrients.'),check('normal-definition','BAMIS and NASA statistics cannot be silently equated','বামিস ও নাসার পরিসংখ্যান সরাসরি এক করা যাবে না','BAMIS printed week/day mapping, normal statistic, reference period and spatial definition before numerical normal-to-normal comparison.',source_ids)]
    if intake['current']['crop_id']=='rice':checks.append(check('rice-system','Rice production system is unspecified','ধানের উৎপাদন পদ্ধতি নির্ধারিত নয়','Aman, Boro or Aus and the applicable variety/stage; do not infer them from generic rice or district.'))
    if intake['current']['state']=='growing' and not intake['current'].get('sown_on'):checks.append(check('current-stage','Current crop stage is unresolved','বর্তমান ফসলের পর্যায় অজানা','Known sowing/transplanting event and date with a reviewed stage convention.'))
    baseline=intake['baseline'];segments=[]
    for part in baseline['segments']:
        period=part['period'];period_label=(period['start']+' → '+period['end']) if period['kind']=='dates' else f"{period['season_id']} · {period['year']} (reported season, not planting dates)"
        segment = {'kind':part['kind'], 'crop_id':part['crop_id'],
                   'label':labels.get(part['crop_id'],{'en':'Fallow','bn':'পতিত'}), 'period':period_label}
        if period['kind'] == 'dates':
            historical = comparable_season(db, district['grid'], period['start'], period['end'])
            segment['historical_weather'] = {key:value for key,value in historical.items() if key != 'samples'}
        segments.append(segment)
    source_meta=metadata(db,'weather_metadata')
    sources=[{'source_id':'nasa-power-regional-2001-2025','provider':'NASA POWER','product_version':source_meta['collection_id'],'url':source_meta['source_url'],'period':'2001–2025 · LST','spatial_support':f"Representative point {climate['spatial_support']['latitude']}, {climate['spatial_support']['longitude']}; {district['distance_km']} km from district anchor; not a district/farm average",'qa':'Archive and chart identities preserved; no independent scientific acceptance inferred','archive_sha256':source_meta['archive_sha256']}]
    recent=metadata(db,'recent_weather_receipt')
    if recent:sources.append({'source_id':'nasa-power-recent-2026','provider':'NASA POWER','product_version':'POWER Daily API '+recent['sources']['T2M']['api']['version'],'url':recent['sources']['T2M']['url'],'period':recent['start']+' to '+recent['end']+' · LST; latest complete '+recent['last_complete_date'],'spatial_support':'Same district-anchor grids, not field measurements','qa':'Checksum-verified offline observations; nulls preserved','sha256':recent['payload_sha256']})
    for sid in source_ids:
        src=json.loads(db.execute('SELECT payload FROM sources WHERE id=?',(sid,)).fetchone()[0])
        sources.append({'source_id':sid,'provider':'BAMIS · preserved source calendar','product_version':sid,'url':src.get('source_url') or next(iter(src.get('source_urls_from_existing_catalog',[])),'https://www.bamis.gov.bd/'),'period':'Printed calendar; reference climate period unresolved','spatial_support':crop['region_label']+' · source calendar region','qa':'Extracted evidence; inactive as a crop rule','sha256':src['sha256']})
    total=counts(db);active=[r for r in payloads(db,'SELECT payload FROM rules') if executable(r)]
    definitions=metadata(db,'weather_definitions')
    return {'status':'incomplete','report_status':'complete','comparison_status':'incomplete','data_mode':'local_evidence','analysis_mode':'source_evidence_report','reason':'Local inputs and evidence are connected. Complete crop plans are blocked by unresolved crop-rule and operation definitions.','coverage':{'label':'Historical NASA weather and regional crop records','district_id':district['id'],'scientific_region_id':crop['region_id'],'validated_farm_advice':False},'comparison_period':{'start':None,'end':None,'explanation':'Not selected: a reviewed planting/operation policy is required before three-crop scheduling.','policy_id':None},'baseline_assessment':{'plan_id':'reported-baseline','role':'baseline','state':baseline['state'],'label':({'en':'No established rotation reported','bn':'নির্ধারিত ফসল আবর্তন জানানো হয়নি'} if baseline['state']=='no_established_rotation' else {'en':'Your reported usual practice','bn':'আপনার জানানো সাধারণ চাষপদ্ধতি'}),'status':'incomplete','feasibility':'unknown','completion_date':None,'segments':segments,'indicators':[],'unallocated_intervals':[],'reason_ids':[c['check_id'] for c in checks]},'alternatives':[],'calendar_options':options,'current_crop_assessment':{'status':'incomplete' if intake['current']['state']=='growing' else 'not_applicable','crop_label':labels.get(intake['current'].get('crop_id'),{'en':'Fallow','bn':'পতিত'}),'stage':None,'observed_warning_exposure':exposure,'assessment_period':({'start':exposure['start'],'end':exposure['end']} if exposure['status'] in ('complete','incomplete') else None),'checks':checks[:2] if intake['current']['state']=='growing' else [],'limitation':'Historical weather context is provided, not live crop diagnosis or a future forecast. Crop tolerance checks remain unknown.'},'climate':climate,'checks':checks,'sources':sources,'versions':{'contract':'local-assessment.v1','catalogue':source_identity,'method':VERSION},'evidence_profile':{'storage':'local SQLite','source_identity':source_identity,'counts':{k:v for k,v in total.items() if k not in ['submissions','results']},'active_reviewed_rules':len(active),'input_usage':[{'field':'location.district_id','usage':'Joins regional crop calendars and representative NASA grid.'},{'field':'location.coordinates','usage':'Preserved pin and district validation only; not a field-specific NASA measurement.'},{'field':'current.crop_id','usage':'Selects source calendars and an explicitly applicable warning reference, if available.'},{'field':'current.sown_on','usage':'Reported occupancy and observed-weather warning window; no growth stage inferred.'},{'field':'availability','usage':'Preserved for future scheduling; caps reported observed-weather window.'},{'field':'crop_history','usage':'Preserved, not scored: reviewed sequence/family rules absent.'},{'field':'baseline','usage':'Displayed as farmer-reported usual practice, not numerically assessed.'},{'field':'irrigation','usage':'Preserved, not scored: stage water and irrigation treatment absent.'},{'field':'priority','usage':'Preserved, not scored: no validated ranking weights or complete plans.'}],'crop_context':crop,'metric_bridge':[{'bamis_field':d['field'],'metric_id':METRICS[d['field']]['metric_id'],'canonical_unit':METRICS[d['field']]['canonical_unit'],'nasa_parameter':d['counterpart'],'crop_threshold':False,'evaluable_now':d['evaluable_now'],'missing_information':d['missing_information']} for d in definitions],'model':{'kind':'deterministic_evidence_pipeline','trained':False,'regression_readiness':'The imported crop/weather packages contain no labelled field outcomes or calibrated target suitability scores. Weather normals and priorities are not outcome labels.','tuning':'Not performed: no justified supervised crop target or independent outcome test set.'}},'intended_crop_assessment':{'status':'unavailable','reason':'The same reviewed crop rules are required for intended-crop evaluation; none are activated for scientific planning.'},'historical_replay':replay_trial(db,district['id'],district['grid']),'limitations':['No numerical crop suitability, probability, yield, profit or nutrient-restoration score was calculated.','BAMIS weather normals retain their original meaning. They are not activated as crop thresholds.','The farmer input, crop calendar and NASA grid are joined by explicit district/region/crop identities; this does not establish scientific field applicability.']}
