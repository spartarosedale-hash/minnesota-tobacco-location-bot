"""Feature registry and evidence-quality checks for retail-location research.

No fitted coefficients: this module defines measurable variables and rejects
missing, stale, or unsupported data rather than making up values.
"""
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Feature:
    name: str
    group: str
    source: str
    unit: str
    importance_hypothesis: str

FEATURES = [
    Feature("adult_21_plus_10min", "demographics", "ACS + drive-time overlay", "people", "reachable adult customer base"),
    Feature("adult_21_plus_15min", "demographics", "ACS + drive-time overlay", "people", "broader customer catchment"),
    Feature("household_income_10min", "demographics", "ACS + drive-time overlay", "USD", "purchasing power"),
    Feature("population_growth_5yr", "demographics", "ACS", "percent", "growing demand"),
    Feature("daytime_worker_population", "commuting", "Census LEHD/LODES", "people", "nonresident daytime customers"),
    Feature("commuter_vehicle_share", "commuting", "ACS B08301", "percent", "drive-by trip propensity"),
    Feature("aadt_frontage", "traffic", "MnDOT traffic segments", "vehicles/day", "passing exposure"),
    Feature("aadt_count_year", "traffic", "MnDOT traffic segments", "year", "measurement recency"),
    Feature("summer_weekend_traffic_index", "traffic", "MnDOT hourly/continuous counts", "ratio", "recreational travel"),
    Feature("friday_northbound_volume", "traffic", "MnDOT directional counts if available", "vehicles", "cabin traffic"),
    Feature("highway_visibility", "access", "field or street imagery audit", "yes/no", "storefront discovery"),
    Feature("easy_northbound_entry", "access", "road access audit", "yes/no", "traveler capture"),
    Feature("left_turn_restriction", "access", "road access audit", "yes/no", "conversion barrier"),
    Feature("parking_capacity", "access", "site plan / field audit", "spaces", "stop convenience"),
    Feature("gas_station_same_stop", "anchors", "verified parcel/business inspection", "yes/no", "trip chaining"),
    Feature("liquor_store_adjacent", "anchors", "verified parcel/business inspection", "yes/no", "trip chaining"),
    Feature("grocery_anchor_5min", "anchors", "verified business listings", "count", "regular shopping traffic"),
    Feature("competitors_10min", "competition", "verified licensing and business listings", "count", "substitute availability"),
    Feature("nearest_competitor_drive_min", "competition", "road routing", "minutes", "competitive separation"),
    Feature("competitor_open_hours_overlap", "competition", "verified store hours", "hours/week", "substitute accessibility"),
    Feature("recreation_destinations_60min", "seasonality", "state parks / lakes / campgrounds", "count", "leisure corridor"),
    Feature("seasonal_traffic_ratio", "seasonality", "MnDOT continuous counts", "ratio", "summer demand"),
    Feature("weekly_open_hours", "operations", "store schedule", "hours/week", "sales opportunity"),
    Feature("store_age_months", "operations", "license/opening history", "months", "customer awareness"),
    Feature("category_mix", "operations", "owner POS data", "category shares", "assortment differences"),
    Feature("transactions_per_day", "operations", "owner POS data", "transactions", "traffic conversion"),
    Feature("average_ticket", "operations", "owner POS data", "USD", "revenue per customer"),
]
VALID_STATUS = {"verified", "owner_reported", "estimated", "unknown"}

def validate_observation(observation, as_of=None):
    """Return reasons a measurement should not be treated as independently verified."""
    as_of = as_of or date.today()
    issues = []
    if observation.get("status") not in VALID_STATUS:
        issues.append("invalid_status")
    if observation.get("value") is None:
        issues.append("missing_value")
    if observation.get("status") == "verified" and not observation.get("source_url"):
        issues.append("missing_source")
    observed = observation.get("observed_date")
    if observed:
        try:
            observed_date = date.fromisoformat(observed)
            if observed_date > as_of:
                issues.append("future_observation")
        except ValueError:
            issues.append("invalid_date")
    else:
        issues.append("missing_observed_date")
    return issues

def coverage(observations):
    names = {f.name for f in FEATURES}
    verified = {key for key, item in observations.items()
                if key in names and item.get("status") == "verified"
                and not validate_observation(item)}
    return {"verified": len(verified), "total": len(names),
            "missing_or_unverified": sorted(names - verified)}

if __name__ == "__main__":
    import json
    print(json.dumps({"feature_count": len(FEATURES),
                      "features": [f.__dict__ for f in FEATURES]}, indent=2))
