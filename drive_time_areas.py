"""Generate real 5/10/15-minute driving isochrones for the three validation stores.

Requires ORS_API_KEY environment variable (openrouteservice). Census geocoding
provides coordinates. This script does NOT claim a tract population is a drive
time population; population overlay must be added separately.
Run: ORS_API_KEY=... python drive_time_areas.py --output drive_time_areas.geojson
"""
import argparse
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GEOCODER = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
ORS = "https://api.openrouteservice.org/v2/isochrones/driving-car"
STORES = {
    "Zimmerman Tobacco": "26219 Fremont Dr Ste 101, Zimmerman, MN 55398",
    "Maple Plain Smoke Shop": "5020 US-12 Ste 2, Maple Plain, MN 55359",
    "Litchfield Tobacco": "231 N Sibley Ave, Litchfield, MN 55355",
}

def geocode(address):
    query = urlencode({"address": address, "benchmark": "Public_AR_Current", "vintage": "Census2020_Current", "format": "json"})
    with urlopen(GEOCODER + "?" + query, timeout=30) as response:
        data = json.load(response)
    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        raise ValueError("Census could not geocode: " + address)
    coordinates = matches[0]["coordinates"]
    return [float(coordinates["x"]), float(coordinates["y"])]

def isochrones(coordinates, api_key):
    if not api_key:
        raise ValueError("Set ORS_API_KEY to an openrouteservice API key")
    body = json.dumps({"locations": [coordinates], "range": [300, 600, 900], "range_type": "time"}).encode("utf-8")
    req = Request(ORS, data=body, headers={"Authorization": api_key, "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=90) as response:
        data = json.load(response)
    features = data.get("features", [])
    if len(features) != 3:
        raise ValueError("Expected three drive-time polygons; received " + str(len(features)))
    return features

def build(api_key, stores=STORES):
    output = []
    errors = {}
    for name, address in stores.items():
        try:
            point = geocode(address)
            for feature in isochrones(point, api_key):
                seconds = feature.get("properties", {}).get("value")
                if seconds not in (300, 600, 900):
                    raise ValueError("Unexpected isochrone range")
                output.append({"type": "Feature", "geometry": feature["geometry"],
                               "properties": {"store": name, "address": address,
                                              "minutes": seconds // 60, "source": "openrouteservice driving-car",
                                              "population_21_plus": None,
                                              "median_household_income": None,
                                              "demographics_status": "not_computed"}})
        except Exception as exc:
            errors[name] = type(exc).__name__ + ": " + str(exc)
    return {"type": "FeatureCollection", "features": output,
            "metadata": {"population_estimates_included": False, "errors": errors,
                         "note": "Polygons are road travel-time areas; Census demographic overlay is not implemented."}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="drive_time_areas.geojson")
    args = parser.parse_args()
    if not os.environ.get("ORS_API_KEY"):
        parser.error("ORS_API_KEY environment variable is required")
    result = build(os.environ["ORS_API_KEY"])
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps({"output": args.output, "polygons": len(result["features"]),
                      "errors": result["metadata"]["errors"]}, indent=2))
    if result["metadata"]["errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
