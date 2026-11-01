"""Evidence-only store comparison; no model fitting or causal attribution."""
import argparse
import csv
import json
from pathlib import Path

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def build_report(training, validation, demographics, traffic):
    d = {row["store"]: row for row in demographics.get("results", [])}
    rows = []
    for role, items in (("training", training), ("holdout", validation)):
        for item in items:
            name = item["store_name"]
            low, high = number(item.get("monthly_sales_low")), number(item.get("monthly_sales_high"))
            if low is None or high is None or low <= 0 or high < low:
                continue
            census = d.get(name, {})
            road = traffic.get(name, {})
            midpoint = (low + high) / 2
            row = {
                "store": name, "role": role,
                "monthly_sales_low": low, "monthly_sales_high": high,
                "monthly_sales_midpoint": midpoint,
                "annualized_sales_midpoint": midpoint * 12,
                "rent_to_sales_percent": None,
                "sales_per_square_foot_monthly": None,
                "adult_21_plus_tract": None,
                "median_household_income_tract": None,
                "age_groups_tract": None,
                "income_brackets_tract": None,
                "traffic_candidate_count": len(road.get("candidate_segments") or []),
                "verified_frontage_aadt": None,
                "data_gaps": []
            }
            rent, size = number(item.get("monthly_rent")), number(item.get("square_feet"))
            if rent and rent > 0:
                row["rent_to_sales_percent"] = round(100 * rent / midpoint, 1)
            else:
                row["data_gaps"].append("monthly_rent_missing")
            if size and size > 0:
                row["sales_per_square_foot_monthly"] = round(midpoint / size, 2)
            else:
                row["data_gaps"].append("store_size_missing")
            if census.get("status") == "ok":
                row["adult_21_plus_tract"] = census.get("age_21_plus_tract")
                row["median_household_income_tract"] = census.get("median_household_income_tract")
                row["age_groups_tract"] = census.get("age_groups_tract")
                row["income_brackets_tract"] = census.get("household_income_brackets_tract")
            else:
                row["data_gaps"].append("census_tract_evidence_missing")
            if road.get("frontage_segment_verified") is not True:
                row["data_gaps"].append("frontage_aadt_unverified")
            row["data_gaps"].extend(["drive_time_population_missing", "competitor_count_unverified", "transaction_count_missing", "average_ticket_missing"])
            rows.append(row)
    rows.sort(key=lambda row: row["monthly_sales_midpoint"], reverse=True)
    holdouts = [r for r in rows if r["role"] == "holdout"]
    return {
        "purpose": "Descriptive comparisons only; not causal findings or a trained sales model",
        "store_count": len(rows), "training_store_count": len(rows)-len(holdouts),
        "holdout_store_count": len(holdouts), "stores": rows,
        "interpretation_rules": [
            "Do not use holdout sales to fit coefficients or tune forecasts",
            "Census tract statistics are not drive-time trade-area statistics",
            "Nearby road segments are not verified storefront AADT",
            "Race and ethnicity are descriptive fairness-audit data, not sales-prediction inputs",
            "Correlations with small observational samples do not establish causation"
        ]
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--training", default="training_comparables.csv")
    p.add_argument("--validation", default="validation_results.csv")
    p.add_argument("--demographics", default="research_demographics.json")
    p.add_argument("--traffic", default="research_traffic.json")
    p.add_argument("--output", default="store_comparison_report.json")
    args = p.parse_args()
    with open(args.demographics, encoding="utf-8") as f: demographics = json.load(f)
    with open(args.traffic, encoding="utf-8") as f: traffic = json.load(f)
    report = build_report(read_csv(args.training), read_csv(args.validation), demographics, traffic)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"store_count": report["store_count"], "training_store_count": report["training_store_count"], "holdout_store_count": report["holdout_store_count"]}, indent=2))

if __name__ == "__main__":
    main()
