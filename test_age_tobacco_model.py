import unittest
from age_tobacco_model import estimate_by_age, age_feature_report
class AgeTests(unittest.TestCase):
    def test_weighted(self):
        r=estimate_by_age({"18_24":1000,"25_44":1000,"45_64":1000,"65_plus":1000})
        self.assertAlmostEqual(r.estimated_users["cigarettes"],350)
        self.assertAlmostEqual(r.estimated_users["vaping"],310)
    def test_missing(self):
        with self.assertRaises(ValueError): estimate_by_age({"18_24":100})
    def test_21_plus(self):
        x=age_feature_report({"18_24":100,"25_44":100,"45_64":100,"65_plus":100},age_18_20_count=30)
        self.assertEqual(x["retail_21_plus_eligible_population"],370)
    def test_21_plus_unknown(self):
        x=age_feature_report({"18_24":100,"25_44":100,"45_64":100,"65_plus":100})
        self.assertIsNone(x["retail_21_plus_eligible_population"])
if __name__=="__main__": unittest.main()
