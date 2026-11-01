"""Free OpenStreetMap nearby retail and destination discovery.
Uses public Overpass API with conservative request volume; no paid key.
Presence and distance are NOT measured customer visits.
"""
import requests
from traffic_and_competition import miles

ENDPOINT="https://overpass.private.coffee/api/interpreter"
TAGS={"shop":["tobacco","convenience","supermarket","mall","department_store"],
      "amenity":["fuel","fast_food","restaurant","cafe"]}
def discover(lat,lon,radius_miles=5,endpoint=ENDPOINT):
    if not (-90<=lat<=90 and -180<=lon<=180 and 0<radius_miles<=10):
        raise ValueError("Invalid coordinates or radius")
    radius=int(radius_miles*1609.344)
    filters=[]
    for tag,values in TAGS.items():
        values_regex="|".join(values)
        filters.append(f'node["{tag}"~"^({values_regex})$"](around:{radius},{lat},{lon});')
        filters.append(f'way["{tag}"~"^({values_regex})$"](around:{radius},{lat},{lon});')
    query="[out:json][timeout:25];("+ "".join(filters) +");out center tags;"
    errors=[]
    payload=None
    used_endpoint=None
    endpoints=[endpoint]+(["https://overpass-api.de/api/interpreter"] if endpoint==ENDPOINT else [])
    for url in endpoints:
        try:
            resp=requests.post(url,data={"data":query},timeout=(10,35),
                               headers={"User-Agent":"MinnesotaTobaccoSiteResearchBot/1.0"})
            resp.raise_for_status()
            candidate=resp.json()
            if not isinstance(candidate.get("elements"),list):
                raise ValueError("Missing Overpass elements list")
            if "remark" in candidate and "error" in str(candidate["remark"]).lower():
                raise RuntimeError(str(candidate["remark"])[:250])
            payload=candidate
            used_endpoint=url
            break
        except (requests.RequestException,ValueError,RuntimeError) as exc:
            errors.append(f"{url}: {type(exc).__name__}: {str(exc)[:120]}")
    if payload is None:
        raise RuntimeError("Overpass endpoints failed: "+"; ".join(errors))
    if "remark" in payload and "error" in payload["remark"].lower():
        raise RuntimeError(payload["remark"][:250])
    venues=[]
    seen=set()
    for obj in payload.get("elements",[]):
        tags=obj.get("tags",{})
        coords=obj.get("center") or obj
        if "lat" not in coords or "lon" not in coords:continue
        ident=(obj.get("type"),obj.get("id"))
        if ident in seen:continue
        seen.add(ident)
        distance=miles(lat,lon,float(coords["lat"]),float(coords["lon"]))
        if distance>radius_miles:continue
        venues.append({"name":tags.get("name") or "Unnamed location",
                       "category":tags.get("shop") or tags.get("amenity"),
                       "distance_miles":round(distance,2),
                       "osm_type":obj.get("type"),"osm_id":obj.get("id"),
                       "estimated_visits":None})
    venues.sort(key=lambda x:x["distance_miles"])
    tobacco=[v for v in venues if v["category"]=="tobacco"]
    rings={str(r):sum(v["distance_miles"]<=r for v in tobacco) for r in (1,3,5)}
    return {"status":"ok","source":"OpenStreetMap via Overpass","endpoint_used":used_endpoint,
            "tobacco_candidates_within_miles":rings,"tobacco_candidates":tobacco,
            "competitor_verification":"UNVERIFIED_OSM_CANDIDATES_ONLY","nearby_places":venues,
            "counts_by_category":{k:sum(v["category"]==k for v in venues) for k in sorted(set(v["category"] for v in venues))},
            "coverage":"community_mapped_not_exhaustive","search_radius_miles":radius_miles,
            "warning":"Free business-presence data, NOT footfall. No measured visits or comparable busyness."}
