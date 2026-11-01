"""Run age 21+ Census tract profiles for three validation locations.

This is a tract-level first pass, NOT a 5/10/15-minute driving-area estimate.
Actual drive-time areas require routing polygons and spatially weighted Census
block-group data; do not relabel tract totals as drive-time totals.
"""
import json
from census_location import lookup

STORES = {
    "Zimmerman Tobacco": "26219 Fremont Dr Ste 101, Zimmerman, MN 55398",
    "Maple Plain Smoke Shop": "5020 US-12 Ste 2, Maple Plain, MN 55359",
    "Litchfield Tobacco": "231 N Sibley Ave, Litchfield, MN 55355",
}

def main():
    results = {}
    for name, address in STORES.items():
        try:
            results[name] = lookup(address)
        except Exception as exc:
            results[name] = {"address": address, "status": "source_error", "error_type": type(exc).__name__}
    print(json.dumps({"geography": "2020 Census tract", "year": 2024,
                      "not_drive_time_population": True, "stores": results}, indent=2))

if __name__ == "__main__":
    main()
