"""Enrich a geocoded location with MnDOT observed AADT and competitor distances.
Traffic is a nearby segment measurement, NOT guaranteed frontage traffic.
Competitor CSV columns: name,latitude,longitude,verified_tobacco_sales
"""
import csv
import math
import requests

AADT_URL="https://dotapp9.dot.state.mn.us/egis12/rest/services/TFA/MNDOT_TRAFFIC_DATA/MapServer/6/query"

def miles(lat1,lon1,lat2,lon2):
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=a2-a1
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 3958.7613*2*math.asin(min(1,math.sqrt(a)))

def nearby_aadt(lat,lon,radius_meters=750):
    params={"f":"json","geometry":f"{lon},{lat}","geometryType":"esriGeometryPoint",
            "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
            "distance":radius_meters,"units":"esriSRUnit_Meter",
            "outFields":"CURRENT_VOLUME,CURRENT_YEAR,SEQUENCE_NUMBER",
            "returnGeometry":"false"}
    response=requests.get(AADT_URL,params=params,timeout=25)
    response.raise_for_status()
    payload=response.json()
    if "error" in payload:
        raise RuntimeError(str(payload["error"]))
    found=[]
    for feature in payload.get("features",[]):
        attrs=feature["attributes"]
        if isinstance(attrs.get("CURRENT_VOLUME"),(int,float)) and attrs["CURRENT_VOLUME"]>0:
            found.append({"aadt":attrs["CURRENT_VOLUME"],"year":attrs.get("CURRENT_YEAR"),"segment":attrs.get("SEQUENCE_NUMBER")})
    return {"nearby_segments":found,"search_radius_meters":radius_meters,
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
