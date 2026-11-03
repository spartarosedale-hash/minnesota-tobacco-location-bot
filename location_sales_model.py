"""Location-first monthly gross-sales model, restoring transactions/day x average ticket.

No target store sales are used to create predictions. Requires measured or
explicitly scenario-assumed inputs. This is not a trained accuracy claim.
"""
from dataclasses import dataclass
from typing import Optional
from demographic_demand import summarize_market

DAYS_PER_MONTH = 30.4375

@dataclass(frozen=True)
class SiteInputs:
    frontage_aadt: Optional[float] = None
    highway_aadt: Optional[float] = None
    frontage_capture_rate: Optional[float] = None
    highway_access_share: Optional[float] = None
    highway_capture_rate: Optional[float] = None
    local_21_plus: Optional[float] = None
    local_customer_penetration: Optional[float] = None
    local_visits_per_month: Optional[float] = None
    competition_retention: Optional[float] = None
    accessibility_factor: Optional[float] = None
    average_ticket: Optional[float] = None
    anchor_visits_per_day: float = 0.0
    age_21_plus_by_bin: Optional[dict] = None
    median_household_income_usd: Optional[float] = None
    race_21_plus_by_group: Optional[dict] = None

def predict_monthly_sales(x: SiteInputs):
    required = ("frontage_aadt", "frontage_capture_rate", "highway_aadt",
                "highway_access_share", "highway_capture_rate", "local_21_plus",
                "local_customer_penetration", "local_visits_per_month",
                "competition_retention", "accessibility_factor", "average_ticket")
    missing = [key for key in required if getattr(x, key) is None]
    if missing:
        return {"status": "insufficient_measured_inputs", "missing": missing,
                "monthly_gross_sales": None}
    if any(getattr(x, k) < 0 for k in required) or x.anchor_visits_per_day < 0:
        raise ValueError("Inputs must be nonnegative")
    for key in ("frontage_capture_rate", "highway_access_share",
                "highway_capture_rate", "local_customer_penetration",
                "competition_retention"):
        if getattr(x, key) > 1:
            raise ValueError(key + " must be <= 1")
    if x.accessibility_factor > 2:
        raise ValueError("accessibility_factor > 2 requires new model specification")
    # Capture is counted separately; highway traffic is discounted by access share.
    road_visits = x.frontage_aadt * x.frontage_capture_rate + (
        x.highway_aadt * x.highway_access_share * x.highway_capture_rate)
    repeat_visits = x.local_21_plus * x.local_customer_penetration * x.local_visits_per_month / DAYS_PER_MONTH
    visits = (road_visits + repeat_visits + x.anchor_visits_per_day) * x.competition_retention * x.accessibility_factor
    return {"status": "scenario_not_validated",
            "demographic_research": summarize_market(x.age_21_plus_by_bin, x.median_household_income_usd, x.race_21_plus_by_group),
            "daily_transactions": round(visits, 2),
            "average_ticket": x.average_ticket,
            "monthly_gross_sales": round(visits * x.average_ticket * DAYS_PER_MONTH),
            "components": {"frontage_daily": round(x.frontage_aadt*x.frontage_capture_rate,2),
                           "highway_daily": round(x.highway_aadt*x.highway_access_share*x.highway_capture_rate,2),
                           "local_repeat_daily": round(repeat_visits,2),
                           "anchor_daily": x.anchor_visits_per_day},
            "warning": "Assumed rates are not measured conversion; avoid double counting local and road customers."}
