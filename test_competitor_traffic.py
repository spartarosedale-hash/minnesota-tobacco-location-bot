import csv,tempfile,unittest
from pathlib import Path
from competitor_traffic import scan
class TestCompetitorTraffic(unittest.TestCase):
 def test_relative_google_is_not_absolute(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"c.csv"
   with path.open("w",newline="") as f:
    writer=csv.writer(f);writer.writerow(["competitor_name","latitude","longitude","category","visits_per_month","source","measurement_period","confidence"])
    writer.writerow(["A",45,-94,"tobacco",99999,"google_popular_times","2026-10","high"])
    writer.writerow(["B",45.001,-94,"grocery",12000,"measured_counter","2026-10","medium"])
   result=scan(45,-94,path)
   self.assertEqual(result["measured_store_count"],1)
   self.assertEqual(result["measured_visits_sum"],12000)
   self.assertEqual(result["nearby_store_count"],2)
if __name__=="__main__":unittest.main()
