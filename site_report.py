"""Address report: python site_report.py '231 N Sibley Ave, Litchfield, MN 55355'
Optional --competitors verified_competitors.csv. External API failures are disclosed.
"""
import argparse,json
from address_forecast import forecast
from traffic_and_competition import nearby_aadt,competitor_summary

def build(address,competitors=None):
    result=forecast(address)
    lat=result["site"]["latitude"];lon=result["site"]["longitude"]
    try:
        result["traffic"]=nearby_aadt(lat,lon)
    except Exception as exc:
        result["traffic"]={"status":"unavailable","reason":str(exc)[:250]}
    if competitors:
        try: result["competition"]=competitor_summary(lat,lon,competitors)
        except Exception as exc: result["competition"]={"status":"unavailable","reason":str(exc)[:250]}
    else:
        result["competition"]={"status":"not_assessed","reason":"No verified competitor geolocation dataset provided"}
    result["prediction_confidence"]="NOT CALIBRATED"
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("address")
    p.add_argument("--competitors")
    args=p.parse_args()
    print(json.dumps(build(args.address,args.competitors),indent=2))
