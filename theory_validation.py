"""Test observable traffic-vs-ticket theory without fitting predictions to sales.

Uses user-reported sales and tickets ONLY as evaluation targets, never as
location features. This tests the decomposition, not predictive accuracy.
"""
import csv
import json
from pathlib import Path
from location_sales_model import DAYS_PER_MONTH

ROOT=Path(__file__).resolve().parent
TICKETS={"Zimmerman Tobacco":{"ticket":29.0,"status":"user_reported"},
         "Litchfield Tobacco":{"ticket":None,"status":"derived_from_gross_and_pos_transactions"}}

def analyze(rows):
    by_name={r["store"]:r for r in rows}
    results=[]
    for name, meta in TICKETS.items():
        r=by_name[name]
        low=float(r["monthly_gross_low_usd"])
        high=float(r["monthly_gross_high_usd"])
        midpoint=(low+high)/2
        transactions=int(r["transactions_month"]) if name=="Litchfield Tobacco" else None
        ticket=meta["ticket"] if meta["ticket"] is not None else midpoint/transactions
        derived_transactions=midpoint/ticket
        results.append({
            "store":name,"gross_midpoint_usd":midpoint,
            "gross_range_usd":[low,high],
            "average_ticket_usd":round(ticket,2),
            "ticket_source":meta["status"],
            "transactions_month":round(derived_transactions),
            "transactions_per_day":round(derived_transactions/DAYS_PER_MONTH,1),
            "transaction_count_status":"observed_pos" if transactions is not None else "derived_from_sales_and_ticket",
            "transactions_per_day_range":[round(low/ticket/DAYS_PER_MONTH,1),round(high/ticket/DAYS_PER_MONTH,1)],
        })
    z,l=results
    sales_ratio=z["gross_midpoint_usd"]/l["gross_midpoint_usd"]
    ticket_ratio=z["average_ticket_usd"]/l["average_ticket_usd"]
    traffic_ratio=(z["gross_midpoint_usd"]/z["average_ticket_usd"])/(l["gross_midpoint_usd"]/l["average_ticket_usd"])
    return {"hypothesis":"Zimmerman higher revenue is primarily transaction volume rather than ticket size",
            "sales_ratio":round(sales_ratio,3),"ticket_ratio":round(ticket_ratio,3),
            "transaction_ratio":round(traffic_ratio,3),
            "transaction_share_of_log_sales_gap":None,
            "hypothesis_supported_by_reported_sales_and_tickets":traffic_ratio>ticket_ratio and traffic_ratio>1,
            "independent_location_model_prediction":None,
            "predictive_accuracy":None,
            "remaining_unmeasured":["catchment 21+","frontage AADT","site accessibility","actual competitor capture","customer frequency","Zimmerman observed POS transactions"],
            "warning":"Descriptive decomposition only; no independent prediction or verified location-causality test.",
            "stores":results}

def main():
    with (ROOT/"data"/"store_sales_comparables.csv").open(newline="",encoding="utf-8") as f:
        result=analyze(list(csv.DictReader(f)))
    path=ROOT/"data"/"theory_validation.json"
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="stores"},indent=2))
    for store in result["stores"]:
        print(store["store"],store["transactions_per_day"],"daily transactions")

if __name__=="__main__":
    main()
