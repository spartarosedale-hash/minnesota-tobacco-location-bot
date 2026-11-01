import unittest
from datetime import date
from location_feature_registry import FEATURES, coverage, validate_observation

class FeatureRegistryTests(unittest.TestCase):
    def test_unique_features(self):
        names = [f.name for f in FEATURES]
        self.assertEqual(len(names), len(set(names)))
        self.assertGreaterEqual(len(names), 20)

    def test_verified_requires_source(self):
        item = {"value": 12000, "status": "verified", "observed_date": "2024-06-01"}
        self.assertIn("missing_source", validate_observation(item, date(2026, 10, 31)))

    def test_future_data_rejected(self):
        item = {"value": 100, "status": "verified", "source_url": "https://example.org",
                "observed_date": "2027-01-01"}
        self.assertIn("future_observation", validate_observation(item, date(2026, 10, 31)))

    def test_coverage_only_verified(self):
        data = {"aadt_frontage": {"value": 15000, "status": "verified",
                                 "source_url": "https://example.org", "observed_date": "2024-01-01"},
                "weekly_open_hours": {"value": 80, "status": "owner_reported", "observed_date": "2026-10-31"}}
        result = coverage(data)
        self.assertEqual(result["verified"], 1)
        self.assertIn("weekly_open_hours", result["missing_or_unverified"])

if __name__ == "__main__":
    unittest.main()
