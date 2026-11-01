"""Offline competitor candidates from licensed Geofabrik Minnesota OSM extract.

Bounding boxes come from Nominatim and are approximate, not municipal polygons.
All records are unverified. No live bulk downloads from OSM's map API.
"""
from pathlib import Path
import requests
from specialty_shop_filter import specialty_match

SOURCE="https://download.geofabrik.de/north-america/us/minnesota-latest.osm.pbf"
SHOPS={"tobacco","e-cigarette","convenience"}

def city_bounds(city,fetch=requests.get):
    r=fetch("https://nominatim.openstreetmap.org/search",
        params={"city":city,"state":"Minnesota","country":"United States","format":"jsonv2","limit":5},
        headers={"User-Agent":"MinnesotaRetailResearchBot/1.0 (GitHub research project)"},timeout=20)
    r.raise_for_status()
    for place in r.json():
        if "Minnesota" in place.get("display_name","") and place.get("type") in ("administrative","city","town","village"):
            south,north,west,east=map(float,place["boundingbox"])
            if 43<=south<north<=50 and -98<=west<east<=-89:
                return (south,north,west,east)
    raise ValueError("Minnesota municipality bounding box unavailable: "+city)

def extract_candidates(path,bounds):
    import osmium
    found={city:[] for city in bounds}
    seen={city:set() for city in bounds}
    class Collector(osmium.SimpleHandler):
        def record(self,obj,kind,lat,lon):
            if lat is None or lon is None:return
            tags=obj.tags
            match_reason=specialty_match(tags)
            if not match_reason:return
            for city,(south,north,west,east) in bounds.items():
                if not(south<=lat<=north and west<=lon<=east):continue
                key=(kind,int(obj.id))
                if key in seen[city]:continue
                seen[city].add(key)
                found[city].append({"name":tags.get("name"),"category":tags.get("shop"),
                    "address_candidate":" ".join(filter(None,[tags.get("addr:housenumber"),tags.get("addr:street")])) or None,
                    "latitude":lat,"longitude":lon,"source":"Geofabrik Minnesota OpenStreetMap extract",
                    "source_url":SOURCE,"osm_id":int(obj.id),"osm_type":kind,
                    "match_reason":match_reason,
                    "status":"UNVERIFIED_OSM_BUSINESS_CANDIDATE"})
        def node(self,n):
            if n.location.valid():self.record(n,"node",n.location.lat,n.location.lon)
        def way(self,w):
            pts=[(n.location.lat,n.location.lon) for n in w.nodes if n.location.valid()]
            if pts:self.record(w,"way",sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))
    Collector().apply_file(str(Path(path)),locations=True)
    return found

def discovery(city,records,error=None):
    if error:return {"status":"unavailable","candidates":[],"error":error,"errors":[{"source":"Geofabrik extract","error":error}],
        "endpoint_used":None,"coverage":"unavailable"}
    return {"status":"available" if records else "empty","candidates":records,"error":None,"errors":[],
        "endpoint_used":"Geofabrik Minnesota PBF","coverage":"nominatim_bbox_approximate_not_exhaustive",
        "warning":"Bounding box is not a municipal boundary; nearby businesses may be included and unmapped shops missed."}
