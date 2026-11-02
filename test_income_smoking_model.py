import unittest
from income_smoking_model import estimate_cigarette_demand, compare_with_observed

class IncomeSmokingTests(unittest.TestCase):
    def test_weighted(self):
        r = estimate_cigarette_demand({"under_35k":100, "35k_to_74999":100,
                                      "75k_to_99999":100, "100k_plus":100})
        self.assertAlmostEqual(r.estimated_smokers, 51.0)
        self.assertAlmostEqual(r.prevalence, .1275)
    def test_missing_bucket(self):
        with self.assertRaises(ValueError):
            estimate_cigarette_demand({"under_35k": 100})
    def test_zero(self):
        with self.assertRaises(ValueError):
            estimate_cigarette_demand(dict.fromkeys(("under_35k","35k_to_74999","75k_to_99999","100k_plus"), 0))
    def test_sales_not_invented(self):
        r = estimate_cigarette_demand({"under_35k":100,"35k_to_74999":0,"75k_to_99999":0,"100k_plus":0})
        self.assertIsNone(compare_with_observed(r,None)["observed_monthly_cigarette_sales"])
if __name__ == "__main__":
    unittest.main()
