"""Classify all discovery leads without turning search results into verified businesses."""
import re
import requests

GEOCODER="https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
STREET=re.compile(r"\b\d{1,6}\s+(?:(?:[NSEW]|North|South|East|West)\s+)?(?:[\w.-]+\s+){1,6}?(?:St(?:reet)?|Ave(?:nue)?|Rd|Road|Dr(?:ive)?|Blvd|Boulevard|Ln|Lane|Hwy|Highway|Way|Ct|Court|Pkwy|Parkway)\b",re.I)
SHOP=re.compile(r"\b(tobacco|smoke\s*shop|smoke\s*store|vape|e[ -]?cigarette)\b",re.I)
VACANCY=re.compile(r"\b(for lease|for rent|retail space|vacan(?:t|cy)|available space|commercial lease)\b",re.I)
LICENSE=re.compile(r"\b(licens(?:e|ing)|permit|ordinance|council|renewal)\b",re.I)

def enrich(leads,city,fetch=requests.get,limit=40):
    candidates=[]
    errors=[]
    for lead in leads[:limit]:
        body=" ".join(str(lead.get(k) or "") for k in ("title","snippet"))
        query=str(lead.get("query") or "").lower()
        is_shop=bool(SHOP.search(body))
        is_vacancy=bool(VACANCY.search(body))
        is_license=bool(LICENSE.search(body))
        row=dict(lead)
        if is_vacancy: kind="possible_vacancy"
        elif is_shop: kind="possible_tobacco_business"
        elif is_license: kind="possible_licensing_source"
        else: kind="uncategorized_search_lead"
        row.update(lead_type=kind,verification="UNVERIFIED_SEARCH_LEAD",
                   latitude=None,longitude=None,address_candidate=None,
                   geocode_status="NO_EXTRACTABLE_STREET_ADDRESS")
        match=STREET.search(body)
        if match:
            address=match.group(0)+", "+city+", MN"
            row["address_candidate"]=address
            try:
                response=fetch(GEOCODER,params={"address":address,"benchmark":"Public_AR_Current","format":"json"},timeout=10)
                response.raise_for_status()
                matches=response.json().get("result",{}).get("addressMatches",[])
                if matches:
                    found=matches[0]
                    matched=found.get("matchedAddress","")
                    if city.casefold() in matched.casefold():
                        row["latitude"]=found["coordinates"]["y"]
                        row["longitude"]=found["coordinates"]["x"]
                        row["geocoded_address"]=matched
                        row["geocode_status"]="ADDRESS_RANGE_MATCH_NOT_BUSINESS_VERIFICATION"
                    else: row["geocode_status"]="CITY_MISMATCH"
                else: row["geocode_status"]="NO_ADDRESS_MATCH"
            except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
                row["geocode_status"]="ERROR"
                errors.append({"url":lead.get("url"),"error":str(exc)[:150]})
        candidates.append(row)
    return {"candidates":candidates,"errors":errors,
            "warning":"All leads remain unverified. Search-query wording does not prove a matching store or vacancy exists."}
