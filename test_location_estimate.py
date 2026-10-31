import unittest
from location_estimate import predict,read_comparables

class TestEstimate(unittest.TestCase):
    def test_baseline(self):
        result=predict("123 Unknown St, MN",1200,1500,read_comparables())
        self.assertEqual(result["comparable_count"],8)
        self.assertEqual(result["monthly_sales_low"],8700)
        self.assertEqual(result["monthly_sales_high"],93800)
        self.assertEqual(result["monthly_sales_base"],61000)
        self.assertEqual(result["confidence"],"insufficient evidence")
    def test_exclude_target(self):
        result=predict("212 2nd St E Ste 100, Jordan, MN 55352",1200,1500,read_comparables())
        self.assertEqual(result["comparable_count"],7)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            predict("",1200,1500,read_comparables())

if __name__=="__main__": unittest.main()
