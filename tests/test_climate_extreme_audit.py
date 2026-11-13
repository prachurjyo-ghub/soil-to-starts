"""Synthetic audit-method tests; no cached observations or network required."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/acquire'))
import audit_climate_extremes as audit


class ExtremeAuditTests(unittest.TestCase):
    def test_daily_rate_is_accumulated_once_and_negative_celsius_retained(self):
        self.assertEqual(audit.monthly_statistic('PRECTOTCORR', [965.18, 1, 0]), 966.18)
        self.assertEqual(audit.monthly_statistic('T2M_MIN', [-1, 1]), 0)
        self.assertIsNone(audit.monthly_statistic('PRECTOTCORR', [None]))

    def test_exact_match_rejects_duplicates_and_wrong_location(self):
        rows = [dict(date='2017-07-22', longitude=91.25, value=965.18)]
        predicate = lambda r: r['date'] == '2017-07-22' and r['longitude'] == 91.25
        self.assertEqual(audit.unique_match(rows, predicate)['value'], 965.18)
        with self.assertRaises(ValueError):
            audit.unique_match(rows * 2, predicate)
        with self.assertRaises(ValueError):
            audit.unique_match(rows, lambda r: r['longitude'] == 90)

    def test_temperature_checks_matched_support_and_preserves_source_conflict(self):
        c = (90, 24)
        series = {p: {c: {'20010101': value}} for p, value in [('T2M_MIN', -1), ('T2M', 1), ('T2M_MAX', 3)]}
        self.assertEqual(audit.temperature_consistency(series), (1, 0, []))
        series['T2M'][c]['20010101'] = 4
        self.assertEqual(len(audit.temperature_consistency(series)[2]), 1)
        series['T2M'][c]['20010102'] = 2
        with self.assertRaises(ValueError):
            audit.temperature_consistency(series)

    def test_extrema_filter_uses_actual_district_coordinates_and_counts_ties(self):
        series = {(90, 24): {'20010101': 5, '20010102': 5}, (91, 25): {'20010101': 965.18}}
        self.assertEqual(audit.extrema_candidates('PRECTOTCORR', series)[0][1], 965.18)
        filtered = audit.extrema_candidates('PRECTOTCORR', series, {(90, 24)})[0]
        self.assertEqual(filtered[1], 5)
        self.assertEqual(len(filtered[2]), 2)

    def test_geometry_excludes_holes_and_labels_boundary(self):
        feature = dict(properties={'shapeName': 'synthetic'}, geometry=dict(type='Polygon', coordinates=[
            [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]],
            [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]]))
        self.assertEqual(audit.spatial_relation((3, 3), [feature])['classification'], 'inside_pinned_Bangladesh_geometry')
        self.assertIn('outside', audit.spatial_relation((1.5, 1.5), [feature])['classification'])
        self.assertEqual(audit.spatial_relation((0, 2), [feature])['classification'], 'on_pinned_boundary')

if __name__ == '__main__':
    unittest.main()
