"""Free OpenStreetMap nearby retail and destination discovery.
Uses public Overpass API with conservative request volume; no paid key.
Presence and distance are NOT measured customer visits.
"""
import requests
from traffic_and_competition import miles

ENDPOINT="https://overpass.kumi.systems/api/interpreter"
TAGS={"shop":["tobacco","convenience","supermarket","mall","department_store"],
      "amenity":["fuel","fast_food","restaurant","cafe"]}
def discover(lat,lon,radius_miles=3,endpoint=ENDPOINT):
    if not (-90<=lat<=90 and -180<=lon<=180 and 0<radius_miles<=10):
        raise ValueError("Invalid coordinates or radius")
    radius=int(radius_miles*1609.344)
    filters=[]
    for tag,values in TAGS.items():
        values_regex="|".join(values)
        filters.append(f'node["{tag}"~"^({values_regex})$"](around:{radius},{lat},{lon});')
        filters.append(f'way["{tag}"~"^({values_regex})$"](around:{radius},{lat},{lon});')
    query="[out:json][timeout:25];("+ "".join(filters) +");out center tags;"
    resp=requests.post(endpoint,data={"data":query},timeout=35,
                       headers={"User-Agent":"MinnesotaTobaccoSiteResearchBot/1.0"})
    resp.raise_for_status()
    payload=resp.json()
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
    return {"status":"ok","source":"OpenStreetMap via Overpass","nearby_places":venues,
            "counts_by_category":{k:sum(v["category"]==k for v in venues) for k in sorted(set(v["category"] for v in venues))},
            "coverage":"community_mapped_not_exhaustive",
            "warning":"Free business-presence data, NOT footfall. No measured visits or comparable busyness."}
