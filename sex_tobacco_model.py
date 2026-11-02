"""2024 NHIS sex-stratified tobacco-use research features.

Source: Agaku et al., NEJM Evidence, Tobacco Product Use among U.S.
Adults, 2023-2024, Table 1. DOI:10.1056/EVIDpha2500339.
https://evidence.nejm.org/doi/full/10.1056/EVIDpha2500339

These are US adult sex-specific marginal prevalence rates, not local
Minnesota rates, not joint age-income-sex rates, and not sales forecasts.
Cigar estimate is ALL cigars, not premium-only. Smokeless excludes a
separate nicotine-pouch demand estimate. Product populations overlap.
Do not multiply these rates by income-specific or age-specific rates.
"""
from dataclasses import dataclass

SOURCE = "https://evidence.nejm.org/doi/full/10.1056/EVIDpha2500339"
YEAR = 2024
SEX_RATES = {
    "male": {"cigarettes": .115, "vaping": .077, "cigars_all": .065, "smokeless": .049},
    "female": {"cigarettes": .084, "vaping": .064, "cigars_all": .010, "smokeless": .004},
}

@dataclass(frozen=True)
class SexDemandEstimate:
    adults_included: int
    product_users: dict[str, float]
    source: str = SOURCE
    source_year: int = YEAR
    status: str = "national_marginal_research_feature_not_sales_forecast"

def estimate_by_sex(adults_by_sex: dict[str, int]) -> SexDemandEstimate:
    """Only binary categories published in the cited NHIS table are supported.

    Do not force an unknown/nonbinary population into either category; report
    adults_included and handle uncovered adults separately upstream.
    """
    if set(adults_by_sex) != {"male", "female"}:
        raise ValueError("Provide male and female adult counts explicitly")
    if any(type(n) is not int or n < 0 for n in adults_by_sex.values()):
        raise ValueError("Adult counts must be nonnegative integers")
    total = sum(adults_by_sex.values())
    if not total:
        raise ValueError("At least one adult required")
    products = SEX_RATES["male"].keys()
    estimates = {product: sum(adults_by_sex[sex]*SEX_RATES[sex][product]
                              for sex in SEX_RATES) for product in products}
    return SexDemandEstimate(total, estimates)
