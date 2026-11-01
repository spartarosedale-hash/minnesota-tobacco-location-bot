"""Automatic city-by-city discovery. Search results are leads, never verified stores."""
import csv,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
import requests
from lead_enrichment import enrich

ROOT=Path(__file__).resolve().parent
CITIES=("Zimmerman","Litchfield")
QUERIES=(
    '"{city}" Minnesota tobacco retail license city county',
    '"{city}" Minnesota smoke shop vape shop address',
    '"{city}" Minnesota retail space for lease vacant',
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
    unique={r["url"]:r for r in findings}
    return {"city":city,"checked_at":datetime.now(timezone.utc).isoformat(),
            "leads":list(unique.values()),"errors":errors,
            "verification":"Search results are NOT confirmed businesses, vacancies or licenses"}

def main():
    city_file=ROOT/"research_cities.csv"
    with city_file.open(encoding="utf-8-sig",newline="") as f:
        cities=[r["city"].strip() for r in csv.DictReader(f) if r.get("city","").strip()]
    results=[]
    for city in cities:
        result=discover_city(city)
        result["enrichment"]=enrich(result["leads"],city)
        results.append(result)
    out=ROOT/"data"
    out.mkdir(exist_ok=True)
    (out/"city_discovery.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps([{"city":r["city"],"leads":len(r["leads"]),"errors":len(r["errors"]),"enriched_candidates":len(r["enrichment"]["candidates"])} for r in results],indent=2))

if __name__=="__main__":
    main()
