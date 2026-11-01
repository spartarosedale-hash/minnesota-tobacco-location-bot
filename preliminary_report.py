"""Honest preliminary address report from user-supplied comparable-store revenue.
Run: python preliminary_report.py "123 Main St, City, MN" --rent 1500 --sqft 1200
No trained location model: estimates are comparable-store benchmarks, not site forecasts.
"""
import argparse,csv,json,statistics
from pathlib import Path

DATA=Path(__file__).with_name("reported_store_sales_2026_10_31.csv")

def benchmark(address, rent=None, sqft=None, data=DATA):
    if not address.strip():
        raise ValueError("Address is required")
    with open(data,encoding="utf-8-sig",newline="") as file:
        rows=list(csv.DictReader(file))
    pool=[]
    for r in rows:
        if r.get("role")!="training":continue
        try:
            low=float(r["monthly_sales_low"]);high=float(r["monthly_sales_high"])
            if low<=0 or high<low:continue
            store_rent=float(r["monthly_rent_usd"]) if r.get("monthly_rent_usd") else None
            store_size=float(r["store_sqft"]) if r.get("store_sqft") else None
        except ValueError:continue
        pool.append({"name":r["store_name"],"low":low,"high":high,"rent":store_rent,"sqft":store_size})
    if len(pool)<3:raise ValueError("At least three independent comparison stores required")
    selected=pool
    # Only filter on independently supplied property facts, never inferred rent.
    if sqft is not None:
        candidates=[p for p in selected if p["sqft"] is not None and abs(p["sqft"]-sqft)<=max(250,.25*sqft)]
        if len(candidates)>=3:selected=candidates
    if rent is not None:
        candidates=[p for p in selected if p["rent"] is not None and abs(p["rent"]-rent)<=max(500,.35*rent)]
        if len(candidates)>=3:selected=candidates
    midpoints=[(p["low"]+p["high"])/2 for p in selected]
    low=min(p["low"] for p in selected)
    high=max(p["high"] for p in selected)
    return {
        "address_input":address,
        "status":"PRELIMINARY_COMPARABLE_BENCHMARK_NOT_LOCATION_FORECAST",
        "monthly_sales_usd":{"comparison_low":round(low),"comparison_median":round(statistics.median(midpoints)),"comparison_high":round(high)},
        "comparable_stores":[p["name"] for p in selected],
        "training_stores_excluded":["Litchfield Tobacco","Zimmerman Tobacco"],
        "confidence":"INSUFFICIENT_FOR_SITE_PREDICTION",
        "inputs":{"rent_usd":rent,"square_feet":sqft},
        "explanation":"Sales distribution of independently reported comparable stores; address is not yet used to adjust revenue. Do not use for investment decisions."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("address")
    p.add_argument("--rent",type=float)
    p.add_argument("--sqft",type=float)
    a=p.parse_args()
    print(json.dumps(benchmark(a.address,a.rent,a.sqft),indent=2))
