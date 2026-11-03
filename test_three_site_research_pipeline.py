import unittest
from unittest.mock import patch
from three_site_research_pipeline import SITES, census_tract, research_site

class ThreeSiteResearchTests(unittest.TestCase):
    def test_three_distinct_addresses(self):
        self.assertEqual(len(SITES),3)
        self.assertIn("Saint Paul",SITES[2][1])
    def test_acs_21_plus_correct_bins(self):
        geo={"Census Tracts":[{"GEOID":"27123012345"}]}
        def fake(url,params):
            keys=params["get"].split(",")
            row={k:"0" for k in keys}
            row["NAME"]="test tract"
            row["B01001_001E"]="1000"
            row["B01001_010E"]="50"
            row["B01001_034E"]="40"
            row["B19013_001E"]="75000"
            return [keys,[row[k] for k in keys]]
        with patch("three_site_research_pipeline.get_json",side_effect=fake):
            result=census_tract(geo)
        self.assertEqual(result["population_21_plus"],90)
        self.assertEqual(result["median_household_income"],75000)
        self.assertEqual(result["geography"],"Census tract, NOT drive-time catchment")
    def test_no_sales_used_when_geocode_fails(self):
        with patch("three_site_research_pipeline.geocode",return_value=None):
            r=research_site("Example","123 Main")
        self.assertFalse(r["sales_inputs_used"])
        self.assertIsNone(r["prediction"])
        self.assertIsNone(r["frontage_aadt"])

if __name__=="__main__":
    unittest.main()
