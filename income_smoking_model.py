"""Research-backed cigarette demand feature for Minnesota location scoring.

NHIS 2020 household-income rates, Surgeon General 2024 Table 2.13.
Rates are national historical priors, not Minnesota-specific forecasts.
Inputs must be ADULT PERSON counts by their HOUSEHOLD income bracket,
not household counts. Never use these estimates as observed sales.
"""
from dataclasses import dataclass
from typing import Mapping

SOURCE = "https://www.ncbi.nlm.nih.gov/books/NBK614478/table/ch2.tab14/"
SOURCE_YEAR = 2020
INCOME_BRACKETS = ("under_35k", "35k_to_74999", "75k_to_99999", "100k_plus")
SMOKING_RATES = {"under_35k": 0.202, "35k_to_74999": 0.141,
                 "75k_to_99999": 0.105, "100k_plus": 0.062}

@dataclass(frozen=True)
class CigaretteDemandEstimate:
    adults: int
    estimated_smokers: float
    prevalence: float
    source: str = SOURCE
    source_year: int = SOURCE_YEAR

def estimate_cigarette_demand(adults_by_household_income: Mapping[str, int]) -> CigaretteDemandEstimate:
    """Estimate cigarette smoking population, conditional on complete adult counts.

    Reject missing buckets to avoid silently assuming zero. Reject household
    counts: caller must first obtain/estimate ADULTS distributed by household
    income (ideally ACS microdata), not multiply households by smoking rates.
    """
    if set(adults_by_household_income) != set(INCOME_BRACKETS):
        raise ValueError("Provide exactly all four household-income brackets")
    values = list(adults_by_household_income.values())
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError("Adult counts must be nonnegative integers")
    adults = sum(values)
    if adults == 0:
        raise ValueError("Adult population must be positive")
    smokers = sum(adults_by_household_income[k] * SMOKING_RATES[k] for k in INCOME_BRACKETS)
    return CigaretteDemandEstimate(adults, smokers, smokers / adults)

def compare_with_observed(estimated: CigaretteDemandEstimate, observed_monthly_cigarette_sales: float | None):
    """Return separate research estimate and observed store sales; no invented conversion."""
    if observed_monthly_cigarette_sales is not None and observed_monthly_cigarette_sales < 0:
        raise ValueError("Sales cannot be negative")
    return {"estimated_adult_smokers": round(estimated.estimated_smokers, 1),
            "estimated_smoking_prevalence": round(estimated.prevalence, 4),
            "observed_monthly_cigarette_sales": observed_monthly_cigarette_sales,
            "source": estimated.source, "source_year": estimated.source_year,
            "status": "unvalidated_prior_not_sales_forecast"}
