import unittest
from census_location import lookup, ADULT_CODES

class TestCensusLocation(unittest.TestCase):
    def test_age21_sum_and_tract(self):
        def fake(url,params):
            if "geocoder" in url:
                return {"result":{"addressMatches":[{"matchedAddress":"TEST",
                  "geographies":{"Census Tracts":[{"STATE":"27","COUNTY":"003","TRACT":"050100"}]}}]}}
            return [["NAME"]+ADULT_CODES,["Tract"]+["10"]*len(ADULT_CODES)]
        result=lookup("123 Test St, MN",fake)
        self.assertEqual(result["adult_population_21_plus_tract"],320)
        self.assertEqual(result["census_tract"],"050100")
    def test_no_match(self):
        result=lookup("Unknown",lambda url,params:{"result":{"addressMatches":[]}})
        self.assertEqual(result["status"],"address_not_geocoded")
    def test_empty(self):
        with self.assertRaises(ValueError):lookup("")
if __name__=="__main__":unittest.main()
