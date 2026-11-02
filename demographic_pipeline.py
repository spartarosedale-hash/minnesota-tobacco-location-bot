"""Generate research demographic evidence reports for configured cities.

Uses Census ACS 5-year API (2024 vintage) for age and sex populations.
No household-income-to-adult joint table is assumed. Unknown cells remain
unavailable. Marginal research rates are kept separate, not averaged.
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
from age_tobacco_model import estimate_by_age
from sex_tobacco_model import estimate_by_sex
from vaping_demand_model import estimate_vaping_scenario
from smokeless_demand_model import estimate_smokeless
from combined_demographic_model import DemographicEvidence, combine_demographic_evidence, compare_dimensions

ROOT = Path(__file__).resolve().parent
API = "https://api.census.gov/data/2024/acs/acs5"
# B01001: male age bins 3..25; female age bins 27..49.
AGE_GROUPS = {"18_24": (8,9,10,11), "25_44": (12,13,14,15),
              "45_64": (16,17,18,19,20), "65_plus": (21,22,23,24,25)}
def code(sex, i):
    return f"B01001_{i + (0 if sex == 'male' else 24):03d}E"

def age_counts(row):
    return {band: sum(int(row[code(sex,i)]) for sex in ("male","female") for i in ids)
            for band, ids in AGE_GROUPS.items()}

def sex_counts(row):
    return {sex: sum(int(row[code(sex,i)]) for band, ids in AGE_GROUPS.items() for i in ids)
            for sex in ("male","female")}

def fetch_mn_places(session=requests):
    variables = sorted({code(sex,i) for sex in ("male","female") for ids in AGE_GROUPS.values() for i in ids})
    response = session.get(API,params={"get":"NAME,"+",".join(variables),"for":"place:*","in":"state:27"},timeout=45)
    response.raise_for_status()
    data=response.json()
    return [dict(zip(data[0],values)) for values in data[1:]]

def report_city(city,row):
    ages=age_counts(row)
    sexes=sex_counts(row)
    a=estimate_by_age(ages)
    s=estimate_by_sex(sexes)
    evidence=[]
    for product, users in a.estimated_users.items():
        evidence.append(DemographicEvidence(product,a.source,a.survey_year,users,a.adults_18_plus,"age","US rates applied to MN ACS 2024"))
    for product, users in s.product_users.items():
        evidence.append(DemographicEvidence(product,s.source,s.source_year,users,s.adults_included,"sex","US rates applied to MN ACS 2024"))
    combined=combine_demographic_evidence(evidence)
    vape=estimate_vaping_scenario(a.adults_18_plus)
    smokeless=estimate_smokeless(a.adults_18_plus,0.021)
    supplementary={
        "vaping_mn_benchmark":{"estimated_users_18_plus":round(vape.estimated_adult_vapers,1),
            "monthly_market_spend_benchmark":round(vape.total_market_spend_benchmark,2),
            "store_revenue":None,"status":vape.status},
        "smokeless_us_benchmark":{"estimated_users_18_plus":round(smokeless.users,1),
            "monthly_tins":None,"store_revenue":None,"status":smokeless.status},
        "premium_nonpremium_cigars":{"estimated_users":None,
            "status":"requires adult population by poverty ratio; unavailable"}}

    return {"city":city,"acs_place":row["NAME"],"acs_year":2024,"adult_population_18_plus":a.adults_18_plus,
            "age_counts":ages,"sex_counts":sexes,
            "supplementary_product_scenarios":supplementary,
            "product_evidence":{product:{"marginal_estimates":{dimension:round(e.estimated_users,1)
                  for dimension,e in assessment.evidence_by_dimension.items()},
                  "prevalence_by_dimension":compare_dimensions(assessment),
                  "joint_estimate":assessment.estimated_unique_users,
                  "status":assessment.status} for product,assessment in combined.items()},
            "household_income_context":row.get("_income_context"),
            "income_status":"Household counts are context only, not adult income counts",
            "retail_21_plus_population":a.adults_18_plus-sum(
                int(row[code(sex,i)]) for sex in ("male","female") for i in (8,9)),
            "retail_21_plus_status":"ACS 18-20 excluded; product prevalence still 18+ only",
            "sales_prediction_status":"not calibrated"}

def main():
    with (ROOT/"research_cities.csv").open(newline="",encoding="utf-8") as f:
        cities=[r["city"].strip() for r in csv.DictReader(f) if r["city"].strip()]
    out={"generated_at":datetime.now(timezone.utc).isoformat(),"cities":{},"errors":{}}
    try:
        rows=fetch_mn_places()
        variables=[f"B19001_{i:03d}E" for i in range(1,18)]+["B19013_001E"]
        response=requests.get(API,params={"get":"NAME,"+",".join(variables),"for":"place:*","in":"state:27"},timeout=45)
        response.raise_for_status()
        data=response.json()
        incomes={r["NAME"]:r for r in (dict(zip(data[0],v)) for v in data[1:])}
        for row in rows:
            inc=incomes.get(row["NAME"])
            if inc:
                row["_income_context"]={"household_counts_by_income":{k:int(inc[k]) for k in variables[:-1]},
                    "median_household_income":int(inc["B19013_001E"]),
                    "unit":"households_not_adults"}

        lookup={r["NAME"].split(",")[0].removesuffix(" city").removesuffix(" town").strip().casefold():r for r in rows}
        for city in cities:
            row=lookup.get(city.casefold())
            if row is None:
                out["errors"][city]="No exact Minnesota ACS incorporated place match"
            else:
                try: out["cities"][city]=report_city(city,row)
                except (ValueError,KeyError) as exc: out["errors"][city]=str(exc)
    except (requests.RequestException,ValueError) as exc:
        out["errors"]["census_api"]=str(exc)
    (ROOT/"data").mkdir(exist_ok=True)
    (ROOT/"data"/"demographic_research.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("Demographic reports:",len(out["cities"]),"errors:",out["errors"])
    if out["errors"]: raise SystemExit(1)
if __name__=="__main__": main()
