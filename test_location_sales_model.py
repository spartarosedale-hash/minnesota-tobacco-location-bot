import unittest
from location_sales_model import SiteInputs, predict_monthly_sales

class LocationSalesTests(unittest.TestCase):
    def test_missing_traffic_not_invented(self):
        r = predict_monthly_sales(SiteInputs(average_ticket=29.67))
        self.assertIsNone(r["monthly_gross_sales"])
        self.assertIn("frontage_aadt", r["missing"])

    def test_road_and_repeat_components(self):
        x = SiteInputs(frontage_aadt=10000, frontage_capture_rate=.001,
                       highway_aadt=20000, highway_access_share=.2,
                       highway_capture_rate=.001, local_21_plus=5000,
                       local_customer_penetration=.1, local_visits_per_month=2,
                       competition_retention=.8, accessibility_factor=1,
                       average_ticket=30)
        r = predict_monthly_sales(x)
        self.assertEqual(r["status"], "scenario_not_validated")
        self.assertGreater(r["monthly_gross_sales"], 0)
        self.assertEqual(r["components"]["frontage_daily"], 10)

    def test_invalid_capture_rejected(self):
        x = SiteInputs(frontage_aadt=1, frontage_capture_rate=1.1,
                       highway_aadt=1, highway_access_share=1,
                       highway_capture_rate=1, local_21_plus=1,
                       local_customer_penetration=1, local_visits_per_month=1,
                       competition_retention=1, accessibility_factor=1,
                       average_ticket=30)
        with self.assertRaises(ValueError):
            predict_monthly_sales(x)

if __name__ == "__main__":
    unittest.main()
