"""Preservation and fail-closed checks for the inactive crop evidence package."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from crop_evidence_lineage import select_stage_candidates
spec = importlib.util.spec_from_file_location("crop_evidence", ROOT / "scripts/build_crop_evidence.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
OUT = ROOT / "data/catalog/normalized"


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


class CropEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = builder.read_csv(ROOT / "assets/crop_planning_dataset.csv")
        cls.mapping = builder.read_csv(ROOT / "assets/bamis_region_district_mapping.csv")
        cls.entries = [json.loads(line) for line in (OUT / "entries.jsonl").read_text(encoding="utf-8").splitlines()]
        cls.weather = {r["entry_id"]: r for r in map(json.loads, (OUT / "weather_normals.jsonl").read_text(encoding="utf-8").splitlines())}

    def test_every_input_row_and_null_preserved(self):
        self.assertEqual(len(self.entries), len(self.rows))
        self.assertEqual(len({e["entry_id"] for e in self.entries}), len(self.rows))
        for entry in self.entries:
            row = self.rows[entry["csv_line"] - 2]
            self.assertEqual(entry["growth_stage"], row["growth_stage"] or None)
            for metric in builder.METRICS:
                self.assertEqual(self.weather[entry["entry_id"]]["values"][metric], builder.number(row[metric]))
        self.assertEqual(sum(e["growth_stage"] is None for e in self.entries), 939)

    def test_cross_year_keeps_physical_column_order_without_invented_offsets(self):
        calendar = next(c for c in load("calendars.json") if c["crop_label"] == "Rice" and c["region_label"] == "Rajshahi" and c["season_label"] == "Boro")
        entries = [e for e in self.entries if e["calendar_id"] == calendar["calendar_id"]]
        weeks = [e["standard_week"] for e in entries]
        self.assertTrue(any(a > b for a, b in zip(weeks, weeks[1:])), weeks)
        self.assertTrue(all(e["year_offset"] is None and e["cycle_offset"] is None for e in entries))

    def test_repetitions_and_excluded_banana_retained(self):
        self.assertEqual(len(load("repeated_weeks.json")), 124)
        group = next(g for g in load("repeated_weeks.json") if g["key"] == ["Pointed Gourd", "Kharif", "Mymensingh", "23"])
        calendar_ids = {e["calendar_id"] for e in self.entries if e["entry_id"] in group["entry_ids"]}
        self.assertEqual(len(calendar_ids), 2)
        self.assertTrue(any(r["source_pdf"].endswith("Banana/Dhaka/25595.pdf") for r in load("quarantine.json")["exclusions"]))

    def test_ambiguous_columns_never_get_an_invented_order(self):
        ambiguous = [e for e in self.entries if len(e["source_column_candidates"]) > 1]
        self.assertTrue(all(e["sequence_index"] is None for e in ambiguous))
        audit = load("lineage_audit.json")
        self.assertEqual(len(audit), 221)
        self.assertEqual(len({r["previous_entry_id"] for r in audit}), 221)
        for record in audit:
            selected = [c for c in record["numeric_candidates"] if c["source_entry_id"] in record["selected_source_entry_ids"]]
            self.assertEqual(len(selected), 1)
            self.assertTrue(record["imported_growth_stage"])
            self.assertEqual(selected[0]["extracted_stage"], record["imported_growth_stage"])

    def test_stage_lineage_never_uses_blank_fuzzy_or_tied_matches(self):
        candidates = [(("table", 1), {}), (("table", 2), {})]
        stage_by_column = {("table", 1): "Seedling", ("table", 2): "Harvesting"}
        self.assertEqual(select_stage_candidates(candidates, "Seedling", stage_by_column), [candidates[0]])
        for label in (None, "", "Seed", "Unrecorded"):
            self.assertEqual(select_stage_candidates(candidates, label, stage_by_column), candidates)
        stage_by_column[("table", 2)] = "Seedling"
        self.assertEqual(select_stage_candidates(candidates, "Seedling", stage_by_column), candidates)

    def test_receipt_text_fingerprint_ignores_checkout_line_endings_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_bytes(b"crop,region\nRice,Dhaka\n")
            original = builder.input_fingerprint(path)
            path.write_bytes(b"crop,region\r\nRice,Dhaka\r\n")
            self.assertEqual(builder.input_fingerprint(path), original)
            path.write_bytes(b"crop,region\r\nRice,Sylhet\r\n")
            self.assertNotEqual(builder.input_fingerprint(path), original)
            binary = path.with_suffix(".gz")
            binary.write_bytes(b"a\r\nb")
            first = builder.input_fingerprint(binary)
            binary.write_bytes(b"a\nb")
            self.assertNotEqual(builder.input_fingerprint(binary), first)

    def test_source_relationships_and_physical_entry_identity(self):
        source_entries = [json.loads(line) for line in (OUT / "source_entries.jsonl").read_text(encoding="utf-8").splitlines()]
        identities = {e["source_entry_id"] for e in source_entries}
        self.assertEqual(len(identities), len(source_entries))
        calendars = {c["calendar_id"] for c in load("calendar_inventory.json")}
        self.assertTrue(all(e["calendar_id"] in calendars for e in source_entries))
        self.assertEqual(len({(e["calendar_id"], e["sequence_index"]) for e in source_entries}), len(source_entries))
        for entry in self.entries:
            self.assertTrue(all(ref["source_entry_id"] in identities for ref in entry["source_column_candidates"]))

    def test_rules_stay_inactive_and_compatibility_complete(self):
        rules = load("rule_compatibility.json")
        self.assertEqual(len(rules), 17)
        self.assertTrue(all(not r["evaluable_now"] for r in rules))
        self.assertEqual(load("qa.json")["executable_rules"], 0)
        self.assertEqual(len(load("legacy_crop_candidates.json")), 6)

    def test_invalid_numeric_and_geographic_inputs_fail(self):
        for field, value in (("humidity_mean_pct", "101"), ("rainfall_mm", "nan"),
                             ("duration_min_days", "9999"), ("region", "Unknown")):
            with self.subTest(field=field):
                row = dict(self.rows[0], **{field: value})
                with self.assertRaises(ValueError):
                    builder.validate_rows([row], self.mapping)
        mapping = copy.deepcopy(self.mapping)
        mapping[0]["district"] = mapping[1]["district"]
        with self.assertRaises(ValueError):
            builder.validate_rows(self.rows, mapping)


if __name__ == "__main__":
    unittest.main()
