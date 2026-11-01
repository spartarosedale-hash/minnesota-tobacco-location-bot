"""Source-backed local competitor registry, independent of Overpass availability."""
import csv
from pathlib import Path
import requests
from traffic_and_competition import miles

GEOCODER="https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
def registry_competitors(lat,lon,city,path="competitor_registry.csv",geocode=requests.get):
    matches=[]
    errors=[]
    rows=list(csv.DictReader(Path(path).open(encoding="utf-8-sig",newline="")))
    selected=[r for r in rows if r["city"].strip().casefold()==city.strip().casefold()]
    for row in selected:
        try:
            response=geocode(GEOCODER,params={"address":row["address"],"benchmark":"Public_AR_Current","vintage":"Current_Current","format":"json"},timeout=12)
            response.raise_for_status()
            found=response.json().get("result",{}).get("addressMatches",[])
            if not found:
                errors.append(row["name"]+": address not geocoded")
                continue
            coords=found[0]["coordinates"]
            distance=miles(lat,lon,float(coords["y"]),float(coords["x"]))
            if distance<=5:
                matches.append({"name":row["name"],"category":row["category"],"distance_miles":round(distance,2),
                                "address":row["address"],"source_url":row["source_url"],"source_date":row["source_date"],
                                "verification":row["verification"]})
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            errors.append(row["name"]+": "+str(exc)[:90])
    direct=[r for r in matches if r["category"]=="tobacco_shop"]
    rings={str(radius):sum(r["distance_miles"]<=radius for r in direct) for radius in (1,3,5)}
    return {"status":"partial" if errors else ("ok" if selected else "no_registry_for_city"),
            "source":"Sourced municipal-license candidates; Census address geocoding",
            "city":city,"source_records":len(selected),"geocoded_within_5_miles":len(matches),
            "direct_tobacco_shop_candidates_within_miles":rings,"businesses":sorted(matches,key=lambda x:x["distance_miles"]),
            "geocoding_errors":errors,
            "caution":"Not a complete or currently verified competitor census; licenses and store status require local confirmation. Counts include subject location if listed."}
