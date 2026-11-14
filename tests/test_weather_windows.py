import sqlite3,unittest
from src.api.daily_index import schema,records_to_sql
from src.compute.weather import comparable_season, historical_window
class WeatherWindowTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.execute('CREATE TABLE weather_grids(id TEXT PRIMARY KEY)');self.db.execute("INSERT INTO weather_grids VALUES('90.625-24.0')");schema(self.db)
    def tearDown(self):self.db.close()
    def record(self,day='2001-01-01',rain=0):return {'date':day,'output_longitude':90.625,'output_latitude':24.0,'time_standard':'LST','units':{'T2M':'C','T2M_MIN':'C','T2M_MAX':'C','PRECTOTCORR':'mm/day'},'values':{'T2M':20,'T2M_MIN':10,'T2M_MAX':30,'PRECTOTCORR':rain},'missing_reasons':{}}
    def insert(self,record):self.db.execute('INSERT INTO weather_daily VALUES(?,?,?,?,?,?,?)',records_to_sql(record,{'90.625-24.0'}))
    def test_zero_precipitation_is_not_missing(self):
        self.insert(self.record());r=historical_window(self.db,'90.625-24.0','2001-01-01','2001-01-01','PRECTOTCORR');self.assertEqual(r['value'],0);self.assertEqual(r['unit'],'mm');self.assertFalse(r['threshold_inferred'])
    def test_daily_temperature_and_amount_have_different_statistics(self):
        self.insert(self.record());self.insert(self.record('2001-01-02',5));self.assertEqual(historical_window(self.db,'90.625-24.0','2001-01-01','2001-01-02','T2M')['statistic'],'mean');self.assertEqual(historical_window(self.db,'90.625-24.0','2001-01-01','2001-01-02','PRECTOTCORR')['value'],5)
    def test_missing_day_is_unknown_not_a_partial_sum(self):
        self.insert(self.record());r=historical_window(self.db,'90.625-24.0','2001-01-01','2001-01-02','PRECTOTCORR');self.assertEqual(r['status'],'unknown');self.assertIsNone(r['value'])
    def test_future_dates_never_get_synthetic_weather(self):
        r=historical_window(self.db,'90.625-24.0','2027-01-01','2027-01-10','T2M');self.assertEqual(r['status'],'unavailable');self.assertIn('no forecast',r['reason'])
    def test_foreign_grid_and_malformed_units_are_rejected(self):
        r=self.record();self.assertIsNone(records_to_sql(r,{'different-grid'}));r['units']['PRECTOTCORR']='mm'
        with self.assertRaises(ValueError):records_to_sql(r,{'90.625-24.0'})
    def test_extreme_source_values_are_not_clipped(self):
        r=self.record(rain=500);r['values']['T2M_MIN']=-2;self.insert(r);self.assertEqual(historical_window(self.db,'90.625-24.0','2001-01-01','2001-01-01','T2M_MIN')['value'],-2)

    def test_future_dates_resolve_to_exact_past_windows_and_keep_zero(self):
        for day, rain in [('2001-11-20', 0), ('2001-11-21', 0),
                          ('2002-11-20', 6), ('2002-11-21', 10), ('2003-11-20', 80)]:
            self.insert(self.record(day, rain))
        result = comparable_season(self.db, '90.625-24.0', '2027-11-20', '2027-11-21')
        self.assertEqual(result['years_used'], 2)
        self.assertEqual(result['median']['rain_mm'], 8)
        self.assertEqual([sample['rain_mm'] for sample in result['samples']], [0, 16])

    def test_same_dates_can_cross_years_or_select_leap_years(self):
        for day in ['2001-12-31', '2002-01-01', '2004-02-29']:
            self.insert(self.record(day))
        winter = comparable_season(self.db, '90.625-24.0', '2027-12-31', '2028-01-01')
        self.assertEqual([sample['end'] for sample in winter['samples']], ['2002-01-01'])
        leap = comparable_season(self.db, '90.625-24.0', '2028-02-29', '2028-02-29')
        self.assertEqual([sample['year'] for sample in leap['samples']], [2004])
