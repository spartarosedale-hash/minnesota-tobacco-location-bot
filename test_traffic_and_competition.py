import unittest
from unittest.mock import patch,Mock
from traffic_and_competition import miles,nearby_aadt

class TestEnrichment(unittest.TestCase):
    def test_distance(self):
        self.assertAlmostEqual(miles(45,-94,45,-94),0)
        self.assertGreater(miles(45,-94,45.02,-94),1)
    @patch("traffic_and_competition.requests.get")
    def test_aadt(self,get):
        response=Mock()
        response.json.return_value={"features":[{"attributes":{"AADT_CURRENT_VOLUME":8400,"AADT_CURRENT_YEAR":2024,"AADT_ROUTE_LABEL":"A"}}]}
        get.return_value=response
        result=nearby_aadt(45,-94)
        self.assertEqual(result["nearby_segments"][0]["aadt"],8400)
if __name__=="__main__":unittest.main()
