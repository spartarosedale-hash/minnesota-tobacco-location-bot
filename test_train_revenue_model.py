import csv,tempfile,unittest
from pathlib import Path
from train_revenue_model import load,train,FEATURES
class Tests(unittest.TestCase):
 def test_holdout_and_minimum(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"stores.csv"
   with p.open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["store_name",*FEATURES,"monthly_sales_excluding_tax"])
    w.writerow(["Litchfield Tobacco",5000,50000,8000,3,1000,80,90000])
    w.writerow(["Independent A",5000,50000,8000,3,1000,80,90000])
   self.assertEqual(len(load(p)),1)
   with self.assertRaisesRegex(ValueError,"at least 10"):
    train(p)
if __name__=="__main__":unittest.main()
