import unittest
from location_feature_audit import build_audit

REQUIREMENTS = {"feature_groups": {
    "road_network": ["frontage AADT", "highway AADT"],
    "site_access": ["parking"],
    "observed_validation": ["monthly sales"],
}}

class FeatureAuditTests(unittest.TestCase):
    def test_no_fabricated_aadt_or_sales(self):
        result = build_audit("Zimmerman", REQUIREMENTS)
        self.assertEqual(result["coverage"]["required_features"], 3)
        self.assertEqual(result["coverage"]["measured_features"], 0)
        self.assertIsNone(result["monthly_sales_prediction"])
        self.assertTrue(all(x["value"] is None for x in result["feature_groups"]["road_network"]))
        self.assertEqual(result["feature_groups"]["observed_validation"][0]["status"], "held_out")

    def test_census_population_is_not_a_sales_forecast(self):
        result = build_audit("Litchfield", REQUIREMENTS,
                             {"adult_population_18_plus": 5000, "retail_21_plus_population": 4700})
        self.assertEqual(result["census_population_21_plus"], 4700)
        self.assertIsNone(result["monthly_sales_prediction"])

if __name__ == "__main__":
    unittest.main()
