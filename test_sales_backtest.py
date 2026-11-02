import unittest
from sales_backtest import leave_one_out

class BacktestTests(unittest.TestCase):
    def test_held_out_store_not_used(self):
        rows = [
            {"store": "A", "city": "A", "low": 100.0, "high": 100.0, "mid": 100.0},
            {"store": "B", "city": "B", "low": 200.0, "high": 200.0, "mid": 200.0},
            {"store": "C", "city": "C", "low": 300.0, "high": 300.0, "mid": 300.0},
        ]
        result = leave_one_out(rows)
        self.assertEqual(result[0]["prediction_monthly_usd"], 250)
        self.assertEqual(result[2]["prediction_monthly_usd"], 150)
        self.assertFalse(result[0]["location_features_used"])

    def test_single_store_no_prediction(self):
        self.assertEqual(leave_one_out([{"store": "A", "mid": 100.0}]), [])

if __name__ == "__main__":
    unittest.main()
