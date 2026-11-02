"""Build auditable, no-fabrication site feature coverage reports.

This is a data-readiness audit, NOT a revenue prediction. A location feature
is only measured when a sourced measurement is explicitly supplied.
"""
import json
import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "location_research_requirements.json"
KNOWN_SITES = {
    "Zimmerman": {
        "address": "26219 Fremont Dr Ste 101, Zimmerman, MN",
        "qualitative": {
            "co_tenancy": {
                "value": "Holiday gas station and liquor store nearby",
                "status": "user_reported",
                "source": "owner supplied; verify on site",
            },
            "highway_proximity": {
                "value": "Highway 169 corridor; frontage and turning access require verification",
                "status": "user_reported",
                "source": "owner supplied; no measured AADT yet",
            },
        },
        "road_segments_to_verify": ["Fremont Drive storefront frontage", "US Highway 169", "County Road 4"],
    },
    "Litchfield": {
        "address": "231 N Sibley Ave, Litchfield, MN",
        "qualitative": {
            "competitors": {
                "value": "Shell, Marathon and Litchfield Corner reportedly sell tobacco/vapes",
                "status": "user_reported",
                "source": "owner supplied; inventory and operation unverified",
            },
        },
        "road_segments_to_verify": ["North Sibley Avenue storefront frontage", "connecting regional highways"],
    },
}

def build_audit(city, requirements, demographic=None):
    groups = {}
    for group, features in requirements["feature_groups"].items():
        if group == "observed_validation":
            # Actual sales stay outside pre-prediction features.
            groups[group] = [{"feature": feature, "status": "held_out",
                              "value": None, "source": None} for feature in features]
        else:
            groups[group] = [{"feature": feature, "status": "unavailable",
                              "value": None, "source": None} for feature in features]
    site = KNOWN_SITES.get(city, {})
    demographic = demographic or {}
    counts = {
        "required_features": sum(len(x) for k, x in groups.items() if k != "observed_validation"),
        "measured_features": 0,
        "verified_qualitative_features": 0,
    }
    return {
        "city": city, "site_address": site.get("address"),
        "site_context": site.get("qualitative", {}),
        "road_segments_to_verify": site.get("road_segments_to_verify", []),
        "feature_groups": groups,
        "census_population_18_plus": demographic.get("adult_population_18_plus"),
        "census_population_21_plus": demographic.get("retail_21_plus_population"),
        "census_status": "available" if demographic.get("retail_21_plus_population") is not None else "unavailable",
        "coverage": counts,
        "monthly_sales_prediction": None,
        "prediction_status": "blocked: site traffic, catchment, competition and capture not measured; blind test preserved",
    }

def main():
    requirements = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    with (ROOT / "research_cities.csv").open(newline="", encoding="utf-8-sig") as f:
        cities = [r["city"].strip() for r in csv.DictReader(f) if r.get("city", "").strip()]
    census_path = ROOT / "data" / "demographic_research.json"
    census = json.loads(census_path.read_text(encoding="utf-8")).get("cities", {}) if census_path.exists() else {}
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "research readiness; no unmeasured traffic or forecast fabricated",
        "sites": [build_audit(city, requirements, census.get(city)) for city in cities],
    }
    output = ROOT / "data" / "location_feature_audit.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Location feature audits:", len(report["sites"]), "->", output)

if __name__ == "__main__":
    main()
