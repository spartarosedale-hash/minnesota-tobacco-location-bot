"""Automatic city-by-city discovery. Search results are leads, never verified stores."""
import csv,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
import requests
from lead_enrichment import enrich
from source_verification import verify_candidates
from lead_filter import relevant
from official_sources import for_city
from geofabrik_discovery import city_bounds,extract_candidates,discovery

ROOT=Path(__file__).resolve().parent
CITIES=("Zimmerman","Litchfield")
QUERIES=(
    '{city} MN tobacco shops vape stores',
    '{city} Minnesota tobacco retailer license list',
    '{city} MN retail commercial space for lease',
    '{city} Minnesota city council tobacco license renewals',
)
def discover_city(city,fetch=requests.get):
    findings=[]
    errors=[]
    for template in QUERIES:
        query=template.format(city=city)
        try:
            response=fetch("https://www.bing.com/search",params={"q":query,"format":"rss"},timeout=15,
                           headers={"User-Agent":"Mozilla/5.0 (compatible; MinnesotaRetailResearch/1.0)"})
            response.raise_for_status()
            root=ET.fromstring(response.content)
            items=root.findall(".//channel/item")
            if not items:
                errors.append(query+": no RSS items returned")
            for item in items[:12]:
                title=item.findtext("title") or ""
                url=item.findtext("link") or ""
                snippet=item.findtext("description") or ""
                if url.startswith("https://"):
                    findings.append({"city":city,"query":query,"title":title,"url":url,
                                     "snippet":snippet[:400],"status":"UNVERIFIED_SEARCH_LEAD"})
        except (requests.RequestException,ET.ParseError) as exc:
            errors.append(query+": "+str(exc)[:160])
    unique={}
    rejected=0
    for row in findings:
        if not relevant(row,city):
            rejected+=1
            continue
        if row["url"] not in unique:
            unique[row["url"]]=row
    return {"city":city,"rejected_irrelevant":rejected,"raw_search_results":len(findings),"checked_at":datetime.now(timezone.utc).isoformat(),
            "leads":list(unique.values()),"errors":errors,
            "verification":"Search results are NOT confirmed businesses, vacancies or licenses"}

def main():
    city_file=ROOT/"research_cities.csv"
    with city_file.open(encoding="utf-8-sig",newline="") as f:
        cities=[r["city"].strip() for r in csv.DictReader(f) if r.get("city","").strip()]
    results=[]
    pbf=ROOT/"data"/"minnesota.osm.pbf"
    bounds={}
    bound_errors={}
    for city in cities:
        try:
            bounds[city]=city_bounds(city)
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            bound_errors[city]=str(exc)[:200]
    extracted={}
    extract_error=None
    if pbf.exists() and pbf.stat().st_size>1000000:
        try:
            extracted=extract_candidates(pbf,bounds)
        except (ImportError,OSError,RuntimeError,ValueError) as exc:
            extract_error=str(exc)[:200]
    else:
        extract_error="Minnesota Geofabrik PBF download unavailable"
    for city in cities:
        result=discover_city(city)
        result["official_licensing_sources"]=for_city(city)
        result["osm_discovery"]=discovery(city,extracted.get(city,[]),bound_errors.get(city) or extract_error)
        result["enrichment"]=enrich(result["leads"],city)
        result["source_verification"]=verify_candidates(result["enrichment"]["candidates"])
        result["official_source_verification"]=verify_candidates([{"city":city,"title":s["name"],"url":s["url"],"address_candidate":None} for s in result["official_licensing_sources"]])
        result["quality"]={"official_licensing_sources":len(result["official_licensing_sources"]),
                           "osm_business_candidates":len(result["osm_discovery"]["candidates"]),
                           "osm_status":result["osm_discovery"]["status"],
                           "osm_endpoint_attempts":len(result["osm_discovery"]["errors"])+(1 if result["osm_discovery"]["endpoint_used"] else 0),
                           "official_pages_read":sum(x.get("source_checked",False) for x in result["official_source_verification"]["candidates"]),
                           "page_address_candidates":sum(len(x.get("page_address_candidates",[])) for x in result["source_verification"]["candidates"]),
                           "search_leads":len(result["leads"]),
                           "classified_leads":sum(x["lead_type"]!="uncategorized_search_lead" for x in result["enrichment"]["candidates"]),
                           "address_candidates":sum(bool(x["address_candidate"]) for x in result["enrichment"]["candidates"]),
                           "geocoded_addresses":sum(x["latitude"] is not None for x in result["enrichment"]["candidates"]),
                           "source_pages_read":sum(x["evidence_status"].startswith("SOURCE_READ") or x["evidence_status"].startswith("SOURCE_MENTIONS") for x in result["source_verification"]["candidates"]),
                           "verified_operating_businesses":0,
                           "ready_for_competitor_scoring":False}
        results.append(result)
    out=ROOT/"data"
    out.mkdir(exist_ok=True)
    (out/"city_discovery.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps([{"city":r["city"],"leads":len(r["leads"]),"errors":len(r["errors"]),"rejected_irrelevant":r["rejected_irrelevant"],"official_pages_read":r["quality"]["official_pages_read"],"osm_business_candidates":r["quality"]["osm_business_candidates"],"osm_status":r["quality"]["osm_status"],"osm_coverage":r["osm_discovery"]["coverage"],"osm_endpoint_attempts":r["quality"]["osm_endpoint_attempts"],"page_address_candidates":r["quality"]["page_address_candidates"],"classified_leads":r["quality"]["classified_leads"],"address_candidates":r["quality"]["address_candidates"],"source_pages_read":r["quality"]["source_pages_read"]} for r in results],indent=2))

if __name__=="__main__":
    main()
