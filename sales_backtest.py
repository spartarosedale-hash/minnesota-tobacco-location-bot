"""Transparent leave-one-store-out baseline; NOT a location-aware sales model.

Sales are excluded from a held-out store's training set. This baseline is
intentionally simple and is reported alongside missing location-feature status.
"""
import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_comparables(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    records = []
    for row in rows:
        low = float(row["monthly_gross_low_usd"])
        high = float(row["monthly_gross_high_usd"])
        if low < 0 or high < low:
            raise ValueError("Invalid monthly sales range for " + row["store"])
        if row["source_status"] == "user_estimate":
            continue  # Not observed sales: don't train or validate against estimates.
        records.append({"store": row["store"], "city": row["city"],
                        "low": low, "high": high,
                        "mid": (low + high) / 2,
                        "source_status": row["source_status"]})
    return records

def leave_one_out(records):
    results = []
    for heldout in records:
        train = [r["mid"] for r in records if r["store"] != heldout["store"]]
        if not train:
            continue
        prediction = statistics.median(train)
        actual_mid = heldout["mid"]
        results.append({
            "store": heldout["store"], "city": heldout["city"],
            "prediction_monthly_usd": round(prediction),
            "observed_monthly_low_usd": heldout["low"],
            "observed_monthly_high_usd": heldout["high"],
            "observed_midpoint_usd": actual_mid,
            "midpoint_absolute_percentage_error": round(abs(prediction - actual_mid) / actual_mid * 100, 2) if actual_mid else None,
            "error_method": "leave-one-store-out median of other user-reported stores",
            "location_features_used": False,
        })
    return results

def main():
    records = load_comparables(ROOT / "data" / "store_sales_comparables.csv")
    results = leave_one_out(records)
    errors = [r["midpoint_absolute_percentage_error"] for r in results if r["midpoint_absolute_percentage_error"] is not None]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "leave-one-store-out sales-only median baseline",
        "limitations": [
            "This is a benchmark, not a traffic/demographic/competition-aware forecast.",
            "Monthly figures are user-reported and may cover different months.",
            "The midpoint of a sales range is a convenience, not an observed exact value.",
            "User estimates are excluded; no sales from the held-out store enter its prediction.",
            "No verified road counts, drive-time catchments, store age, or traffic-capture measurements are in the model.",
        ],
        "training_store_count": len(records),
        "mean_absolute_percentage_error": round(statistics.mean(errors), 2) if errors else None,
        "results": results,
        "location_model_accuracy": None,
        "location_model_status": "not trained: sourced feature matrix unavailable",
    }
    output = ROOT / "data" / "sales_backtest.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Baseline stores:", len(records), "LOO MAPE:", report["mean_absolute_percentage_error"])
    for r in results:
        print(r["store"], "prediction:", r["prediction_monthly_usd"], "actual midpoint:", r["observed_midpoint_usd"], "error:", r["midpoint_absolute_percentage_error"])

if __name__ == "__main__":
    main()
