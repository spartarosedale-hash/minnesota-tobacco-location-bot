import unittest
from lead_filter import relevant
class LeadFilterTests(unittest.TestCase):
    def test_fashion_false_positive(self):
        self.assertFalse(relevant({"title":"ZIMMERMANN Dresses","snippet":"Fashion designer","url":"https://www.zimmermann.com"},"Zimmerman"))
    def test_microsoft_false_positive(self):
        self.assertFalse(relevant({"title":"Microsoft","snippet":"Software","url":"https://www.microsoft.com"},"Litchfield"))
    def test_local_tobacco_candidate(self):
        self.assertTrue(relevant({"title":"Tobacco retailer in Zimmerman MN","snippet":"Retail license application in Sherburne County","url":"https://example.org/notice"},"Zimmerman"))
    def test_query_alone_not_evidence(self):
        self.assertFalse(relevant({"title":"Generic clothing","snippet":"Shop clothing","query":"Zimmerman MN tobacco","url":"https://example.org"},"Zimmerman"))
if __name__=="__main__":unittest.main()
