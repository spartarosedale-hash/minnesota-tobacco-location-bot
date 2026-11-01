import os,unittest
from unittest.mock import patch,Mock
from besttime_connector import fetch_nearby
class BestTimeTests(unittest.TestCase):
 def test_disabled(self):
  self.assertEqual(fetch_nearby(45,-94)["status"],"disabled")
 def test_missing_key(self):
  with patch.dict(os.environ,{"BESTTIME_PRIVATE_KEY":""}):
   self.assertEqual(fetch_nearby(45,-94,enable_api=True)["status"],"missing_credentials")
 @patch("besttime_connector.requests.get")
 def test_relative_never_absolute(self,get):
  response=Mock()
  response.json.return_value={"status":"OK","venues":[{"venue_name":"Example","venue_lat":45,"venue_lng":-94,"day_raw_whole":[10,50,100]}]}
  get.return_value=response
  with patch.dict(os.environ,{"BESTTIME_PRIVATE_KEY":"test"}):
   venue=fetch_nearby(45,-94,enable_api=True)["venues"][0]
  self.assertIsNone(venue["absolute_visits"])
  self.assertEqual(venue["relative_busyness_peak"],100)
if __name__=="__main__":unittest.main()
