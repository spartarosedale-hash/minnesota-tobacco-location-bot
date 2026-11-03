import unittest
from demographic_demand import estimate_vape_users_by_age, summarize_market

class DemographicDemandTests(unittest.TestCase):
    def test_weighted_21_plus_age_prevalence(self):
        counts={"21_24":1000,"25_34":0,"35_49":0,"50_64":0,"65_plus":0}
        r=estimate_vape_users_by_age(counts)
        self.assertEqual(r["estimated_users"],155)
        self.assertEqual(r["weighted_prevalence_percent"],15.5)

    def test_missing_bins_not_assumed(self):
        self.assertIsNone(estimate_vape_users_by_age({"21_24":100})["estimated_users"])

    def test_income_does_not_fabricate_sales_effect(self):
        r=summarize_market(median_household_income=85000)
        self.assertEqual(r["median_household_income_usd"],85000)
        self.assertIsNone(r["income_multiplier"])
        self.assertIsNone(r["cigarette_users_estimate"])

if __name__=="__main__":
    unittest.main()
