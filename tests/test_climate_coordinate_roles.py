"""Synthetic regressions distinguishing original anchors from returned positions."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/acquire'))
import check_climate_coordinate_roles as check


class CoordinateRoleTests(unittest.TestCase):
    def setUp(self):
        self.features = {'district': dict(type='Polygon', coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]])}
        self.row = dict(district_id='district', longitude='0.9', latitude='0.5')
        self.coordinates = [(1.1, 0.5), (0, 0.5)]
        distance = check.r.haversine_km(0.5, 0.9, 0.5, 1.1)
        self.diagnostic = dict(anchor_longitude=0.9, anchor_latitude=0.5,
            diagnostic_output_longitude=1.1, diagnostic_output_latitude=0.5, distance_km=distance, exact_distance_ties=1)

    def test_interior_anchor_and_exterior_output_are_distinct_roles(self):
        result = check.check_role(self.row, self.diagnostic, self.features, self.coordinates)
        self.assertEqual(result['anchor_containing_district_ids'], ['district'])
        self.assertEqual(result['output_containing_district_ids'], [])
        self.assertFalse(result['output_on_pinned_boundary'])
        self.assertEqual(result['anchor_longitude'], 0.9)
        self.assertEqual(result['output_longitude'], 1.1)

    def test_registry_anchor_mismatch_is_rejected(self):
        self.diagnostic['anchor_longitude'] = 1.1
        with self.assertRaisesRegex(ValueError, 'differs from original registry'):
            check.check_role(self.row, self.diagnostic, self.features, self.coordinates)

    def test_exterior_original_anchor_is_rejected(self):
        self.row['longitude'] = '1.1'
        self.diagnostic['anchor_longitude'] = 1.1
        with self.assertRaisesRegex(ValueError, 'assigned pinned district'):
            check.check_role(self.row, self.diagnostic, self.features, self.coordinates)

    def test_mapping_change_or_distance_error_is_rejected(self):
        self.diagnostic['distance_km'] += 1
        with self.assertRaisesRegex(ValueError, 'distance mismatch'):
            check.check_role(self.row, self.diagnostic, self.features, self.coordinates)
        self.diagnostic['diagnostic_output_longitude'] = 0
        with self.assertRaisesRegex(ValueError, 'nearest-output ranking'):
            check.check_role(self.row, self.diagnostic, self.features, self.coordinates)

if __name__ == '__main__':
    unittest.main()
