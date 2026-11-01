"""Retrieve nearby MnDOT AADT segments using an official Minnesota GIS service.

Output is a list of nearby road segments, NOT a verified storefront frontage
count. Road selection requires review of route, access, and segment geometry.
"""
import argparse
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from drive_time_areas import geocode, STORES

LAYER = "https://services6.arcgis.com/nAAX2HQeTkcM7MyI/arcgis/rest/services/AADT/FeatureServer/0"

def nearby_segments(lon, lat, radius_m=1500):
    params = {
        "f": "json", "where": "1=1", "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint", "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects", "distance": radius_m,
        "units": "esriSRUnit_Meter", "outFields": "*", "returnGeometry": "true",
        "outSR": "4326",
    }
    with urlopen(LAYER + "/query?" + urlencode(params), timeout=60) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError("MnDOT GIS returned an error: " + str(result["error"]))
    return result.get("features", [])

def collect(stores=STORES):
    results = {}
    for name, address in stores.items():
        try:
            lon, lat = geocode(address)
            features = nearby_segments(lon, lat)
            results[name] = {
                "status": "ok", "address": address,
                "geocoded_coordinates": [lon, lat],
                "candidate_segments": features,
                "candidate_count": len(features),
                "frontage_segment_verified": False,
                "source": LAYER,
                "warning": "Nearby candidates are not necessarily the road directly in front of the store.",
            }
        except Exception as exc:
            results[name] = {"status": "source_error", "address": address,
                             "error_type": type(exc).__name__, "error_detail": str(exc)[:500]}
            print(f"::error title=MnDOT collection failed for {name}::{type(exc).__name__}: {str(exc)[:500]}")
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="research_traffic.json")
    args = parser.parse_args()
    results = collect()
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
    print(json.dumps({k: {"status": v["status"], "candidate_count": v.get("candidate_count", 0)}
                      for k, v in results.items()}, indent=2))
    if any(v["status"] != "ok" for v in results.values()):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
