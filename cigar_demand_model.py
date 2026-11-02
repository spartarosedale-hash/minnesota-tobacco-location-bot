"""Research-based premium/nonpremium cigar prevalence scenarios.

Historical National Academies figures by household poverty ratio.
These are NOT income-dollar brackets and must not be applied to median income.
Inputs are counts of adults in each poverty-ratio bracket, not households.
Cigar types may overlap with cigarette/vape users: do not sum across products
to estimate unique tobacco users. This module is not a revenue forecast.
Source: National Academies, Premium Cigars: Patterns of Use, Marketing,
and Health Effects (historical 2010–2019 data).
https://nap.nationalacademies.org/catalog/26421/premium-cigars-patterns-of-use-marketing-and-health-effects
"""
from dataclasses import dataclass
from typing import Mapping

SOURCE = "https://nap.nationalacademies.org/catalog/26421/premium-cigars-patterns-of-use-marketing-and-health-effects"
BRACKETS = ("in_poverty", "poverty_to_200pct", "above_200pct")
RATES = {
    "premium": {"in_poverty": .004, "poverty_to_200pct": .005, "above_200pct": .013},
    "nonpremium": {"in_poverty": .054, "poverty_to_200pct": .040, "above_200pct": .023},
}

@dataclass(frozen=True)
class CigarDemandEstimate:
    adults: int
    premium_users: float
    nonpremium_users: float
    premium_prevalence: float
    nonpremium_prevalence: float
    status: str = "historical_unvalidated_prevalence_scenario"
    source: str = SOURCE

def estimate_cigar_demand(adults_by_poverty_ratio: Mapping[str, int]) -> CigarDemandEstimate:
    if set(adults_by_poverty_ratio) != set(BRACKETS):
        raise ValueError("All three poverty-ratio adult-population brackets required")
    if any(type(v) is not int or v < 0 for v in adults_by_poverty_ratio.values()):
        raise ValueError("Counts must be nonnegative integers")
    total = sum(adults_by_poverty_ratio.values())
    if total == 0:
        raise ValueError("Adult population must be positive")
    premium = sum(adults_by_poverty_ratio[k]*RATES["premium"][k] for k in BRACKETS)
    nonpremium = sum(adults_by_poverty_ratio[k]*RATES["nonpremium"][k] for k in BRACKETS)
    return CigarDemandEstimate(total,premium,nonpremium,premium/total,nonpremium/total)
