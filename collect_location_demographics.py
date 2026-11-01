"""Evidence-first public data collector for Minnesota retail location analysis.

Requires CENSUS_API_KEY for ACS requests. Traffic datasets are discoverable
through the MnDOT catalog; no undocumented traffic API is assumed.
"""
import argparse
import csv
import json
import os
from datetime import date
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ACS = "https://api.census.gov/data/2024/acs/acs5"
GEO = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
STORES = {
    "Zimmerman Tobacco": "26219 Fremont Dr Ste 101, Zimmerman, MN 55398",
    "Maple Plain Smoke Shop": "5020 US-12 Ste 2, Maple Plain, MN 55359",
    "Litchfield Tobacco": "231 N Sibley Ave, Litchfield, MN 55355",
}
# B01001 male 21+ 010-025, female 21+ 034-049
AGE21 = [f"B01001_{n:03d}E" for n in list(range(10,26))+list(range(34,50))]
AGE65 = [f"B01001_{n:03d}E" for n in list(range(20,26))+list(range(44,50))]
FIELDS = list(dict.fromkeys(["B01001_001E", "B19013_001E"] + AGE21 + [f"B19001_{i:03d}E" for i in range(1, 18)] + [f"B03002_{i:03d}E" for i in (1, 3, 4, 6, 12)]))
AGE_GROUPS = {"21_24": [10, 11, 34, 35], "25_34": [12, 13, 36, 37], "35_44": [14, 38], "45_54": [15, 16, 39, 40], "55_64": [17, 18, 19, 41, 42, 43], "65_plus": list(range(20, 26)) + list(range(44, 50))}
INCOME_BRACKETS = {"under_35k": list(range(2, 8)), "35k_to_75k": list(range(8, 13)), "75k_to_125k": [13, 14], "125k_plus": [15, 16, 17]}

def get_json(base, params):
    req = Request(base + "?" + urlencode(params), headers={"User-Agent":"MinnesotaLocationResearch/1.0"})
    with urlopen(req, timeout=35) as response:
        return json.load(response)

def collect_one(name, address, key):
    geo = get_json(GEO, {"address": address, "benchmark":"Public_AR_Current",
                         "vintage":"Census2020_Current","format":"json"})
    matches = geo.get("result",{}).get("addressMatches",[])
    if not matches:
        return {"store":name,"address":address,"status":"geocode_failed"}
    match=matches[0]
    tract=match.get("geographies",{}).get("Census Tracts",[])
    if not tract:
        return {"store":name,"address":address,"status":"tract_unavailable"}
    t=tract[0]
    params={"get":",".join(FIELDS),"for":"tract:"+t["TRACT"],
            "in":f"state:{t['STATE']} county:{t['COUNTY']}",**({"key":key} if key else {})}
    data=get_json(ACS,params)
    if len(data)<2:
        return {"store":name,"address":address,"status":"acs_missing"}
    values=dict(zip(data[0],data[1]))
    try:
        population=int(values["B01001_001E"])
        adults=sum(int(values[k]) for k in AGE21)
        older=sum(int(values[k]) for k in AGE65)
        income=int(values["B19013_001E"])
        if min(population,adults,older,income)<0:
            raise ValueError("suppressed estimate")
    except (ValueError,KeyError):
        return {"store":name,"address":address,"status":"acs_suppressed"}
    age_groups = {label: sum(int(values[f"B01001_{i:03d}E"]) for i in indices) for label, indices in AGE_GROUPS.items()}
    income_brackets = {label: sum(int(values[f"B19001_{i:03d}E"]) for i in indices) for label, indices in INCOME_BRACKETS.items()}
    ethnicity = {label: int(values[f"B03002_{i:03d}E"]) for label, i in {"total": 1, "non_hispanic_white": 3, "non_hispanic_black": 4, "non_hispanic_asian": 6, "hispanic_any_race": 12}.items()}
    return {"store":name,"address":address,"status":"ok",
            "age_groups_tract": age_groups,
            "household_income_brackets_tract": income_brackets,
            "households_tract": int(values["B19001_001E"]),
            "ethnicity_descriptive_only_tract": ethnicity,
            "latitude":match["coordinates"]["y"],"longitude":match["coordinates"]["x"],
            "tract_fips":t["STATE"]+t["COUNTY"]+t["TRACT"],
            "population_tract":population,"age_21_plus_tract":adults,
            "age_65_plus_tract":older,"median_household_income_tract":income,
            "acs_vintage":"2024 ACS 5-year","geography":"Census tract (NOT drive-time area)",
            "source":"https://api.census.gov/data/2024/acs/acs5",
            "retrieved_date":date.today().isoformat()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="research_demographics.json")
    args=parser.parse_args()
    key=os.environ.get("CENSUS_API_KEY")
    results=[]
    for name,address in STORES.items():
        try:
            results.append(collect_one(name,address,key))
        except Exception as error:
            results.append({"store":name,"address":address,"status":"source_error",
                            "error_type":type(error).__name__})
    with open(args.output,"w",encoding="utf-8") as handle:
        json.dump({"method":"ACS 2024 Census tract estimates; NOT 5/10/15-minute demographics",
                   "results":results},handle,indent=2)
    print(json.dumps({"output":args.output,"statuses":{r["store"]:r["status"] for r in results}},indent=2))
    if any(r["status"]!="ok" for r in results):
        raise SystemExit(1)

if __name__=="__main__":
    main()
