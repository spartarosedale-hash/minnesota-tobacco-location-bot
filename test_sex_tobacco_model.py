import unittest
from sex_tobacco_model import estimate_by_sex

class SexTobaccoTests(unittest.TestCase):
    def test_rates(self):
        r=estimate_by_sex({"male":5000,"female":5000})
        self.assertAlmostEqual(r.product_users["cigarettes"],995)
        self.assertAlmostEqual(r.product_users["vaping"],705)
        self.assertAlmostEqual(r.product_users["cigars_all"],375)
        self.assertAlmostEqual(r.product_users["smokeless"],265)
    def test_missing(self):
        with self.assertRaises(ValueError): estimate_by_sex({"male":100})
    def test_negative(self):
        with self.assertRaises(ValueError): estimate_by_sex({"male":-1,"female":100})
if __name__=="__main__": unittest.main()
