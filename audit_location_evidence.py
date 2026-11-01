"""Audit collected evidence and compare frozen pre-actual forecasts with holdouts.

Never use holdout actual sales to fit coefficients. Nearby MnDOT road segments
are candidates, not verified frontage counts. Census tracts are not drive-time
catchments. Output JSON contains no new location-calibrated prediction.
"""
import argparse
import csv
import json
from pathlib import Path

def audit(demographics, traffic, validation_csv):
    d = {r["store"]: r for r in demographics.get("results", [])}
    t = traffic
    names = sorted(set(d) | set(t))
    stores = []
    for name in names:
        census = d.get(name, {})
        roads = t.get(name, {})
        candidates = roads.get("candidate_segments", [])
        verified = roads.get("frontage_segment_verified") is True
        stores.append({
            "store": name,
            "census_status": census.get("status", "missing"),
            "census_geography": "tract_not_drive_time",
            "adult_21_plus_tract": census.get("age_21_plus_tract") if census.get("status") == "ok" else None,
            "median_household_income_tract": census.get("median_household_income_tract") if census.get("status") == "ok" else None,
            "traffic_status": roads.get("status", "missing"),
            "nearby_segment_count": len(candidates),
            "frontage_aadt": None,
            "frontage_verified": verified,
            "traffic_note": "Nearby candidates only; no verified frontage AADT",
        })
    holdouts = []
    with open(validation_csv, newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            try:
                actual = float(r["actual_midpoint"])
                prior = float(r["prior_estimate"])
                if actual <= 0:
                    continue
                holdouts.append({"store": r["store_name"], "actual_midpoint": actual,
                    "frozen_prior_estimate": prior,
                    "absolute_percentage_error": round(100 * abs(prior - actual) / actual, 1),
                    "role": "holdout_only"})
            except (ValueError, TypeError):
                continue
    mape = round(sum(x["absolute_percentage_error"] for x in holdouts) / len(holdouts), 1) if holdouts else None
    return {"stores": stores, "holdout_validation": holdouts,
            "holdout_mape_percent": mape, "holdout_count": len(holdouts),
            "model_status": "not_retrained",
            "prediction_status": "not_location_calibrated",
            "caveats": ["No target leakage from validation sales",
                "No verified frontage traffic counts",
                "Tract demographics are not drive-time demographics",
                "A successful API call does not guarantee useful candidate segments"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demographics", default="research_demographics.json")
    p.add_argument("--traffic", default="research_traffic.json")
    p.add_argument("--validation", default="validation_results.csv")
    p.add_argument("--output", default="location_evidence_audit.json")
    args = p.parse_args()
    with open(args.demographics, encoding="utf-8") as f: d = json.load(f)
    with open(args.traffic, encoding="utf-8") as f: t = json.load(f)
    result = audit(d, t, args.validation)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"stores": len(result["stores"]),
                      "holdout_count": result["holdout_count"],
                      "holdout_mape_percent": result["holdout_mape_percent"],
                      "model_status": result["model_status"]}, indent=2))

if __name__ == "__main__":
    main()
