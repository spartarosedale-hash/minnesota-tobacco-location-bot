import unittest
from unittest.mock import Mock
from source_verification import verify_candidates

class VerificationTests(unittest.TestCase):
    def test_source_address_is_not_operating_confirmation(self):
        def fetch(*args,**kwargs):
            response=Mock()
            response.headers={"Content-Type":"text/html"}
            response.text="<html><body>123 Main St Zimmerman MN tobacco retailer</body></html>"
            return response
        leads=[{"url":"https://example.com/page","address_candidate":"123 Main St, Zimmerman, MN","title":"Tobacco retailer"}]
        row=verify_candidates(leads,fetch=fetch)["candidates"][0]
        self.assertEqual(row["evidence_status"],"SOURCE_MENTIONS_ADDRESS_UNVERIFIED")
        self.assertEqual(row["operating_status"],"UNKNOWN")
        self.assertEqual(row["license_status"],"UNKNOWN")

if __name__=="__main__": unittest.main()
