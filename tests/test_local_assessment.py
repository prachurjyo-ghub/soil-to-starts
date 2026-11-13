import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from src.api.local_service import handle
from src.api.storage import connect,seed,counts
from src.compute.rule_engine import inclusive_indicator,check_threshold,schedule_operations,score_checks,RuleError
from src.compute.metric_contract import canonical_observation,comparison_readiness

# Test-only farmer answers and synthetic executable-rule examples; never runtime agronomy.
def intake():
    return {'schema_version':'farmer-intake.v2','location':{'country_code':'BD','district_id':'bd-district-dhaka','selection_method':'district_search','level':'district','coordinates':None},'current':{'state':'growing','crop_id':'rice','sown_on':None},'availability':{'kind':'date','start':'2027-01-01','end':'2027-01-01','basis':'expected','applies_to':'after_harvest'},'crop_history':{'state':'first_cultivation','entries':[]},'baseline':{'state':'no_established_rotation','segments':[]},'irrigation':{'access':'rainfed','seasonal_limitations':'not_applicable','limited_seasons':[]},'priority':'balanced','planning':{'status':'unavailable','reason':'scientific_api_not_connected','comparison_status':'unavailable'}}

def test_rule():
    return {'rule_id':'test-only-rule','activation_status':'active','review':{'status':'accepted','reviewer':'TEST FIXTURE ONLY'},'source_ids':['test-only-source'],'unit':'degC','minimum':10,'maximum':30,'growth_origin':'sowing','growth_endpoint':'maturity','durations':{key:{'min':days,'max':days,'unit':'day','source_ids':['test-only-source']} for key,days in [('preparation',3),('growth',60),('harvest',4),('clearance',2)]}}

class LocalAssessment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.path=Path(cls.temp.name)/'local.sqlite3'
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def run_service(self,operation,**kwargs):return handle({'operation':operation,**kwargs},self.path)
    def test_health_imports_preserved_rows_without_activating_rules(self):
        result=self.run_service('health')['body'];self.assertEqual(result['counts']['districts'],64);self.assertEqual(result['counts']['calendar_entries'],7834);self.assertEqual(result['counts']['calendars'],366);self.assertEqual(result['counts']['rules'],0)
    def test_report_joins_district_region_crop_and_weather(self):
        result=self.run_service('plan',intake=intake());self.assertEqual(result['http_status'],200);r=result['body'];self.assertEqual(r['status'],'incomplete');self.assertEqual(r['report_status'],'complete');self.assertEqual(r['data_mode'],'local_evidence');self.assertEqual(r['evidence_profile']['crop_context']['region_label'],'Dhaka');self.assertEqual(r['climate']['status'],'complete');self.assertTrue(r['evidence_profile']['crop_context']['current_crop_calendars']);self.assertEqual(r['alternatives'],[]);self.assertTrue(all(c['outcome']=='unknown' for c in r['checks']));self.assertIsNone(r['comparison_period']['start']);self.assertEqual(r['evidence_profile']['active_reviewed_rules'],0)
    def test_records_restore_identical_private_input_and_report(self):
        request=intake();r=self.run_service('plan',intake=request)['body'];restored=self.run_service('result',id=r['result_id'])['body'];self.assertEqual(restored['intake'],request);self.assertEqual(restored['result'],r);self.assertEqual(self.run_service('submission',id=r['submission_id'])['body']['result'],r)
    def test_same_input_and_sources_have_stable_fingerprint_with_distinct_delivery_ids(self):
        a=self.run_service('plan',intake=intake())['body'];b=self.run_service('plan',intake=intake())['body'];self.assertNotEqual(a['result_id'],b['result_id']);self.assertEqual(a['input_fingerprint'],b['input_fingerprint']);self.assertEqual(a['result_fingerprint'],b['result_fingerprint'])
    def test_changed_inputs_change_result_identity(self):
        a=self.run_service('plan',intake=intake())['body'];other=intake();other['priority']='water';b=self.run_service('plan',intake=other)['body'];self.assertNotEqual(a['input_fingerprint'],b['input_fingerprint']);self.assertNotEqual(a['result_fingerprint'],b['result_fingerprint'])
    def test_no_listing_or_unsafe_id_lookup(self):
        self.assertEqual(self.run_service('result',id="' OR 1=1 --")['http_status'],404);self.assertEqual(self.run_service('result',id='00000000-0000-0000-0000-000000000000')['http_status'],404)
    def test_invalid_input_is_not_persisted(self):
        before=self.run_service('health')['body']['counts']['submissions'];bad=intake();bad['location']['district_id']='not-real';self.assertEqual(self.run_service('plan',intake=bad)['http_status'],422);self.assertEqual(self.run_service('health')['body']['counts']['submissions'],before)
    def test_import_is_idempotent_and_preserves_saved_results(self):
        report=self.run_service('plan',intake=intake())['body'];db=connect(self.path)
        try:a=seed(db);before=counts(db);self.assertEqual(seed(db),a);self.assertEqual(counts(db),before)
        finally:db.close()
        self.assertEqual(self.run_service('result',id=report['result_id'])['http_status'],200)
    def test_missing_crop_evidence_does_not_substitute_another_crop(self):
        request=intake();request['current']['crop_id']='sesame';r=self.run_service('plan',intake=request)['body'];self.assertEqual(r['evidence_profile']['crop_context']['current_crop_calendars'],[]);self.assertEqual(r['current_crop_assessment']['crop_label']['en'],'Sesame');self.assertEqual(r['alternatives'],[])
    def test_regional_calendar_duplicates_keep_source_identities(self):
        request=intake();r=self.run_service('plan',intake=request)['body'];calendars=r['evidence_profile']['crop_context']['current_crop_calendars'];self.assertEqual(len({c['calendar_id'] for c in calendars}),len(calendars));self.assertTrue(all(c['printed_life_span']['origin'] is None for c in calendars));self.assertTrue(all(not c['example_source_column']['usable_as_crop_threshold'] for c in calendars))
    def test_database_is_not_world_readable(self):
        self.run_service('health');self.assertEqual(self.path.stat().st_mode&0o777,0o600)

class CalculationBoundaries(unittest.TestCase):
    def test_missing_daily_values_do_not_become_zero(self):
        self.assertEqual(inclusive_indicator([0,0],2,'sum')['value'],0);self.assertEqual(inclusive_indicator([0,None],2,'sum')['status'],'unknown');self.assertEqual(inclusive_indicator([True,2],2,'sum')['status'],'unknown')
    def test_threshold_requires_review_and_metric_units(self):
        rule=test_rule();self.assertEqual(check_threshold({'status':'complete','value':10},rule,'degC')['outcome'],'pass');rule['activation_status']='inactive';self.assertEqual(check_threshold({'status':'complete','value':40},rule,'degC')['outcome'],'unknown');rule=test_rule()
        with self.assertRaises(RuleError):check_threshold({'status':'complete','value':10},rule,'mm')
    def test_operation_events_are_counted_once(self):
        result=schedule_operations('2027-01-01',test_rule());self.assertEqual(result['field_clear_on'],'2027-03-11');self.assertEqual(sum(o['duration_days'] for o in result['operations']),69)
    def test_undefined_duration_or_event_blocks_scheduling(self):
        rule=test_rule();rule['growth_endpoint']='unknown'
        with self.assertRaises(RuleError):schedule_operations('2027-01-01',rule)
        rule=test_rule();del rule['durations']['clearance']
        with self.assertRaises(RuleError):schedule_operations('2027-01-01',rule)
    def test_unknown_and_essential_failures_cannot_receive_a_score(self):
        self.assertIsNone(score_checks([{'key':'water','outcome':'unknown'}],{'water':1})['score']);self.assertEqual(score_checks([{'key':'water','outcome':'fail','essential':True}],{'water':1})['status'],'infeasible');self.assertEqual(score_checks([{'key':'water','outcome':'pass'}],{'water':1})['score'],100)
    def test_normalising_units_does_not_invent_a_definition_or_threshold(self):
        a=canonical_observation('temp_mean_c',0,'°C','test');self.assertEqual(a['value'],0);self.assertEqual(a['unit'],'degC');self.assertFalse(a['usable_as_crop_threshold']);self.assertFalse(comparison_readiness(a,a)['comparable'])
        with self.assertRaises(ValueError):canonical_observation('rainfall_mm',4,'mm/day','test')

class SQLNormalizationTests(unittest.TestCase):
    def test_numeric_observations_are_normalised_without_becoming_thresholds(self):
        with tempfile.TemporaryDirectory() as directory:
            db=connect(Path(directory)/'index.sqlite3')
            try:
                seed(db)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM crop_observations').fetchone()[0],54838)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM crop_observations WHERE usable_as_threshold<>0').fetchone()[0],0)
                self.assertTrue(db.execute('SELECT COUNT(*) FROM crop_observations WHERE value=0').fetchone()[0]>0)
                self.assertTrue(db.execute('SELECT COUNT(*) FROM crop_observations WHERE value IS NULL AND missing_reason IS NOT NULL').fetchone()[0]>0)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM weather_annual').fetchone()[0],2100)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM crop_aliases').fetchone()[0],30)
            finally:db.close()
