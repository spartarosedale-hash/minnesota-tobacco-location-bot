import unittest
from unittest.mock import patch,Mock
from free_places import discover
class Tests(unittest.TestCase):
 @patch("free_places.requests.post")
 def test_discovery(self,post):
  response=Mock()
  response.json.return_value={"elements":[{"type":"node","id":1,"lat":45,"lon":-94,"tags":{"name":"Test","shop":"tobacco"}}]}
  post.return_value=response
  report=discover(45,-94)
  self.assertEqual(report["counts_by_category"]["tobacco"],1)
  self.assertIsNone(report["nearby_places"][0]["estimated_visits"])
if __name__=="__main__":unittest.main()
