"""Sourced demographic tobacco-demand features, not retail sales predictions.

Age-adjusted smoking and race-specific vaping are independent survey marginals.
Do not multiply age and race prevalence: that would invent joint probabilities.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "tobacco_usage_statistics.json"

def estimate_vape_users_by_age(age_21_plus, stats=None):
    """Return expected current users from disjoint age counts; national 2023 rates."""
    stats = stats or json.loads(DATA.read_text(encoding="utf-8"))
    rates = stats["vape_current_use_percent_by_age_2023"]
    missing = [k for k in rates if k not in age_21_plus or age_21_plus[k] is None]
    if missing:
        return {"status":"missing_age_bins","missing":missing,"estimated_users":None}
    if any(age_21_plus[k] < 0 for k in rates):
        raise ValueError("Age counts must be nonnegative")
    total = sum(age_21_plus[k] for k in rates)
    users = sum(age_21_plus[k]*rates[k]/100 for k in rates)
    return {"status":"national_prevalence_scenario","population_21_plus":total,
            "estimated_users":round(users,1),
            "weighted_prevalence_percent":round(100*users/total,2) if total else None,
            "warning":"Survey-based expected users, NOT store customers, visits or revenue; age 21+ catchment population required."}

def summarize_market(age_21_plus=None, median_household_income=None, race_21_plus=None):
    stats = json.loads(DATA.read_text(encoding="utf-8"))
    output = {"source_year":2023,
              "income_source":"ACS 2024 5-year B19013_001E",
              "median_household_income_usd":median_household_income,
              "income_multiplier":None,
              "race_prevalence_reference_percent":stats["vape_current_use_percent_by_race_2023"],
              "smoking_race_prevalence_reference_percent":stats["cigarette_current_smoking_age_adjusted_percent_by_race_2023"],
              "race_21_plus_available":race_21_plus is not None,
              "cigarette_users_estimate":None,
              "vape_users_by_age":estimate_vape_users_by_age(age_21_plus,stats) if age_21_plus is not None else {"status":"missing_age_bins","estimated_users":None},
              "purchase_frequency_verified":False,
              "status":"research_features_only_not_revenue_prediction"}
    if median_household_income is not None and median_household_income < 0:
        raise ValueError("Median income must be nonnegative")
    return output
