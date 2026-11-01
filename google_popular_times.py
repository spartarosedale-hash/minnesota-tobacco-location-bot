"""Analyze user-observed Google Maps Popular times bars without scraping Google.

Input CSV columns: business_name,day,hour,relative_popularity,source_url,observed_date
day: Monday..Sunday; hour: 0..23; relative_popularity: 0..100.
Google charts normalize each business to its own peak. Never compare these as
absolute visitor volumes or use them as observed customer counts.
"""
import csv,collections,json
DAYS=("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
def analyze(path):
    groups=collections.defaultdict(list)
    with open(path,newline="",encoding="utf-8-sig") as f:
        for n,row in enumerate(csv.DictReader(f),start=2):
            name=row.get("business_name","").strip()
            day=row.get("day","").strip().title()
            try: hour=int(row.get("hour",""));value=float(row.get("relative_popularity",""))
            except (ValueError,TypeError):raise ValueError(f"Invalid chart value on line {n}")
            if not name or day not in DAYS or hour not in range(24) or not 0<=value<=100:
                raise ValueError(f"Invalid chart observation on line {n}")
            if not row.get("source_url","").startswith("https://www.google.com/maps/") and not row.get("source_url","").startswith("https://maps.app.goo.gl/"):
                raise ValueError(f"Google Maps source URL required on line {n}")
            if not row.get("observed_date","").strip():raise ValueError(f"Observation date required on line {n}")
            groups[name].append({"day":day,"hour":hour,"relative_popularity":value})
    result={}
    for name,observations in groups.items():
        unique={(o["day"],o["hour"]) for o in observations}
        if len(unique)!=len(observations):raise ValueError("Duplicate business/day/hour: "+name)
        busiest=max(observations,key=lambda o:o["relative_popularity"])
        daily={day:round(sum(o["relative_popularity"] for o in observations if o["day"]==day)/max(1,sum(o["day"]==day for o in observations)),1) for day in DAYS if any(o["day"]==day for o in observations)}
        result[name]={"observations":len(observations),"coverage_hours_of_168":len(unique),
                      "busiest_observed":busiest,"daily_relative_average":daily,
                      "observed_mean_relative":round(sum(o["relative_popularity"] for o in observations)/len(observations),1),
                      "measured_visitors":None}
    return {"status":"observed_relative_busyness","businesses":result,
            "warning":"Google Popular times are relative to each business's own weekly peak, not absolute visitors. Do not compare relative values as customer volumes across stores. Incomplete observations bias averages."}
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("csv_file")
    a=p.parse_args()
    print(json.dumps(analyze(a.csv_file),indent=2))
