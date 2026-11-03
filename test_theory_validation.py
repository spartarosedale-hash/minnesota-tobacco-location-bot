import csv
import unittest
from pathlib import Path
from theory_validation import analyze

class TheoryValidationTests(unittest.TestCase):
    def test_revenue_gap_is_traffic_not_ticket(self):
        with (Path(__file__).parent/"data"/"store_sales_comparables.csv").open(newline="",encoding="utf-8") as f:
            result=analyze(list(csv.DictReader(f)))
        self.assertTrue(result["hypothesis_supported_by_reported_sales_and_tickets"])
        self.assertGreater(result["transaction_ratio"],2.6)
        self.assertLess(result["transaction_ratio"],2.9)
        self.assertLess(abs(result["ticket_ratio"]-1),.05)
        self.assertIsNone(result["independent_location_model_prediction"])
        self.assertIsNone(result["predictive_accuracy"])
        self.assertEqual(result["stores"][0]["transaction_count_status"],"derived_from_sales_and_ticket")
        self.assertEqual(result["stores"][1]["transaction_count_status"],"observed_pos")

if __name__=="__main__":
    unittest.main()
