import importlib.util,unittest,calendar
from pathlib import Path
spec=importlib.util.spec_from_file_location('ui_climate',Path(__file__).resolve().parents[1]/'scripts/build_ui_climate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ClimateUIAggregation(unittest.TestCase):
    def rows(self):
        return [dict(date=f'{year}-{month:02}',coverage='complete',value=0 if month==1 else 10,valid_days=calendar.monthrange(year,month)[1],expected_days=calendar.monthrange(year,month)[1]) for year in range(2001,2026) for month in range(1,13)]
    def test_precipitation_zero_and_sum(self):
        out=m.aggregate(self.rows(),'PRECTOTCORR');self.assertEqual(out['annual'][0]['value'],110);self.assertEqual(out['difference'],0)
    def test_temperature_day_weighting(self):
        self.assertEqual(m.aggregate(self.rows(),'T2M')['annual'][0]['value'],round(10*(365-31)/365,4))
    def test_missing_year_prevents_comparison(self):
        rows=self.rows();rows[0]['value']=None;out=m.aggregate(rows,'T2M');self.assertIsNone(out['annual'][0]['value']);self.assertIsNone(out['difference']);self.assertEqual(out['periods'][0]['valid_years'],9)
    def test_duplicate_month_not_complete(self):
        rows=self.rows();rows[0]['date']='2001-02';self.assertIsNone(m.aggregate(rows,'T2M')['annual'][0]['value'])
