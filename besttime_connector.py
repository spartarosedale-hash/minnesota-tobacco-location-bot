"""BestTime nearby-venue relative busyness connector.
Requires BESTTIME_PRIVATE_KEY. No paid requests without explicit --enable-api flag.
Venue filter returns relative (0-100) peak-normalized busyness, NOT visitor counts.
"""
import argparse,json,os,requests
from traffic_and_competition import miles

URL="https://besttime.app/api/v1/venues/filter"
def fetch_nearby(lat,lon,radius_miles=3,enable_api=False):
    if not enable_api:
        return {"status":"disabled","reason":"Paid API calls require --enable-api"}
    key=os.environ.get("BESTTIME_PRIVATE_KEY")
    if not key:
        return {"status":"missing_credentials","reason":"Set BESTTIME_PRIVATE_KEY in GitHub Actions secrets or environment"}
    if not (0<radius_miles<=10):
        raise ValueError("radius_miles must be between 0 and 10")
    params={"api_key_private":key,"lat":lat,"lng":lon,
            "radius":round(radius_miles*1609.344),"foot_traffic":"day",
            "limit":100,"page":0}
    response=requests.get(URL,params=params,timeout=35)
    response.raise_for_status()
    payload=response.json()
    if payload.get("status")!="OK":
        raise RuntimeError("BestTime API returned non-OK status")
    venues=[]
    for v in payload.get("venues",[]):
        try:
            distance=miles(lat,lon,float(v["venue_lat"]),float(v["venue_lng"]))
        except (KeyError,TypeError,ValueError):
            continue
        if distance>radius_miles:continue
        raw=v.get("day_raw_whole")
        if not isinstance(raw,list):raw=v.get("day_raw")
        raw=[x for x in raw if isinstance(x,(int,float)) and 0<=x<=100] if isinstance(raw,list) else []
        venues.append({"name":v.get("venue_name"),"address":v.get("venue_address"),
            "type":v.get("venue_type") or (v.get("venue_info") or {}).get("venue_type"),
            "distance_miles":round(distance,2),
            "relative_busyness_mean":round(sum(raw)/len(raw),1) if raw else None,
            "relative_busyness_peak":max(raw) if raw else None,
            "absolute_visits":None,"source":"besttime_relative_busyness"})
    return {"status":"ok","venues":venues,"count":len(venues),
        "coverage":"provider_results_not_exhaustive",
        "warning":"Busyness is normalized to each venue's own peak; values are NOT comparable absolute customer volumes. Do not sum relative busyness across venues."}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--lat",type=float,required=True)
    p.add_argument("--lon",type=float,required=True)
    p.add_argument("--radius",type=float,default=3)
    p.add_argument("--enable-api",action="store_true")
    a=p.parse_args()
    print(json.dumps(fetch_nearby(a.lat,a.lon,a.radius,a.enable_api),indent=2))
