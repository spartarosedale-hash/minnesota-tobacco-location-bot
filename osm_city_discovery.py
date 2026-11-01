"""OpenStreetMap city discovery with bounded fallback and explicit availability."""
import requests

ENDPOINTS=(
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
)

def discover_osm(city,fetch=requests.get,endpoints=ENDPOINTS):
    # Restrict to exact municipal administrative area in Minnesota.
    safe=city.replace('"',"").replace("\\","")
    query=('[out:json][timeout:12];area["name"="'+safe+'"]["boundary"="administrative"]'
           '["is_in:state_code"="MN"]->.a;'
           '(nwr["shop"~"^(tobacco|e-cigarette|convenience)$"](area.a););out center;')
    errors=[]
    for endpoint in endpoints:
        try:
            response=fetch(endpoint,params={"data":query},timeout=(4,16),
                headers={"User-Agent":"MinnesotaRetailResearchBot/1.0 (weekly public data research)"})
            response.raise_for_status()
            payload=response.json()
            if not isinstance(payload,dict) or not isinstance(payload.get("elements"),list):
                raise ValueError("Invalid Overpass response: missing elements")
            if payload.get("remark") and "error" in str(payload["remark"]).lower():
                raise ValueError(str(payload["remark"])[:160])
            candidates=[]
            for obj in payload["elements"][:100]:
                tags=obj.get("tags") or {}
                if not tags.get("name"):continue
                point=obj.get("center") or obj
                candidates.append({
                    "name":tags["name"],"category":tags.get("shop"),
                    "address_candidate":" ".join(filter(None,[tags.get("addr:housenumber"),tags.get("addr:street")])) or None,
                    "latitude":point.get("lat"),"longitude":point.get("lon"),
                    "source":"OpenStreetMap","osm_id":obj.get("id"),"osm_type":obj.get("type"),
                    "status":"UNVERIFIED_OSM_BUSINESS_CANDIDATE"})
            return {"status":"available" if candidates else "empty","candidates":candidates,
                    "error":None,"errors":errors,"endpoint_used":endpoint,
                    "coverage":"community_mapped_not_exhaustive",
                    "warning":"Empty does not establish absence; city-area mapping or tags may be incomplete."}
        except (requests.RequestException,ValueError,TypeError) as exc:
            errors.append({"endpoint":endpoint,"error":str(exc)[:180]})
    return {"status":"unavailable","candidates":[],"error":"All Overpass endpoints failed",
            "errors":errors,"endpoint_used":None,"coverage":"unavailable"}
