"""Read a downloaded Minnesota OSM PBF without live Overpass calls.

Only addr:city matches are assigned to cities; records without that tag are
unassigned, not assumed absent. OSM is community data, not a license registry.
"""
from pathlib import Path

TAGS={"tobacco","e-cigarette","convenience"}

def extract_pbf(path,cities):
    import osmium
    wanted={city.casefold():city for city in cities}
    found={city:[] for city in cities}
    seen=set()
    class Collector(osmium.SimpleHandler):
        def record(self,obj,kind):
            tags=obj.tags
            if tags.get("shop") not in TAGS or not tags.get("name"):return
            city=wanted.get((tags.get("addr:city") or "").strip().casefold())
            if city is None:return
            key=(kind,int(obj.id))
            if key in seen:return
            seen.add(key)
            addr=" ".join(filter(None,[tags.get("addr:housenumber"),tags.get("addr:street")])) or None
            found[city].append({"name":tags.get("name"),"category":tags.get("shop"),
                "address_candidate":addr,"latitude":None,"longitude":None,
                "source":"OpenStreetMap Minnesota PBF","osm_id":int(obj.id),"osm_type":kind,
                "status":"UNVERIFIED_OSM_BUSINESS_CANDIDATE"})
        def node(self,n):self.record(n,"node")
        def way(self,w):self.record(w,"way")
        def relation(self,r):self.record(r,"relation")
    Collector().apply_file(str(Path(path)),locations=False)
    return found

def discovery_from_extract(city,records,error=None):
    if error:return {"status":"unavailable","candidates":[],"error":error,
        "errors":[{"source":"Minnesota PBF","error":error}],"endpoint_used":None,
        "coverage":"unavailable"}
    return {"status":"available" if records else "empty","candidates":records,
        "error":None,"errors":[],"endpoint_used":"Minnesota PBF",
        "coverage":"addr_city_tagged_only_not_exhaustive",
        "warning":"Missing addr:city tags are excluded. No license or operating status verified."}
