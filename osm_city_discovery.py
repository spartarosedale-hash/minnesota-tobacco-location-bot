"""Weekly, conservative OpenStreetMap candidate discovery by municipal area."""
import requests
ENDPOINT="https://overpass-api.de/api/interpreter"
def discover_osm(city,fetch=requests.get):
    # A single bounded request per city. No coordinates or fabricated business data.
    safe=city.replace('"','').replace('\\','')
    query=('[out:json][timeout:25];area["name"="'+safe+'"]["boundary"="administrative"]'
           '["is_in:state_code"="MN"]->.a;'
           '(nwr["shop"~"^(tobacco|e-cigarette|convenience)$"](area.a););out center;')
    try:
        r=fetch(ENDPOINT,params={"data":query},timeout=40,
                headers={"User-Agent":"MinnesotaRetailResearchBot/1.0 (weekly public data research)"})
        r.raise_for_status()
        data=r.json()
        results=[]
        for obj in data.get("elements",[])[:100]:
            tags=obj.get("tags",{})
            point=obj.get("center") or obj
            if not tags.get("name"):continue
            results.append({"name":tags["name"],"category":tags.get("shop"),
                            "address_candidate":" ".join(filter(None,[tags.get("addr:housenumber"),tags.get("addr:street")])) or None,
                            "latitude":point.get("lat"),"longitude":point.get("lon"),
                            "source":"OpenStreetMap","osm_id":obj.get("id"),"osm_type":obj.get("type"),
                            "status":"UNVERIFIED_OSM_BUSINESS_CANDIDATE"})
        return {"candidates":results,"error":None,"coverage":"community_mapped_not_exhaustive"}
    except (requests.RequestException,ValueError) as exc:
        return {"candidates":[],"error":str(exc)[:200],"coverage":"unavailable"}
