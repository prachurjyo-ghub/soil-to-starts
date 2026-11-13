"""Canonical metric identities; unit conversion never supplies missing semantics."""
import math

METRICS={
 'rainfall_mm':{'metric_id':'precipitation','canonical_unit':'mm','nasa_parameter':'PRECTOTCORR','requires':'accumulation over explicitly matching days'},
 'temp_min_c':{'metric_id':'minimum_air_temperature','canonical_unit':'degC','nasa_parameter':'T2M_MIN','requires':'absolute minimum versus mean daily minima must be resolved'},
 'temp_max_c':{'metric_id':'maximum_air_temperature','canonical_unit':'degC','nasa_parameter':'T2M_MAX','requires':'absolute maximum versus mean daily maxima must be resolved'},
 'temp_mean_c':{'metric_id':'mean_air_temperature','canonical_unit':'degC','nasa_parameter':'T2M','requires':'matching averaging method and explicit days'},
 'humidity_mean_pct':{'metric_id':'relative_humidity','canonical_unit':'percent','nasa_parameter':None,'requires':'not present in current NASA archive'},
 'sunshine_hours':{'metric_id':'sunshine_duration','canonical_unit':'h','nasa_parameter':None,'requires':'do not substitute solar irradiance for sunshine hours'},
 'wind_speed_kmh':{'metric_id':'wind_speed','canonical_unit':'km/h','nasa_parameter':None,'requires':'not present in current NASA archive'}
}
UNIT_ALIASES={'°C':'degC','degC':'degC','mm':'mm','%':'percent','percent':'percent','hours':'h','h':'h','km/hour':'km/h','km/h':'km/h'}

def canonical_observation(field,value,unit,source_id,definition=None):
    if field not in METRICS:raise ValueError('Unknown metric identity')
    metric=METRICS[field]
    if UNIT_ALIASES.get(unit)!=metric['canonical_unit']:raise ValueError('Unit mismatch; no implicit rate/amount conversion')
    if value is not None and (not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value)):raise ValueError('Non-finite or non-numeric observation')
    return {'metric_id':metric['metric_id'],'value':value,'unit':metric['canonical_unit'],'nasa_parameter':metric['nasa_parameter'],'source_id':source_id,'definition':definition,'status':'observed_context' if value is not None else 'missing','usable_as_crop_threshold':False}

def comparison_readiness(left,right):
    missing=[]
    for key in ['metric_id','unit']:
        if left.get(key)!=right.get(key):missing.append('incompatible_'+key)
    for key in ['statistic','time_window','reference_period','spatial_method']:
        a=(left.get('definition') or {}).get(key);b=(right.get('definition') or {}).get(key)
        if not a or not b:missing.append('unresolved_'+key)
        elif a!=b:missing.append('incompatible_'+key)
    return {'comparable':not missing,'blocking_reasons':missing,'threshold_inferred':False}
