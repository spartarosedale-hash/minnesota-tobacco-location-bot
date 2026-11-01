import unittest
from audit_location_evidence import audit
class AuditTests(unittest.TestCase):
    def test_no_frontage_inference(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"v.csv"
            p.write_text("store_name,actual_midpoint,prior_estimate\nTest,100000,60000\n")
            d={"results":[{"store":"Test","status":"ok","age_21_plus_tract":500}]}
            t={"Test":{"status":"ok","candidate_segments":[{"attributes":{"AADT":99999}}],"frontage_segment_verified":False}}
            r=audit(d,t,p)
            self.assertIsNone(r["stores"][0]["frontage_aadt"])
            self.assertEqual(r["holdout_mape_percent"],40.0)
            self.assertEqual(r["model_status"],"not_retrained")
if __name__ == "__main__": unittest.main()
