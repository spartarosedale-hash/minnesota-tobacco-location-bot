"""Address -> Census place demographics -> scenario sales estimate.
Run: python address_forecast.py "231 N Sibley Ave, Litchfield, MN 55355"
Optional: CENSUS_API_KEY environment variable. Results are scenarios, not trained predictions.
"""
import argparse
import json
import os
import requests

GEOCODER = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
ACS = "https://api.census.gov/data/2024/acs/acs5"
# ACS B01001 age 21+ (male indices 9..25, female indices 33..49)
ADULT_FIELDS = [f"B01001_{i:03d}E" for i in list(range(9, 26)) + list(range(33, 50))]

def fetch_json(url, params):
    response = requests.get(url, params=params, timeout=25, headers={"User-Agent":"MinnesotaSiteResearchBot/1.0"})
    response.raise_for_status()
    if "/missing_key.html" in response.url:
        raise RuntimeError("Census API redirected to missing_key.html. Configure the free CENSUS_API_KEY as a GitHub Actions repository secret; no demographic data was returned.")
    try:
        return response.json()
    except ValueError as exc:
        content_type = response.headers.get("Content-Type", "unknown")
        preview = response.text[:160].replace("\\n", " ").replace("\\r", " ")
        raise ValueError(f"Non-JSON response from {response.url.split('?')[0]} (HTTP {response.status_code}, Content-Type {content_type}): {preview!r}") from exc

def lookup(address):
    data = fetch_json(GEOCODER, {"address":address,"benchmark":"Public_AR_Current","vintage":"Current_Current","format":"json"})
    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        raise ValueError("Address not matched by US Census geocoder")
    match = matches[0]
    geo = match.get("geographies", {})
    places = geo.get("Incorporated Places", []) + geo.get("Census Designated Places", [])
    if not places:
        for key, entries in geo.items():
            if "place" in key.lower() and isinstance(entries,list):
                places.extend(entries)
    if not places:
        raise ValueError("Address is outside a Census place; no city proxy available")
    place = places[0]
    return {"matched_address":match["matchedAddress"],"latitude":match["coordinates"]["y"],"longitude":match["coordinates"]["x"],"place":place["NAME"],"state":place["STATE"],"place_code":place["PLACE"]}

def demographics(site):
    # The Census API permits a maximum of 50 variables per request. Use two
    # smaller calls and avoid making a public API key mandatory.
    base = {"for": "place:" + site["place_code"], "in": "state:" + site["state"]}
    key = os.environ.get("CENSUS_API_KEY", "").strip()
    if key:
        base["key"] = key
    def query(fields):
        params = dict(base, get=",".join(fields))
        return fetch_json(ACS, params)
    rows = query(["NAME", "B01001_001E", "B19013_001E"])
    if len(rows) < 2:
        raise ValueError("No ACS records for place")
    record = dict(zip(rows[0], rows[1]))
    age_rows = query(ADULT_FIELDS)
    if len(age_rows) < 2:
        raise ValueError("No ACS age records for place")
    ages = dict(zip(age_rows[0], age_rows[1]))
    adults = sum(int(ages[f]) for f in ADULT_FIELDS)
    population = int(record["B01001_001E"])
    if not 0 < adults <= population:
        raise ValueError("ACS adult counts failed validation")
    income = int(record["B19013_001E"])
    return {"acs_vintage":"2020-2024 ACS 5-year","place_population":population,"adults_21_plus":adults,"median_household_income":income if income > 0 else None}

def forecast(address, capture_rates=(0.05,0.10,0.15), monthly_spend=60):
    if not 0 < monthly_spend or any(not 0 <= x <= 1 for x in capture_rates) or list(capture_rates)!=sorted(capture_rates):
        raise ValueError("Invalid scenario assumptions")
    site = lookup(address)
    demo = demographics(site)
    adults = demo["adults_21_plus"]
    return {"site":site,"demographics":demo,"sales_estimate_monthly_usd":{"low":round(adults*capture_rates[0]*monthly_spend),"base":round(adults*capture_rates[1]*monthly_spend),"high":round(adults*capture_rates[2]*monthly_spend)},"assumptions":{"monthly_spend_usd":monthly_spend,"market_capture_rates":capture_rates},"status":"UNTRAINED_SCENARIO_ONLY","limitations":["Uses whole Census place, NOT 1/3/5-mile trade area","No road traffic, competitors, rent or real-store calibration","Do not treat as an investment-grade forecast"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("address")
    parser.add_argument("--monthly-spend",type=float,default=60)
    parser.add_argument("--capture-low",type=float,default=.05)
    parser.add_argument("--capture-base",type=float,default=.10)
    parser.add_argument("--capture-high",type=float,default=.15)
    args=parser.parse_args()
    print(json.dumps(forecast(args.address,(args.capture_low,args.capture_base,args.capture_high),args.monthly_spend),indent=2))

if __name__=="__main__":
    main()
