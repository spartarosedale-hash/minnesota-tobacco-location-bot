"""Evidence-first individual retail location investigation.

Usage: python location_investigation.py "Zimmerman Tobacco"
Produces a structured investigation from reported store facts; does not invent traffic counts
or assert that correlation establishes causation.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FEATURES = [
    ("highway_frontage_reported", "Traffic exposure", "Potential passing-customer awareness; verify traffic counts and actual storefront visibility"),
    ("near_gas_station", "Trip generator", "Potential convenience-store cross-shopping; verify location and shared access"),
    ("liquor_store_adjacency", "Adjacent retail", "Potential combined shopping trips; compare similar stores before assigning revenue impact"),
]
RESEARCH = [
    ("road_traffic", "MnDOT segment-specific annual average daily traffic and count year"),
    ("access", "Driveway entrances, median restrictions, parking, storefront visibility"),
    ("catchment", "Adult population and income in 5/10/15-minute drive-time areas"),
    ("competition", "Open tobacco shops and drive times within the trade area"),
    ("operations", "Store age, hours, pricing, product mix, and transaction counts"),
    ("seasonality", "Monthly retail sales by month and local seasonal visitor proxies"),
]

def investigate(store_name, path=ROOT / "validation_results.csv"):
    with open(path, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    row = next((r for r in rows if r["store_name"].casefold() == store_name.casefold()), None)
    if row is None:
        raise ValueError(f"Store not found in validation file: {store_name}")
    hypotheses = []
    for field, label, explanation in FEATURES:
        value = row.get(field, "").strip().lower()
        if value in {"yes", "adjacent"}:
            hypotheses.append({"factor": label, "status": "owner-reported", "hypothesis": explanation, "causal_effect_established": False})
    low = float(row["monthly_sales_low"])
    high = float(row["monthly_sales_high"])
    result = {
        "store": row["store_name"],
        "address": row["address"],
        "reported_typical_monthly_retail_sales": [low, high],
        "reported_summer_peak": float(row["summer_peak_monthly_sales"]) if row.get("summer_peak_monthly_sales") else None,
        "hypotheses_to_test": hypotheses,
        "research_gaps": [{"field": k, "verification_needed": v} for k, v in RESEARCH],
        "conclusion": "Location advantages are hypotheses, not proven revenue causes.",
        "training_data_leakage_policy": "Exclude validation-store sales from model fitting and feature selection decisions."
    }
    return result

if __name__ == "__main__":
    print(json.dumps(investigate(sys.argv[1] if len(sys.argv) > 1 else "Zimmerman Tobacco"), indent=2))
