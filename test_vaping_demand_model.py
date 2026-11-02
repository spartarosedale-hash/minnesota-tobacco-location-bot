import unittest
from vaping_demand_model import estimate_vaping_scenario

class TestVapingDemand(unittest.TestCase):
    def test_baseline(self):
        r = estimate_vaping_scenario(10000)
        self.assertAlmostEqual(r.estimated_adult_vapers, 710)
        self.assertAlmostEqual(r.total_market_spend_benchmark, 710*82.22)
        self.assertIsNone(r.store_revenue_scenario)
    def test_capture(self):
        r = estimate_vaping_scenario(10000, store_capture_share=.1)
        self.assertAlmostEqual(r.store_revenue_scenario, 710*82.22*.1)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            estimate_vaping_scenario(10000, store_capture_share=1.2)

if __name__ == "__main__":
    unittest.main()
