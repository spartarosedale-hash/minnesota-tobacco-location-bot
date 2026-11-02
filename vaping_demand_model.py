"""Research benchmarks for adult vaping demand; NOT a calibrated sales predictor.

Sources:
- 2024 MN adult vaping prevalence 7.1%: https://truthinitiative.org/research-resources/smoking-region/tobacco-use-minnesota-2026
- US adult e-cigarette users 2023 average monthly spend $82.22:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12280165/
- Daily use 70.17% in separate sample of 771 adult vapers:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC13289341/

Do not infer a spending-by-income curve from these studies. Survey expenditures
are across channels and do not establish revenue captured by a single store.
"""
from dataclasses import dataclass

MN_VAPING_PREVALENCE_2024 = 0.071
US_MONTHLY_VAPE_SPEND_2023 = 82.22

@dataclass(frozen=True)
class VapingDemandScenario:
    estimated_adult_vapers: float
    total_market_spend_benchmark: float
    store_revenue_scenario: float | None
    status: str = "unvalidated_research_scenario"

def estimate_vaping_scenario(adult_population: int, prevalence: float = MN_VAPING_PREVALENCE_2024,
                             monthly_spend: float = US_MONTHLY_VAPE_SPEND_2023,
                             store_capture_share: float | None = None) -> VapingDemandScenario:
    """Calculate a transparent scenario, not a forecast.

    Capture share must be explicitly supplied from real observed data; if
    absent, no store revenue estimate is returned.
    """
    if type(adult_population) is not int or adult_population < 0:
        raise ValueError("adult_population must be a nonnegative integer")
    if not (0 <= prevalence <= 1) or not (0 <= monthly_spend):
        raise ValueError("Invalid prevalence or spending")
    if store_capture_share is not None and not (0 <= store_capture_share <= 1):
        raise ValueError("Capture share must be between 0 and 1")
    vapers = adult_population * prevalence
    spend = vapers * monthly_spend
    revenue = None if store_capture_share is None else spend * store_capture_share
    return VapingDemandScenario(vapers, spend, revenue)
