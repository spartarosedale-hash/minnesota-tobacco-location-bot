import unittest
from collect_location_demographics import AGE_GROUPS, INCOME_BRACKETS, FIELDS

class DemographicFieldTests(unittest.TestCase):
    def test_age_groups_cover_21_plus_exactly_once(self):
        from collect_location_demographics import AGE21
        grouped = [f"B01001_{i:03d}E" for indices in AGE_GROUPS.values() for i in indices]
        self.assertEqual(sorted(grouped), sorted(AGE21))
    def test_income_brackets_cover_all_16_bins(self):
        bins = [i for indices in INCOME_BRACKETS.values() for i in indices]
        self.assertEqual(sorted(bins), list(range(2, 18)))
    def test_fields_are_unique(self):
        self.assertEqual(len(FIELDS), len(set(FIELDS)))

if __name__ == "__main__":
    unittest.main()
