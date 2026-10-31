"""Address-first sales estimate CLI. Baseline from user-reported comparable stores.
Not a trained geographic model: geographic factors are not yet available.
Run: python location_estimate.py --address "123 Main St, Minnesota"
"""
import argparse, csv, json, math
from pathlib import Path

DATA = Path(__file__).with_name("training_comparables.csv")

def read_comparables(path=DATA):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        try:
            low, high = float(r["monthly_sales_low"]), float(r["monthly_sales_high"])
            rent, area = float(r["monthly_rent"]), float(r["square_feet"])
            if not (0 < low <= high and rent > 0 and area > 0):
                continue
            out.append({"name":r["store_name"], "city":r["city"], "address":r["exact_address"],
                        "low":low, "high":high, "mid":(low+high)/2,
                        "rent":rent, "area":area})
        except (ValueError, TypeError, KeyError):
            continue
    return out

def predict(address, size, rent, comparables):
    if not address.strip() or size <= 0 or rent <= 0:
        raise ValueError("Address, size, and monthly rent must be supplied")
    # Intentionally exclude exact address matches to prevent target leakage.
    rows = [r for r in comparables if r["address"].strip().casefold() != address.strip().casefold()]
    if len(rows) < 3:
        raise ValueError("Need at least 3 other comparables")
    # Nonparametric baseline: scale each comparable by store area.
    # Cap area adjustment to avoid extrapolating wildly.
    projections = sorted(r["mid"] * min(1.5, max(0.67, size/r["area"])) for r in rows)
    mid = len(projections)//2
    baseline = (projections[mid] if len(projections)%2 else
                (projections[mid-1]+projections[mid])/2)
    return {"address":address,"square_feet":size,"monthly_rent":rent,
            "monthly_sales_low":round(projections[0],-2),
            "monthly_sales_base":round(baseline,-2),
            "monthly_sales_high":round(projections[-1],-2),
            "comparable_count":len(rows),
            "method":"Comparable-store baseline; size-adjusted; not location-calibrated",
            "confidence":"insufficient evidence",
            "missing_features":["verified 21+ trade-area population","competitor density",
                                "road traffic","visibility/access","store age",
                                "product mix","verified historical sales"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--address",required=True)
    p.add_argument("--size",type=float,default=1200)
    p.add_argument("--rent",type=float,required=True)
    a=p.parse_args()
    print(json.dumps(predict(a.address,a.size,a.rent,read_comparables()),indent=2))

if __name__=="__main__":
    main()
