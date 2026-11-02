"""Smokeless tobacco demand scenarios: adult use, tins/week, and sales capture.

CDC 2021 adult smokeless prevalence 2.1% nationally (not Minnesota specific):
https://www.cdc.gov/tobacco/other-tobacco-products/smokeless-product-use-in-the-us.html
Clinical research on 182 selected smokeless users found 4.2 tins/week:
https://aacrjournals.org/cebp/article/16/8/1567/176896/
This is NOT a representative average for all users, income brackets, or Minnesota.
WHO advises measuring units/day and occasional users separately:
https://fctc.who.int/docs/librariesprovider12/default-document-library/who_fctc_indicator_compendium_first_edition.pdf

No observed income-specific consumption or prices are assumed. Provide
adult prevalence, tins/week, price and store capture explicitly for scenarios.
Traditional smokeless only; nicotine pouches must be modeled separately.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class SmokelessScenario:
    users: float
    monthly_tins_market: float | None
    monthly_market_dollars: float | None
    monthly_store_dollars: float | None
    status: str = "unvalidated_scenario_not_forecast"

def estimate_smokeless(adults: int, prevalence: float,
                       tins_per_week: float | None = None,
                       price_per_tin: float | None = None,
                       store_capture: float | None = None) -> SmokelessScenario:
    if type(adults) is not int or adults < 0 or not 0 <= prevalence <= 1:
        raise ValueError("Invalid adult count or prevalence")
    for name, val in (("tins_per_week", tins_per_week), ("price_per_tin", price_per_tin)):
        if val is not None and not 0 <= val < float("inf"):
            raise ValueError("Invalid " + name)
    if store_capture is not None and not 0 <= store_capture <= 1:
        raise ValueError("Capture must be in [0,1]")
    users = adults * prevalence
    tins = None if tins_per_week is None else users * tins_per_week * 52 / 12
    dollars = None if tins is None or price_per_tin is None else tins * price_per_tin
    store = None if dollars is None or store_capture is None else dollars * store_capture
    return SmokelessScenario(users, tins, dollars, store)
