import unittest
from demographic_pipeline import age_counts,sex_counts,report_city,code,AGE_GROUPS
class DemographicPipelineTests(unittest.TestCase):
    def test_acs_age_boundaries(self):
        self.assertEqual(AGE_GROUPS["18_24"],(8,9,10,11))
        self.assertEqual(AGE_GROUPS["25_44"],(12,13,14,15))
        self.assertEqual(AGE_GROUPS["45_64"],(16,17,18,19,20))
        self.assertEqual(AGE_GROUPS["65_plus"],(21,22,23,24,25))
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
        self.assertEqual(result["retail_21_plus_population"],sum(s.values())-40)
        self.assertIsNone(result["supplementary_product_scenarios"]["premium_nonpremium_cigars"]["estimated_users"])
        self.assertIsNone(result["supplementary_product_scenarios"]["vaping_mn_benchmark"]["store_revenue"])
if __name__=="__main__": unittest.main()
