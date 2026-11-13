"""Delivery-only regressions; synthetic bytes, no NASA data/network required."""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/acquire'))
import prepare_climate_team_delivery as delivery


class ClimateTeamDeliveryTests(unittest.TestCase):
    def example_tree(self, root, duplicate=False, chart_mismatch=False):
        p=root/'cache/nasa_power_regional/prepared-v1'
        (p/'district-context').mkdir(parents=True)
        row=dict(date='2001-01-01',output_longitude=88.125,output_latitude=24.5,values={'T2M':17.48})
        for name in ('2001.wide-replay.jsonl.gz','district-context/bd-district-chapainawabganj-2001.wide-replay.jsonl.gz'):
            with gzip.open(p/name,'wt') as f:
                f.write(json.dumps(row)+'\n')
                if duplicate:f.write(json.dumps(row)+'\n')
        month=dict(date='2001-01',output_longitude=88.125,output_latitude=24.5,value=5)
        (p/'bgd-padded-national__PRECTOTCORR__20010101_20011231.monthly.json').write_text(json.dumps([month]))
        chart=dict(series=[dict(month,value=8) if chart_mismatch else month],period=['2001-01','2025-12'],time_standard='LST')
        (p/'chart-88.125-24.5-PRECTOTCORR.json').write_text(json.dumps(chart))
        return p

    def test_component_missing_wrong_hash_or_size_is_not_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'part'
            with self.assertRaises(ValueError):delivery.verified_component(p,'0'*64)
            p.write_bytes(b'synthetic')
            with self.assertRaises(ValueError):delivery.verified_component(p,'0'*64)
            with self.assertRaises(ValueError):delivery.verified_component(p,delivery.package.digest(p),123)
            delivery.verified_component(p,delivery.package.digest(p),9)

    def test_inventory_covers_actual_folder_without_claiming_recipient_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'archive').write_bytes(b'synthetic')
            delivery.write_inventory(p)
            result=delivery.write_inventory(p)
            self.assertEqual(result['file_count'],1)
            self.assertEqual(result['files'][0]['sha256'],delivery.package.digest(p/'archive'))
            self.assertFalse(result['recipient_received'])
            self.assertFalse(result['independent_recipient_validation'])

    def test_real_example_selects_same_region_and_context_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.example_tree(Path(tmp))
            result=delivery.selected_example(p)
            self.assertEqual(result['regional']['record']['values'],{'T2M':17.48})
            self.assertEqual(result['district_context']['record']['values'],result['regional']['record']['values'])
            self.assertEqual(result['regional']['path'],'cache/nasa_power_regional/prepared-v1/2001.wide-replay.jsonl.gz')

    def test_duplicate_example_key_is_not_silently_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.example_tree(Path(tmp),duplicate=True)
            with self.assertRaisesRegex(ValueError,'duplicate'):delivery.selected_example(p)

    def test_monthly_chart_example_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.example_tree(Path(tmp),chart_mismatch=True)
            with self.assertRaisesRegex(ValueError,'chart/monthly mismatch'):delivery.selected_example(p)

if __name__=='__main__':unittest.main()
