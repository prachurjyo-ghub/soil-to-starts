"""Pure deterministic building blocks. Inactive evidence is never executable."""
from datetime import date, timedelta
import math

class RuleError(ValueError): pass

def executable(rule):
    return rule.get('activation_status')=='active' and rule.get('review',{}).get('status')=='accepted' and bool(rule.get('review',{}).get('reviewer')) and bool(rule.get('source_ids'))

def inclusive_indicator(values, expected_days, statistic):
    """Only explicit complete daily windows. Zero is a valid observation."""
    if len(values)!=expected_days or expected_days<1 or any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) for v in values):
        return {'status':'unknown','value':None,'reason':'incomplete_daily_window'}
    if statistic=='sum':value=sum(values)
    elif statistic=='mean':value=sum(values)/len(values)
    elif statistic=='maximum':value=max(values)
    elif statistic=='minimum':value=min(values)
    else:raise RuleError('Unsupported statistic; metric definitions must be explicit')
    return {'status':'complete','value':value,'days':expected_days}

def check_threshold(indicator,rule,unit):
    if not executable(rule):return {'outcome':'unknown','reason':'rule_not_active_and_reviewed'}
    if indicator.get('status')!='complete':return {'outcome':'unknown','reason':'missing_weather'}
    if rule.get('unit')!=unit:raise RuleError('Incompatible units')
    value=indicator['value'];minimum=rule.get('minimum');maximum=rule.get('maximum')
    if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value):return {'outcome':'unknown','reason':'invalid_indicator'}
    if any(v is not None and (not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v)) for v in [minimum,maximum]) or minimum is not None and maximum is not None and minimum>maximum:raise RuleError('Invalid threshold range')
    if minimum is None and maximum is None:raise RuleError('No threshold supplied')
    return {'outcome':'pass' if (minimum is None or value>=minimum) and (maximum is None or value<=maximum) else 'fail','value':value,'unit':unit,'rule_id':rule['rule_id'],'source_ids':rule['source_ids']}

def schedule_operations(available_from,rule):
    """Conservative max-duration schedule; requires reviewed event-specific durations."""
    if not executable(rule):raise RuleError('Cannot schedule an inactive rule')
    if rule.get('growth_origin')!='sowing' or rule.get('growth_endpoint')!='maturity':raise RuleError('Unresolved growth-duration events')
    durations=rule.get('durations',{})
    for key in ['preparation','growth','harvest','clearance']:
        item=durations.get(key,{})
        if item.get('unit')!='day' or not item.get('source_ids') or not all(isinstance(item.get(n),int) and not isinstance(item.get(n),bool) and item[n]>=0 for n in ['min','max']) or item['min']>item['max']:
            raise RuleError('Missing reviewed operation duration: '+key)
    if durations['growth']['min']<1:raise RuleError('Growth must be positive')
    cursor=date.fromisoformat(available_from);operations=[]
    # Boundaries are events, not overlapping occupied-day counts. Each duration is counted once.
    for key in ['preparation','growth','harvest','clearance']:
        end=cursor+timedelta(days=durations[key]['max'])
        operations.append({'type':key,'start':cursor.isoformat(),'end':end.isoformat(),'duration_days':durations[key]['max'],'source_ids':durations[key]['source_ids']})
        cursor=end
    return {'operations':operations,'field_clear_on':cursor.isoformat(),'duration_convention':'elapsed days between event boundaries; max of each reviewed range'}

def score_checks(checks,weights):
    """No missing-value imputation; no arbitrary default weights; never a probability."""
    if any(c.get('outcome') not in ['pass','fail','unknown'] for c in checks):raise RuleError('Unknown check outcome')
    if not checks or any(c.get('outcome')=='unknown' for c in checks):return {'status':'incomplete','score':None}
    if any(c.get('essential',True) and c.get('outcome')=='fail' for c in checks):return {'status':'infeasible','score':None}
    if set(weights)!={c['key'] for c in checks}:raise RuleError('Weights must name exactly the reviewed indicators')
    if any(not isinstance(w,(int,float)) or isinstance(w,bool) or not math.isfinite(w) or w<0 for w in weights.values()) or sum(weights.values())<=0:raise RuleError('Invalid weights')
    value=100*sum(weights[c['key']]*(1 if c['outcome']=='pass' else 0) for c in checks)/sum(weights.values())
    return {'status':'complete','score':round(value,4),'meaning':'weighted rule agreement, not probability, yield or field validation'}
