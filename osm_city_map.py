"""Download small city OSM XML map slices instead of the full Minnesota PBF.

Nominatim supplies city bounds; OSM map API supplies nodes/ways in a capped box.
This is candidate discovery, not authoritative operating or licensing evidence.
"""
import xml.etree.ElementTree as ET
import requests

def discover_city_map(city,fetch=requests.get):
    headers={"User-Agent":"MinnesotaRetailResearchBot/1.0 (research; github.com/spartarosedale-hash/minnesota-tobacco-location-bot)"}
    try:
        r=fetch("https://nominatim.openstreetmap.org/search",params={
            "city":city,"state":"Minnesota","country":"United States","format":"jsonv2","limit":5},
            headers=headers,timeout=18)
        r.raise_for_status()
        places=r.json()
        places=[p for p in places if p.get("type") in ("administrative","city","town","village") and "Minnesota" in p.get("display_name","")]
        if not places:raise ValueError("No confirmed Minnesota city boundary found")
        south,north,west,east=map(float,places[0]["boundingbox"])
        # OSM API /map has a hard area limit. A bounded city-centre slice
        # avoids accidentally requesting a large county.
        lat=(south+north)/2
        lon=(west+east)/2
        half_lat=min((north-south)/2,0.025)
        half_lon=min((east-west)/2,0.035)
        bbox=f"{lon-half_lon:.5f},{lat-half_lat:.5f},{lon+half_lon:.5f},{lat+half_lat:.5f}"
        response=fetch("https://api.openstreetmap.org/api/0.6/map",
            params={"bbox":bbox},headers=headers,timeout=35)
        response.raise_for_status()
        root=ET.fromstring(response.content)
        results=[]
        for obj in root:
            if obj.tag not in ("node","way"):continue
            tags={t.attrib.get("k"):t.attrib.get("v") for t in obj.findall("tag")}
            if tags.get("shop") not in ("tobacco","e-cigarette","convenience") or not tags.get("name"):continue
            results.append({"name":tags["name"],"category":tags.get("shop"),
                "address_candidate":" ".join(filter(None,[tags.get("addr:housenumber"),tags.get("addr:street")])) or None,
                "latitude":float(obj.attrib["lat"]) if obj.tag=="node" and "lat" in obj.attrib else None,
                "longitude":float(obj.attrib["lon"]) if obj.tag=="node" and "lon" in obj.attrib else None,
                "source":"OpenStreetMap city map API","osm_id":int(obj.attrib["id"]),"osm_type":obj.tag,
                "status":"UNVERIFIED_OSM_BUSINESS_CANDIDATE"})
        return {"status":"available" if results else "empty","candidates":results,
            "error":None,"errors":[],"endpoint_used":"OpenStreetMap city map API",
            "coverage":"bounded_city_centre_slice_not_exhaustive",
            "bbox":bbox,"warning":"Only a bounded city-centre area was checked; no license or active operation verified."}
    except (requests.RequestException,ValueError,ET.ParseError,KeyError,TypeError) as exc:
        return {"status":"unavailable","candidates":[],"error":str(exc)[:200],
            "errors":[{"source":"city map API","error":str(exc)[:200]}],
            "endpoint_used":None,"coverage":"unavailable"}
