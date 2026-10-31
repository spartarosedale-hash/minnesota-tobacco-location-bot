"""Phase-one store prediction input validation. Run: python store_predictor.py"""
import csv
from pathlib import Path

AGE_GROUPS = ["21_24", "25_34", "35_44", "45_54", "55_64", "65_plus"]
ROOT = Path(__file__).resolve().parent

def evaluate(row):
    required = ["store_id", "store_name", "city", "address", "population_21_plus"]
    missing = [field for field in required if not (row.get(field) or "").strip()]
    if not missing:
        try:
            adult = float(row["population_21_plus"])
            if adult < 0:
                missing.append("population_21_plus")
            age_values = [float(row["population_" + age]) for age in AGE_GROUPS if (row.get("population_" + age) or "").strip()]
            if len(age_values) == len(AGE_GROUPS) and abs(sum(age_values) - adult) > max(5, adult * .02):
                missing.append("age_population_mismatch")
            for age in AGE_GROUPS:
                m, f, t = (row.get("male_" + age) or "").strip(), (row.get("female_" + age) or "").strip(), (row.get("population_" + age) or "").strip()
                if m and f and t and abs(float(m) + float(f) - float(t)) > 2:
                    missing.append("gender_age_mismatch_" + age)
        except ValueError:
            missing.append("invalid_demographics")
    return {
        "store_id": row.get("store_id", ""),
        "store_name": row.get("store_name", ""),
        "status": "needs_data" if missing else "needs_calibration",
        "missing_fields": ";".join(missing),
        "estimated_monthly_sales": "",
        "confidence": "insufficient",
        "notes": "No calibrated sales model yet. Popular Times graphs are relative to each store peak, not absolute traffic."
    }

def main():
    with (ROOT / "stores.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    results = [evaluate(row) for row in rows]
    out = ROOT / "data" / "store_predictions.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]) if results else ["store_id", "status"])
        writer.writeheader()
        writer.writerows(results)
    for r in results:
        print(f'{r["store_name"]}: {r["status"]} ({r["missing_fields"]})')
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
