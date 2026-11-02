import unittest
from demographic_pipeline import age_counts,sex_counts,report_city,code,AGE_GROUPS
class DemographicPipelineTests(unittest.TestCase):
    def test_population_alignment_and_no_joint_prediction(self):
        row={"NAME":"Test city, Minnesota"}
        for sex in ("male","female"):
            for ids in AGE_GROUPS.values():
                for i in ids: row[code(sex,i)]="10"
        a=age_counts(row);s=sex_counts(row)
        self.assertEqual(sum(a.values()),sum(s.values()))
        result=report_city("Test",row)
        self.assertEqual(result["adult_population_18_plus"],sum(s.values()))
        self.assertIsNone(result["product_evidence"]["vaping"]["joint_estimate"])
        self.assertEqual(result["sales_prediction_status"],"not calibrated")
if __name__=="__main__": unittest.main()
