import unittest
from unittest.mock import patch
import address_forecast as f

class TestAddressForecast(unittest.TestCase):
    @patch("address_forecast.fetch_json")
    def test_lookup(self, fetch):
        fetch.return_value={"result":{"addressMatches":[{"matchedAddress":"123 MAIN ST","coordinates":{"x":-94.0,"y":45.0},"geographies":{"Incorporated Places":[{"NAME":"Test city","STATE":"27","PLACE":"12345"}]}}]}}
        self.assertEqual(f.lookup("123 Main St")["place_code"],"12345")

    @patch("address_forecast.fetch_json")
    def test_demographics(self, fetch):
        cols=["NAME","B01001_001E","B19013_001E"]+f.ADULT_FIELDS
        vals=["Test city","1000","55000"]+["10"]*len(f.ADULT_FIELDS)
        fetch.return_value=[cols,vals]
        self.assertEqual(f.demographics({"state":"27","place_code":"12345"})["adults_21_plus"],340)

    def test_bad_assumptions(self):
        with self.assertRaises(ValueError):
            f.forecast("x",(0.2,0.1,0.3))

if __name__=="__main__":
    unittest.main()
