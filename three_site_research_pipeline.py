"""Reproducible public-source traffic and census enrichment for three known sites.

Never uses store sales in research features. Traffic is returned as nearby
segments, not automatically assigned to storefront frontage.
"""
import json
import math
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent
TRAFFIC="https://dotapp9.dot.state.mn.us/egis12/rest/services/TFA/MNDOT_TRAFFIC_DATA/MapServer/6/query"
CENSUS="https://api.census.gov/data/2024/acs/acs5"
GEOCODE="https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
SITES=[
    ("Litchfield Tobacco","231 N Sibley Ave, Litchfield, MN 55355"),
    ("Zimmerman Tobacco","26219 Fremont Dr Ste 101, Zimmerman, MN 55398"),
    ("MSP Tobacco and Vapor","2439 W 7th St, Saint Paul, MN 55116"),
]
def get_json(url,params):
    r=requests.get(url,params=params,timeout=35,headers={"User-Agent":"MNStoreLocationResearch/0.2 (research)"})
    r.raise_for_status()
    return r.json()

def geocode(address):
    data=get_json(GEOCODE,{"address":address,"benchmark":"Public_AR_Current","vintage":"Current_Current","format":"json"})
    matches=data.get("result",{}).get("addressMatches",[])
    if not matches: return None
    m=matches[0]
    return {"lat":m["coordinates"]["y"],"lon":m["coordinates"]["x"],
            "matched_address":m.get("matchedAddress"),"geographies":m.get("geographies",{})}

def nearby_aadt(lat,lon):
    # Query in WGS84, 1.5km search radius, inspect returned segment geometry.
    data=get_json(TRAFFIC,{"f":"json","geometry":json.dumps({"x":lon,"y":lat,"spatialReference":{"wkid":4326}}),
        "geometryType":"esriGeometryPoint","inSR":4326,"spatialRel":"esriSpatialRelIntersects",
        "distance":1500,"units":"esriSRUnit_Meter","outFields":"*","returnGeometry":"false","outSR":4326})
    if "error" in data: raise RuntimeError(str(data["error"]))
    results=[]
    for feature in data.get("features",[]):
        a=feature["attributes"]
        results.append({"year":a.get("CURRENT_YEAR"),"aadt":a.get("CURRENT_VOLUME"),
                        "road_name":a.get("ROUTE_NAME") or a.get("STREET_NAME"),
                        "attributes":a})
    return results[:100]

def census_tract(geo):
    tracts=geo.get("Census Tracts",[])
    if not tracts: return None
    tract=tracts[0]
    geoid=tract.get("GEOID","")
    if len(geoid)!=11:return None
    state,county,tract_code=geoid[:2],geoid[2:5],geoid[5:]
    # B01001 sex-by-age counts, B19013 median household income.
    fields=["NAME","B01001_001E","B19013_001E"]+[
        f"B01001_{i:03d}E" for i in list(range(9,26))+list(range(33,50))]
    data=get_json(CENSUS,{"get":",".join(fields),"for":f"tract:{tract_code}",
                           "in":f"state:{state} county:{county}"})
    values=dict(zip(data[0],data[1]))
    def num(k):
        try:
            v=int(values[k])
            return v if v>=0 else None
        except (ValueError,TypeError,KeyError):return None
    # ACS B01001: male 21+ bins 009..025; female 21+ bins 033..049.
    bins=[num(f"B01001_{i:03d}E") for i in list(range(9,26))+list(range(33,50))]
    return {"geography":"Census tract, NOT drive-time catchment","geoid":geoid,
            "name":values.get("NAME"),"population_total":num("B01001_001E"),
            "population_21_plus":sum(bins) if all(v is not None for v in bins) else None,
            "median_household_income":num("B19013_001E"),
            "source":"ACS 2024 five-year","warning":"Tract data cannot be represented as 5/10/15 minute catchment"}

def research_site(name,address):
    result={"name":name,"address":address,"sales_inputs_used":False}
    try:
        geo=geocode(address)
        result["geocode"]=geo
        if geo:
            for key,fn in (("census_tract",lambda:census_tract(geo)),
                           ("nearby_aadt_segments",lambda:nearby_aadt(geo["lat"],geo["lon"]))):
                try:result[key]=fn()
                except Exception as e:result[key+"_error"]=str(e)
        else:result["error"]="Census geocoder returned no address match"
    except Exception as e:result["error"]=str(e)
    result["frontage_aadt"]=None
    result["catchment_21_plus"]=None
    result["prediction"]=None
    result["limitations"]=["Nearby road segments require geometric and entrance-access matching",
        "Census tract population is not a drive-time catchment",
        "Conversion, competition and parking measurements not independently calibrated"]
    return result

def main():
    result={"method":"address-centered research, sales withheld",
            "sites":[research_site(name,address) for name,address in SITES]}
    out=ROOT/"data"/"three_site_research.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    for site in result["sites"]:
        print(site["name"],"geocoded:",bool(site.get("geocode")),
              "traffic_segments:",len(site.get("nearby_aadt_segments",[])),
              "tract_21_plus:",(site.get("census_tract") or {}).get("population_21_plus"),
              "error:",site.get("error"))
if __name__=="__main__":main()
