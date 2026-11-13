"""Source review must preserve uncertainty and distinguish evidence roles."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("source_semantics", ROOT / "scripts/audit_crop_source_semantics.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class SourceSemanticsTests(unittest.TestCase):
    def test_review_covers_entire_snapshot_and_all_lentil_regions(self):
        output = ROOT / "data/catalog/source_review"
        docs = json.loads((output / "document_definition_leads.json").read_text(encoding="utf-8"))
        lentil = json.loads((output / "lentil_region_comparison.json").read_text(encoding="utf-8"))
        self.assertEqual(len(docs), 318)
        self.assertEqual(len({d["source_id"] for d in docs}), 318)
        self.assertEqual(len({d["region"] for d in docs}), 14)
        self.assertEqual(len(lentil), 13)
        self.assertEqual({d["region"] for d in lentil if d["has_month_label_gap"]},
                         {"Dhaka", "Faridpur", "Mymensingh", "Rajshahi"})
        for document in lentil:
            for calendar in document["calendars"]:
                for gap in calendar["month_label_gaps"]:
                    self.assertEqual((gap["before"], gap["after"]), ("December", "February"))
                    self.assertEqual(gap["omitted_month_numbers"], [1])

    def test_nonstandard_month_labels_are_never_guessed(self):
        self.assertEqual(review.month_number("Feb."), 2)
        for value in ("September-February", "জানুয়ারি", "February/March", ""):
            self.assertIsNone(review.month_number(value))

    def test_week_definition_search_does_not_match_iso_inside_words(self):
        pattern = review.DEFINITION_PATTERNS["week_convention_lead"]
        self.assertIsNone(pattern.search("poison and isolated observations"))
        self.assertIsNotNone(pattern.search("ISO 8601 week convention"))

    def test_explicit_intervals_in_disease_and_warning_rows_stay_inactive(self):
        doc = dict(document_id="test", source_pdf="test.pdf", source_sha256="test", crop_folder="Test", region="Test",
                   pages=[dict(page_number=1, text="Weekly rainfall in disease conditions")], weekly_weather=[],
                   tables=[dict(table_id="table", page_number=1, cells=[], rows=[
                       ["Favourable weather conditions for diseases"], ["Disease A", "Weekly total rainfall 40 mm"],
                       ["Weather Warning"], ["Rainfall", "50 mm/day"],
                       ["Favourable environment"], ["Temperature", "Day temperature 20 C"]])])
        result = review.audit([doc])
        self.assertEqual([r["source_role_lead"] for r in result["interval_wording_leads"]],
                         ["pest_or_disease_context", "weather_warning", "crop_requirement_or_preference_context"])
        self.assertTrue(all(not row["usable_as_normal_definition"] and not row["executable"] for row in result["interval_wording_leads"]))
        self.assertEqual(result["summary"]["executable_rules_added"], 0)
        self.assertEqual(result["document_definition_leads"][0]["definition_search_leads"], [])


if __name__ == "__main__":
    unittest.main()
