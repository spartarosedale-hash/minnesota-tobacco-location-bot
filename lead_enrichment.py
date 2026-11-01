"""Conservative automated enrichment of web-search leads.
A geocoded search snippet is NEVER evidence of an operating or licensed shop.
"""
import re
import requests

GEOCODER="https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
STREET=re.compile(r"\b\d{1,6}\s+(?:[A-Za-z0-9]+\s+){1,5}(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Blvd|Boulevard|Ln|Lane|Hwy|Highway|Way|Ct|Court)\b",re.I)
SHOP=re.compile(r"\b(tobacco|smoke\s*shop|vape|e-cigarette)\b",re.I)
VACANCY=re.compile(r"\b(for lease|retail space|vacant|available space)\b",re.I)

def enrich(leads,city,fetch=requests.get,limit=20):
    enriched=[]
    failures=[]
    for lead in leads[:limit]:
        text=" ".join((lead.get("title",""),lead.get("snippet","")))
        is_shop=bool(SHOP.search(text))
        is_vacancy=bool(VACANCY.search(text))
        if not (is_shop or is_vacancy):
            continue
        match=STREET.search(text)
        row=dict(lead)
        row["lead_type"]="possible_tobacco_business" if is_shop else "possible_vacancy"
        row["verification"]="UNVERIFIED_SEARCH_SNIPPET"
        row["latitude"]=None
        row["longitude"]=None
        row["address_candidate"]=None
        if match:
            address=match.group(0)+", "+city+", MN"
            row["address_candidate"]=address
            try:
                response=fetch(GEOCODER,params={"address":address,"benchmark":"Public_AR_Current","format":"json"},timeout=12)
                response.raise_for_status()
                matches=response.json().get("result",{}).get("addressMatches",[])
                if matches:
                    result=matches[0]
                    matched=result.get("matchedAddress","")
                    if city.casefold() in matched.casefold():
                        row["latitude"]=result["coordinates"]["y"]
                        row["longitude"]=result["coordinates"]["x"]
                        row["geocoded_address"]=matched
                        row["geocode_status"]="ADDRESS_RANGE_MATCH_NOT_BUSINESS_VERIFICATION"
                    else:
                        row["geocode_status"]="CITY_MISMATCH"
                else:
                    row["geocode_status"]="NO_ADDRESS_MATCH"
            except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
                row["geocode_status"]="ERROR"
                failures.append({"url":lead.get("url"),"error":str(exc)[:150]})
        else:
            row["geocode_status"]="NO_EXTRACTABLE_STREET_ADDRESS"
        enriched.append(row)
    return {"candidates":enriched,"errors":failures,
            "warning":"No business existence, license, opening status, or vacancy is verified from search snippets or Census address-range matches."}
