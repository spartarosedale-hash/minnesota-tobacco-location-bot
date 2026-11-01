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

def nearby_aadt(lat,lon,radius_meters=750):
    params={"f":"json","geometry":f"{lon},{lat}","geometryType":"esriGeometryPoint",
            "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
            "distance":radius_meters,"units":"esriSRUnit_Meter",
            "outFields":"AADT_CURRENT_VOLUME,AADT_CURRENT_YEAR,AADT_ROUTE_LABEL,AADT_LOCATION_DESCRIPTION",
            "returnGeometry":"false"}
    response=requests.get(AADT_URL,params=params,timeout=25)
    response.raise_for_status()
    payload=response.json()
    if "error" in payload:
        raise RuntimeError(str(payload["error"]))
    found=[]
    for feature in payload.get("features",[]):
        attrs=feature["attributes"]
        if isinstance(attrs.get("AADT_CURRENT_VOLUME"),(int,float)) and attrs["AADT_CURRENT_VOLUME"]>0:
            found.append({"aadt":attrs["CURRENT_VOLUME"],"year":attrs.get("AADT_CURRENT_YEAR"),"segment":attrs.get("AADT_ROUTE_LABEL"),"road_description":attrs.get("AADT_LOCATION_DESCRIPTION")})
    return {"nearby_segments":found,"search_radius_meters":radius_meters,"source_url":AADT_URL,"source_note":"Public ArcGIS MnDOT-derived layer, last data edit June 2024; not guaranteed current official AADT",
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
