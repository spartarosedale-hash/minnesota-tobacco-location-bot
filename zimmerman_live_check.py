"""Run a real, free-source Zimmerman site check; never invent unavailable measurements."""
import datetime,json,traceback
from site_report import build
ADDRESS="26219 Fremont Dr Ste 101, Zimmerman, MN 55398"
def main():
    result={"address":ADDRESS,"checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "data_policy":"free public sources only; no paid API calls"}
    try:
        report=build(ADDRESS)
        result["status"]="report_generated"
        result["report"]=report
        result["source_status"]={k:(v.get("status","returned") if isinstance(v,dict) else "returned") for k,v in report.items() if k in ("traffic","competition","free_nearby_places","google_popular_times","nearby_busyness")}
        result["forecast_validation"]="UNVALIDATED; do not use as verified revenue prediction"
    except Exception as exc:
        result["status"]="blocked"
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:500]
        result["forecast_validation"]="NO LIVE FORECAST GENERATED"
    with open("zimmerman_live_report.json","w",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
    if result["status"]!="report_generated":raise SystemExit(1)
if __name__=="__main__":main()
