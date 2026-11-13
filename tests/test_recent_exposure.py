"""Contract tests: synthetic boundary cases only, isolated from product data."""
import json,sqlite3,tempfile,unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from src.api.storage import connect,seed,counts
from src.api.daily_index import schema
from src.api.recent_index import install_recent
from src.compute.exposure import assess_exposure
from src.compute.climate_history import seasonal_profile
from src.compute.weather import historical_window

class RecentWeatherQA(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.db=connect(Path(self.temp.name)/'qa.sqlite');seed(self.db);schema(self.db)
    def tearDown(self):self.db.close();self.temp.cleanup()
    def test_real_pack_integrity_and_fill_values(self):
        first=install_recent(self.db);self.assertEqual(first['rows'],13272);self.assertEqual(install_recent(self.db)['status'],'already_indexed')
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM weather_daily WHERE t2m=-999 OR precipitation_mm_day=-999").fetchone()[0],0)
        self.assertTrue(self.db.execute('SELECT COUNT(*) FROM weather_daily WHERE t2m IS NULL').fetchone()[0]>0)
        row=self.db.execute("SELECT grid_id FROM weather_daily WHERE date='2026-01-01' AND t2m IS NOT NULL LIMIT 1").fetchone()
        self.assertEqual(historical_window(self.db,row[0],'2026-01-01','2026-01-01','T2M')['status'],'complete')
    def test_catalogue_refresh_preserves_daily_rows_and_private_records(self):
        self.db.execute("INSERT INTO weather_daily VALUES('90.625-24.0','2026-01-01',20,10,30,0,'{}')");self.db.execute("INSERT INTO submissions VALUES('keep','now','hash','{}','field')");self.db.execute("UPDATE meta SET value='force-refresh' WHERE key='source_identity'");self.db.commit()
        seed(self.db);self.assertEqual(self.db.execute('SELECT COUNT(*) FROM weather_daily').fetchone()[0],1);self.assertEqual(self.db.execute("SELECT COUNT(*) FROM submissions WHERE id='keep'").fetchone()[0],1)
    def test_warning_boundaries_and_missing_values(self):
        district=json.loads(self.db.execute("SELECT payload FROM districts WHERE id='bd-district-dhaka'").fetchone()[0]);grid=district['grid'];region=district['membership']['region_id']
        self.db.executemany('INSERT INTO weather_daily VALUES(?,?,?,?,?,?,?)',[(grid,'2026-01-01',20,10,30,50,'{}'),(grid,'2026-01-02',20,None,31,51,'{}'),(grid,'2026-01-03',20,9,32,0,'{}')]);self.db.commit()
        intake={'current':{'state':'growing','crop_id':'mustard','sown_on':'2026-01-01'},'location':{'district_id':'bd-district-dhaka'},'availability':{'end':'2026-01-03'}}
        out=assess_exposure(self.db,intake,region,today=date(2026,1,4));self.assertEqual(out['status'],'incomplete');hot,cold,rain=out['indicators'];self.assertEqual(hot['exceedance_days'],2);self.assertIsNone(cold['exceedance_days']);self.assertEqual(cold['missing_days'],1);self.assertEqual(rain['exceedance_days'],1)
        intake['current']['crop_id']='rice';self.assertEqual(assess_exposure(self.db,intake,region)['status'],'unavailable')
    def test_foreign_region_never_substitutes_warning(self):
        intake={'current':{'state':'growing','crop_id':'mustard','sown_on':'2026-01-01'}}
        self.assertEqual(assess_exposure(self.db,intake,'other-region')['status'],'unavailable')
    def test_monthly_comparison_requires_ten_unique_complete_values(self):
        rows=[{'date':f'{year}-01','coverage':'complete','value':0,'valid_days':31,'expected_days':31} for year in range(2001,2011)]
        self.assertEqual(seasonal_profile(rows,'PRECTOTCORR')[0]['periods'][0]['mean'],0)
        rows[0]['value']=None;self.assertIsNone(seasonal_profile(rows,'PRECTOTCORR')[0]['periods'][0]['mean'])
