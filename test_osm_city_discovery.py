import unittest
import requests
from osm_city_discovery import discover_osm

class Response:
    def __init__(self,data):self.data=data
    def raise_for_status(self):pass
    def json(self):return self.data

class OSMTests(unittest.TestCase):
    def test_fallback_after_timeout(self):
        called=[]
        def fetch(url,**kwargs):
            called.append(url)
            if len(called)==1:raise requests.Timeout("timeout")
            return Response({"elements":[{"type":"node","id":1,"lat":45,"lon":-93,
              "tags":{"name":"Example Smoke","shop":"tobacco","addr:housenumber":"100","addr:street":"Main St"}}]})
        r=discover_osm("Zimmerman",fetch=fetch,endpoints=("https://one","https://two"))
        self.assertEqual(r["status"],"available")
        self.assertEqual(len(r["candidates"]),1)
        self.assertEqual(len(r["errors"]),1)
    def test_empty_is_not_unavailable(self):
        r=discover_osm("Litchfield",fetch=lambda *a,**k:Response({"elements":[]}),endpoints=("https://one",))
        self.assertEqual(r["status"],"empty")
    def test_all_fail(self):
        def fail(*a,**k):raise requests.Timeout("timeout")
        r=discover_osm("Litchfield",fetch=fail,endpoints=("https://one","https://two"))
        self.assertEqual(r["status"],"unavailable")
        self.assertEqual(len(r["errors"]),2)
    def test_bad_payload_retries(self):
        r=discover_osm("Litchfield",fetch=lambda *a,**k:Response({"remark":"error"}),endpoints=("https://one",))
        self.assertEqual(r["status"],"unavailable")
if __name__=="__main__":unittest.main()
