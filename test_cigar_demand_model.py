import unittest
from cigar_demand_model import estimate_cigar_demand

class CigarDemandTests(unittest.TestCase):
    def test_weighted(self):
        r=estimate_cigar_demand({"in_poverty":1000,"poverty_to_200pct":1000,"above_200pct":1000})
        self.assertAlmostEqual(r.premium_users,22)
        self.assertAlmostEqual(r.nonpremium_users,117)
    def test_missing(self):
        with self.assertRaises(ValueError):
            estimate_cigar_demand({"in_poverty":100})
    def test_zero(self):
        with self.assertRaises(ValueError):
            estimate_cigar_demand({"in_poverty":0,"poverty_to_200pct":0,"above_200pct":0})
    def test_invalid(self):
        with self.assertRaises(ValueError):
            estimate_cigar_demand({"in_poverty":-1,"poverty_to_200pct":100,"above_200pct":100})
if __name__=="__main__":
    unittest.main()
