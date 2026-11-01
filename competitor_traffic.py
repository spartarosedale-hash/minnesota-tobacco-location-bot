"""Competitor visit-traffic signals with explicit evidence and reliability.
Input CSV: competitor_name,latitude,longitude,category,visits_per_month,source,measurement_period,confidence
Only measured absolute visits may enter numeric aggregation. Google Popular Times is
relative to each business's own peak and must NEVER be converted to visit counts.
"""
import csv, math
from traffic_and_competition import miles

ALLOWED_CONFIDENCE={"high","medium","low"}
RELATIVE_SOURCES={"google_popular_times","google_live_busyness","relative_busyness"}

def scan(lat,lon,path,radius_miles=3):
    stores=[]
    with open(path,newline="",encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            try:
                distance=miles(lat,lon,float(row["latitude"]),float(row["longitude"]))
            except (KeyError,TypeError,ValueError):
                continue
            if distance>radius_miles:continue
            source=row.get("source","").strip().lower()
            confidence=row.get("confidence","").strip().lower()
            visits=None
            if source not in RELATIVE_SOURCES and confidence in ALLOWED_CONFIDENCE:
                try:
                    value=float(row.get("visits_per_month",""))
                    if math.isfinite(value) and value>=0:visits=value
                except (TypeError,ValueError):pass
            stores.append({"name":row.get("competitor_name",""),"category":row.get("category",""),
                "distance_miles":round(distance,2),"source":source,"confidence":confidence or "unknown",
                "measured_monthly_visits":visits,
                "signal":"measured_absolute_visits" if visits is not None else "presence_only_unquantified"})
    measured=[x for x in stores if x["measured_monthly_visits"] is not None]
    return {"radius_miles":radius_miles,"nearby_stores":stores,"nearby_store_count":len(stores),
            "measured_store_count":len(measured),
            "measured_visits_sum":round(sum(x["measured_monthly_visits"] for x in measured)) if measured else None,
            "coverage":"partial" if len(measured)!=len(stores) else ("complete_for_supplied_stores" if stores else "none"),
            "warning":"Visits are across businesses and can double-count the same shoppers. Relative Google busyness is never treated as customer counts. Supplied list may be incomplete."}
