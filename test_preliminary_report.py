import unittest
from preliminary_report import benchmark
class BenchmarkTests(unittest.TestCase):
 def test_actual_comparables(self):
  result=benchmark("231 N Sibley Ave, Litchfield, MN 55355")
  self.assertEqual(result["monthly_sales_usd"]["comparison_low"],32000)
  self.assertEqual(result["monthly_sales_usd"]["comparison_high"],95000)
  self.assertEqual(result["monthly_sales_usd"]["comparison_median"],67250)
  self.assertNotIn("Litchfield Tobacco",result["comparable_stores"])
  self.assertNotIn("Zimmerman Tobacco",result["comparable_stores"])
 def test_missing_address(self):
  with self.assertRaises(ValueError):benchmark("")
if __name__=="__main__":unittest.main()
