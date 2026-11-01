import unittest
from unittest.mock import Mock
from lead_enrichment import enrich

class EnrichmentTests(unittest.TestCase):
    def test_address_and_source_are_unverified(self):
        def fetch(*args,**kwargs):
            r=Mock()
            r.json.return_value={"result":{"addressMatches":[{"matchedAddress":"123 MAIN ST, ZIMMERMAN, MN, 55398","coordinates":{"x":-93.5,"y":45.4}}]}}
            return r
        leads=[{"title":"Example Tobacco 123 Main St","snippet":"Zimmerman MN smoke shop","url":"https://example.org/listing"}]
        result=enrich(leads,"Zimmerman",fetch=fetch)
        row=result["candidates"][0]
        self.assertEqual(row["latitude"],45.4)
        self.assertEqual(row["verification"],"UNVERIFIED_SEARCH_SNIPPET")
        self.assertIn("NOT_BUSINESS_VERIFICATION",row["geocode_status"])
    def test_no_address_does_not_invent_coordinates(self):
        result=enrich([{"title":"Tobacco shop","snippet":"Zimmerman","url":"https://example.org"}],"Zimmerman")
        self.assertIsNone(result["candidates"][0]["latitude"])
if __name__=="__main__": unittest.main()
