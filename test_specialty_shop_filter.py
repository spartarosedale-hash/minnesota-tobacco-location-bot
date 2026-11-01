import unittest
from specialty_shop_filter import specialty_match

class SpecialtyShopTests(unittest.TestCase):
    def test_specialty_tags(self):
        for tag in ("tobacco","e-cigarette","vape","cigars","hookah"):
            self.assertEqual(specialty_match({"name":"Main Street","shop":tag}),"specialty_osm_tag")
    def test_specialty_names(self):
        for name in ("Main Smoke Shop","North Vape Shop","Downtown Tobacco","Premium Cigar Shop"):
            self.assertEqual(specialty_match({"name":name,"shop":"convenience"}),"specialty_name_match")
    def test_generic_convenience_excluded(self):
        self.assertIsNone(specialty_match({"name":"Corner Market","shop":"convenience"}))
    def test_gas_and_dispensary_excluded(self):
        self.assertIsNone(specialty_match({"name":"Tobacco Gas Station","shop":"convenience"}))
        self.assertIsNone(specialty_match({"name":"Cannabis Dispensary","shop":"tobacco"}))
if __name__=="__main__":unittest.main()
