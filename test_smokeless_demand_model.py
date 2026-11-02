import unittest
from smokeless_demand_model import estimate_smokeless

class TestSmokeless(unittest.TestCase):
    def test_no_invented_price_or_frequency(self):
        r=estimate_smokeless(10000,.021)
        self.assertEqual(r.users,210)
        self.assertIsNone(r.monthly_market_dollars)
        self.assertIsNone(r.monthly_store_dollars)
    def test_scenario(self):
        r=estimate_smokeless(10000,.021,4.2,5,.1)
        self.assertAlmostEqual(r.monthly_store_dollars,210*4.2*52/12*5*.1)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            estimate_smokeless(10000,.021,store_capture=1.2)
if __name__=="__main__": unittest.main()
