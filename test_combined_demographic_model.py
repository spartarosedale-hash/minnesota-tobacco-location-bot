import unittest
from combined_demographic_model import DemographicEvidence, combine_demographic_evidence, compare_dimensions, attach_joint_estimate
class CombinedTests(unittest.TestCase):
    def setUp(self):
        self.e=[DemographicEvidence("vaping","CDC",2024,700,10000,"age"),
                DemographicEvidence("vaping","CDC",2024,710,10000,"sex"),
                DemographicEvidence("cigarettes","CDC",2024,1000,10000,"age")]
    def test_no_double_counting(self):
        d=combine_demographic_evidence(self.e)
        self.assertIsNone(d["vaping"].estimated_unique_users)
        self.assertEqual(set(compare_dimensions(d["vaping"])),{"age","sex"})
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): combine_demographic_evidence(self.e+[self.e[0]])
    def test_joint_requires_source(self):
        d=combine_demographic_evidence(self.e)
        with self.assertRaises(ValueError): attach_joint_estimate(d["vaping"],estimated_unique_users=700,validated_joint_source="")
    def test_joint_documented(self):
        d=combine_demographic_evidence(self.e)
        a=attach_joint_estimate(d["vaping"],estimated_unique_users=705,validated_joint_source="validated survey cells")
        self.assertEqual(a.estimated_unique_users,705)
if __name__=="__main__": unittest.main()
