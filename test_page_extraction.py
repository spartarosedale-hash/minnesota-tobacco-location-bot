import unittest
from page_extraction import extract

class PageExtractionTests(unittest.TestCase):
    def test_jsonld_address(self):
        html='<script type="application/ld+json">{"@type":"Store","name":"Example Tobacco","address":{"streetAddress":"123 Main St","addressLocality":"Zimmerman"}}</script>'
        rows=extract(html,"Zimmerman")
        self.assertEqual(rows[0]["address"],"123 Main St")
        self.assertEqual(rows[0]["evidence"],"JSON_LD_ADDRESS")
    def test_plain_text_address(self):
        rows=extract("<p>Zimmerman tobacco shop at 456 Main Street, Zimmerman MN</p>","Zimmerman")
        self.assertEqual(rows[0]["address"],"456 Main Street")
    def test_other_city_jsonld_excluded(self):
        html='<script type="application/ld+json">{"address":{"streetAddress":"123 Main St","addressLocality":"Duluth"}}</script>'
        self.assertEqual(extract(html,"Zimmerman"),[])
if __name__=="__main__":unittest.main()
