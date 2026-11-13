"""Explicit real-evidence join audit; synthetic requests, never farmer recommendations."""
from pathlib import Path
import json,sys,socket
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.api.storage import ROOT,connect,seed,dumps
from src.compute.assessment import assess

def main():
    db=connect();identity=seed(db);counts=Counter();examples=[]
    # Scientific service must never acquire remotely during a request.
    def forbidden(*args,**kwargs):raise AssertionError('Network attempted by offline assessment')
    socket.create_connection=forbidden
    districts=[r[0] for r in db.execute('SELECT id FROM districts ORDER BY id')];crops=[r[0] for r in db.execute('SELECT intake_id FROM crop_aliases ORDER BY intake_id')]
    for district in districts:
        for crop in crops:
            request={'schema_version':'farmer-intake.v2','location':{'district_id':district},'current':{'state':'growing','crop_id':crop,'sown_on':'2026-11-01'},'availability':{'end':'2027-02-10'},'baseline':{'state':'no_established_rotation','segments':[]}}
            result=assess(db,request,identity);context=result['evidence_profile']['crop_context'];counts['requests']+=1
            assert result['coverage']['district_id']==district
            assert result['climate']['spatial_support']['district_id']==district
            assert result['alternatives']==[] and result['comparison_period']['start'] is None
            assert result['evidence_profile']['active_reviewed_rules']==0
            assert all(c['region_id']==context['region_id'] for c in context['regional_catalogue'])
            counts['with_matching_calendar' if context['current_crop_calendars'] else 'without_matching_calendar']+=1
            exposure=result['current_crop_assessment']['observed_warning_exposure'];counts['warning_'+exposure['status']]+=1
            if exposure['status']!='unavailable':examples.append({'district':district,'crop':crop,'period':[exposure['start'],exposure['end']],'counts':[{'id':i['id'],'days':i['exceedance_days'],'valid_days':i['valid_days']} for i in exposure['indicators']]})
    report={'schema':'qa-coverage-matrix.v1','status':'passed','source_identity':identity,'districts':len(districts),'crop_labels':len(crops),'counts':dict(counts),'source_warning_examples':examples,'scope':'Synthetic QA intake dates against actual local evidence. Identity, missingness and offline checks only, not agronomic accuracy validation.'}
    (ROOT/'data/qa/coverage_matrix.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));db.close()
if __name__=='__main__':main()
