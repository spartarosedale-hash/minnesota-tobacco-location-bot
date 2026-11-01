"""Fetch official Census tract age-21+ population for a Minnesota street address.

Census geocoder: 2020 census geography (tract identifier).
ACS: 2024 5-year tract B01001 age/sex counts.
A tract is NOT a 1/3/5-mile trade area. Never describe it as such.
Run: python census_location.py --address "525 Diffley Rd, Eagan, MN 55123"
"""
import argparse
import json
from urllib.parse import urlencode
from urllib.request import urlopen

GEOCODER = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
ACS = "https://api.census.gov/data/2024/acs/acs5"
# ACS B01001: male 21+ = 010..025; female 21+ = 034..049.
ADULT_CODES = [f"B01001_{i:03d}E" for i in list(range(10,26))+list(range(34,50))]

def fetch_json(url, params, opener=urlopen):
    with opener(url+"?"+urlencode(params), timeout=20) as response:
        return json.load(response)

def lookup(address, fetch=fetch_json):
    if not address.strip():
        raise ValueError("Street address is required")
    geo=fetch(GEOCODER,{"address":address,"benchmark":"Public_AR_Current",
                       "vintage":"Census2020_Current","format":"json"})
    matches=geo.get("result",{}).get("addressMatches",[])
    if not matches:
        return {"address":address,"status":"address_not_geocoded"}
    m=matches[0]
    tracts=m.get("geographies",{}).get("Census Tracts",[])
    if not tracts:
        return {"address":address,"status":"tract_not_found"}
    tract=tracts[0]
    state=tract["STATE"];county=tract["COUNTY"];tract_id=tract["TRACT"]
    # API allows <=50 variables per request.
    data=fetch(ACS,{"get":"NAME,"+",".join(ADULT_CODES),
                    "for":"tract:"+tract_id,"in":f"state:{state} county:{county}"})
    if len(data)<2:
        return {"address":address,"status":"acs_unavailable"}
    row=dict(zip(data[0],data[1]))
    counts=[int(row[c]) for c in ADULT_CODES]
    if any(v<0 for v in counts):
        return {"address":address,"status":"acs_suppressed"}
    return {"address":address,"matched_address":m.get("matchedAddress"),
            "status":"ok","census_tract":tract_id,"county_fips":county,
            "state_fips":state,"acs_year":2024,
            "adult_population_21_plus_tract":sum(counts),
            "geography_warning":"Census tract population, NOT a radius trade-area count",
            "source":"US Census geocoder and 2024 ACS 5-year B01001"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--address",required=True)
    args=p.parse_args()
    try:
        result=lookup(args.address)
    except Exception as e:
        result={"address":args.address,"status":"data_source_error",
                "error_type":type(e).__name__}
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
