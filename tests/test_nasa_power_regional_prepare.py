"""Synthetic preparation regressions; no network or agronomic inference."""
import copy
import json
import sys
import unittest
import tempfile
import gzip
from unittest import mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/acquire'))
import prepare_nasa_power_regional as p
from tests.test_nasa_power_regional_acquire import synthetic_response


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.config = p.r.build_config()
        self.spec = p.r.build_request(self.config, 'test', self.config['boundary']['national_request_bbox'], ['PRECTOTCORR'], '20040201', '20040229')

    def rows(self, fill=False):
        return list(p.observations(synthetic_response(self.spec, self.config, fill_first=fill), self.spec, self.config, 'synthetic-sha'))

    def test_fill_is_null_and_partial_total_is_not_complete(self):
        rows = self.rows(True)
        self.assertIsNone(rows[0]['value'])
        self.assertEqual(rows[0]['missing_reason'], 'source_fill_value')
        partial = next(i for i in p.monthly(rows) if i['coverage'] == 'partial')
        self.assertIsNone(partial['value'])
        self.assertEqual(partial['valid_days'], 28)
        self.assertEqual(partial['expected_days'], 29)
        all_missing = [dict(row, value=None, missing_reason='source_fill_value') for row in rows]
        self.assertTrue(all(item['available_day_statistic'] is None for item in p.monthly(all_missing)))

    def test_complete_daily_rate_accumulation(self):
        summary = list(p.monthly(self.rows()))[0]
        self.assertEqual(summary['value'], sum(range(29)))
        self.assertEqual(summary['unit'], 'mm')

    def test_duplicate_and_conflict_rejected(self):
        rows = self.rows()
        for value in (rows[0]['value'], 900):
            duplicate = dict(rows[0], value=value)
            with self.assertRaises(ValueError):
                list(p.monthly(rows + [duplicate]))

    def test_invalid_numbers_rejected(self):
        for value in (True, float('nan'), float('inf'), '2', None):
            payload = json.loads(synthetic_response(self.spec, self.config))
            payload['features'][0]['properties']['parameter']['PRECTOTCORR']['20040201'] = value
            with self.assertRaises(p.r.ResponseValidationError):
                list(p.observations(json.dumps(payload).encode(), self.spec, self.config, 'synthetic'))

    def test_cross_year_and_leap_dates(self):
        self.spec['start'], self.spec['end'] = '20031231', '20040301'
        rows = self.rows()
        dates = {row['date'] for row in rows}
        self.assertIn('2003-12-31', dates)
        self.assertIn('2004-02-29', dates)
        self.assertIn('2004-03-01', dates)

    def test_wide_join_requires_identical_keys(self):
        rows = self.rows()
        parameters = {name: [dict(row, parameter=name) for row in rows] for name in p.r.PARAMETERS}
        self.assertEqual(len(p.join_wide(parameters)), len(rows))
        parameters['T2M'][0]['output_longitude'] += 0.01
        self.assertIsNone(p.join_wide(parameters))

    def test_duplicate_json_dates_rejected(self):
        raw = synthetic_response(self.spec, self.config).replace(b'"20040201":0.0', b'"20040201":0.0,"20040201":9.0')
        with self.assertRaises(p.r.ResponseValidationError):
            list(p.observations(raw, self.spec, self.config, 'synthetic'))

    def test_provisional_cross_year_selection_excludes_partial(self):
        rows = [dict(parameter='PRECTOTCORR', date=date, value=value, coverage='complete', expected_days=31)
                for date, value in [('2001-12', 2), ('2002-01', 3), ('2002-12', 8), ('2003-01', 9)]]
        result = p.select_periods(rows, 12, 2)
        self.assertEqual(result['usable_periods'], 2)
        self.assertEqual(result['minimum']['value'], 5)
        rows[-1]['coverage'] = 'partial'
        self.assertEqual(p.select_periods(rows, 12, 2)['usable_periods'], 1)

    def test_deterministic_compressed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / 'a.gz', Path(directory) / 'b.gz'
            p.write_jsonl_gzip(a, self.rows())
            p.write_jsonl_gzip(b, self.rows())
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(len(gzip.decompress(a.read_bytes()).splitlines()), 116)

    def test_mapping_preserves_all_anchors_and_regions(self):
        import regional_climate_handoff as handoff
        manifest = dict(validation=dict(output_coordinates=[[90.0, 23.5], [90.625, 24.0]]), response=dict(sha256='synthetic'))
        with mock.patch.object(p.r.RegionalDownloader, '_cached', return_value=manifest):
            result = handoff.diagnostics(self.config)
        self.assertEqual(result['mapped_districts'], 64)
        self.assertEqual(len({d['district_id'] for d in result['districts']}), 64)
        self.assertTrue(all(d['distance_km'] <= d['second_nearest_distance_km'] for d in result['districts']))
        self.assertFalse(result['native_cell_ids_assigned'])

    def test_adopted_export_preserves_selected_values(self):
        import regional_climate_handoff as handoff
        with tempfile.TemporaryDirectory() as directory:
            prepared = Path(directory)
            source = prepared / '2004.wide-replay.jsonl.gz'
            row = dict(date='2004-02-29', output_longitude=90.0, output_latitude=23.5, values={'T2M': 24.5})
            p.write_jsonl_gzip(source, [row])
            inventory = dict(wide_artifacts=[dict(path=str(source), sha256=p.r.sha256(source.read_bytes()))])
            (prepared / 'inventory.json').write_text(json.dumps(inventory))
            mapping = dict(districts=[dict(district_id='synthetic', diagnostic_output_longitude=90.0,
                diagnostic_output_latitude=23.5, anchor_longitude=90.01, anchor_latitude=23.51, distance_km=1.5)])
            self.assertEqual(handoff.export_context(mapping, prepared), 1)
            path = next((prepared / 'district-context').glob('*.gz'))
            result = json.loads(gzip.decompress(path.read_bytes()))
            self.assertEqual(result['values'], row['values'])
            self.assertEqual(result['spatial_interpretation'], 'representative_point_context')

    def test_full_plan_matches_preflight_identity(self):
        full = p.r.build_full_requests(self.config)
        self.assertEqual(len(full), 100)
        self.assertEqual(full[0], p.r.build_preflight_request(self.config))

if __name__ == '__main__':
    unittest.main()
