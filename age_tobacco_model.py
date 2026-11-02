"""2024 CDC NHIS age-specific cigarette and e-cigarette prevalence features.

Source: https://www.cdc.gov/nchs/data/hestat/hestat115.htm
NCHS Health E-Stat 115 (March 2026), 2024 survey Tables 1 and 2.
Rates are national, age-specific marginal estimates. They are NOT
income-sex-age joint probabilities. Do not multiply with income/sex rates.
Counts must be adults aged 18+; the bot must separately enforce 21+ retail
eligibility when translating prevalence to lawful addressable demand.
"""
from dataclasses import dataclass
from typing import Mapping

SOURCE = "https://www.cdc.gov/nchs/data/hestat/hestat115.htm"
SURVEY_YEAR = 2024
AGE_BANDS = ("18_24", "25_44", "45_64", "65_plus")
AGE_RATES = {
    "cigarettes": {"18_24": .034, "25_44": .105, "45_64": .133, "65_plus": .078},
    "vaping": {"18_24": .148, "25_44": .111, "45_64": .041, "65_plus": .010},
}
URBANIZATION_RATES = {
    "large_central_metro": {"cigarettes": .080, "vaping": .061},
    "large_fringe_metro": {"cigarettes": .080, "vaping": .067},
    "medium_small_metro": {"cigarettes": .110, "vaping": .073},
    "nonmetropolitan": {"cigarettes": .154, "vaping": .092},
}

@dataclass(frozen=True)
class AgeDemandEstimate:
    adults_18_plus: int
    estimated_users: dict[str, float]
    prevalence: dict[str, float]
    source: str = SOURCE
    survey_year: int = SURVEY_YEAR
    status: str = "unvalidated_national_age_prevalence_not_store_forecast"

def estimate_by_age(adults_by_age: Mapping[str, int]) -> AgeDemandEstimate:
    if set(adults_by_age) != set(AGE_BANDS):
        raise ValueError("Supply all four adult age bands")
    if any(type(v) is not int or v < 0 for v in adults_by_age.values()):
        raise ValueError("Counts must be nonnegative integers")
    total = sum(adults_by_age.values())
    if not total:
        raise ValueError("Total adult population must be positive")
    users = {product: sum(adults_by_age[age]*rates[age] for age in AGE_BANDS)
             for product, rates in AGE_RATES.items()}
    return AgeDemandEstimate(total, users, {k: v/total for k,v in users.items()})

def age_feature_report(adults_by_age: Mapping[str,int], *, age_18_20_count: int | None = None):
    """18-24 includes under-21 adults; don't imply all are eligible buyers."""
    estimate = estimate_by_age(adults_by_age)
    if age_18_20_count is not None:
        if type(age_18_20_count) is not int or not 0 <= age_18_20_count <= adults_by_age["18_24"]:
            raise ValueError("Invalid 18-20 count")
    return {"estimate": estimate, "retail_21_plus_eligible_population":
            None if age_18_20_count is None else estimate.adults_18_plus-age_18_20_count,
            "warning": "Prevalence estimates include ages 18-20; do not use directly as lawful 21+ buyers."}
