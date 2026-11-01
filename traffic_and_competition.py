"""Enrich a geocoded location with MnDOT observed AADT and competitor distances.
Traffic is a nearby segment measurement, NOT guaranteed frontage traffic.
Competitor CSV columns: name,latitude,longitude,verified_tobacco_sales
"""
import csv
import math
import requests

AADT_URL="https://services.arcgis.com/rD2ylXRs80UroD90/ArcGIS/rest/services/MnDOT_AADTWithCommercial/FeatureServer/43/query"

def miles(lat1,lon1,lat2,lon2):
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=a2-a1
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 3958.7613*2*math.asin(min(1,math.sqrt(a)))

def _segment_distance_m(lat, lon, geometry):
    """Approximate shortest ground distance from point to a WGS84 road polyline."""
    paths = (geometry or {}).get("paths", [])
    if not paths:
        return None
    scale_x = 111320 * math.cos(math.radians(lat))
    scale_y = 111195
    best = float("inf")
    for path in paths:
        coords = [((p[0] - lon) * scale_x, (p[1] - lat) * scale_y) for p in path]
        for index, (x, y) in enumerate(coords):
            best = min(best, math.hypot(x, y))
            if index == 0:
                continue
            ax, ay = coords[index - 1]
            dx, dy = x - ax, y - ay
            t = max(0, min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy))) if dx * dx + dy * dy else 0
            best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return round(best, 1) if best != float("inf") else None

def nearby_aadt(lat,lon,radius_meters=750):
    params={"f":"json","geometry":f"{lon},{lat}","geometryType":"esriGeometryPoint",
            "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
            "distance":radius_meters,"units":"esriSRUnit_Meter",
            "outFields":"AADT_CURRENT_VOLUME,AADT_CURRENT_YEAR,AADT_ROUTE_LABEL,AADT_LOCATION_DESCRIPTION",
            "returnGeometry":"true","outSR":"4326"}
    response=requests.get(AADT_URL,params=params,timeout=25)
    response.raise_for_status()
    payload=response.json()
    if "error" in payload:
        raise RuntimeError(str(payload["error"]))
    found=[]
    for feature in payload.get("features",[]):
        attrs=feature["attributes"]
        if isinstance(attrs.get("AADT_CURRENT_VOLUME"),(int,float)) and attrs["AADT_CURRENT_VOLUME"]>0:
            found.append({"aadt":attrs["AADT_CURRENT_VOLUME"],"year":attrs.get("AADT_CURRENT_YEAR"),"segment":attrs.get("AADT_ROUTE_LABEL"),"road_description":attrs.get("AADT_LOCATION_DESCRIPTION"),"distance_to_site_meters":_segment_distance_m(lat,lon,feature.get("geometry"))})
    found.sort(key=lambda item: (item["distance_to_site_meters"] is None, item["distance_to_site_meters"] if item["distance_to_site_meters"] is not None else float("inf"), -(item["year"] or 0)))
    nearest = found[0] if found and found[0]["distance_to_site_meters"] is not None else None
    return {"status":"nearby_segments_found" if found else "no_segments_found","nearest_candidate":nearest,"frontage_verified":False,"frontage_note":"Nearest mapped AADT segment is only a candidate. Road access, site frontage and most recent official count must be verified in MnDOT TCDS/EMMA.","nearby_segments":found,"search_radius_meters":radius_meters,"source_url":AADT_URL,"source_note":"Public ArcGIS MnDOT-derived layer, last data edit June 2024; not guaranteed current official AADT",
            "caution":"Nearby road segments only; frontage segment not yet verified"}

def competitor_summary(lat,lon,csv_path):
    within={1:0,3:0,5:0}
    considered=0
    with open(csv_path,newline="",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("verified_tobacco_sales","").strip().lower() not in ("yes","true","1"):
                continue
            distance=miles(lat,lon,float(row["latitude"]),float(row["longitude"]))
            considered+=1
            for radius in within:
                if distance<=radius: within[radius]+=1
    return {"verified_competitors_within_miles":within,"total_verified_in_file":considered,
            "caution":"Counts only verified businesses supplied in the input file; not a complete competitor census"}
