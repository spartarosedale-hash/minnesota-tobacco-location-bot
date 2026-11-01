import csv,tempfile,unittest
from pathlib import Path
from google_popular_times import analyze
class Tests(unittest.TestCase):
 def test_google_relative(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"popular.csv"
   with p.open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["business_name","day","hour","relative_popularity","source_url","observed_date"])
    w.writerow(["Store A","Monday",9,80,"https://www.google.com/maps/place/example","2026-11-01"])
    w.writerow(["Store B","Monday",9,80,"https://www.google.com/maps/place/other","2026-11-01"])
   result=analyze(p)
   self.assertEqual(len(result["businesses"]),2)
   self.assertIsNone(result["businesses"]["Store A"]["measured_visitors"])
if __name__=="__main__":unittest.main()
