"""Google Maps city-area search plan; links are manual research aids, not scraped results."""
from urllib.parse import quote

SEARCH_TERMS=("tobacco shop","smoke shop","vape shop","cigar shop")

def google_maps_search_plan(city,state="MN"):
    return [{"term":term,"city":city,"url":"https://www.google.com/maps/search/?api=1&query="+quote(f"{term} in {city}, {state}"),"status":"MANUAL_MAP_REVIEW_REQUIRED"} for term in SEARCH_TERMS]

def deduplicate_businesses(records):
    """Combine multiple search categories when the physical business matches."""
    unique={}
    for row in records:
        name=" ".join((row.get("name") or "").casefold().split())
        address=" ".join((row.get("address") or "").casefold().split())
        place_id=row.get("place_id")
        key=("place_id",place_id) if place_id else ("address_name",address,name)
        if not place_id and (not name or not address):
            key=("unresolved",len(unique))
        if key not in unique:
            unique[key]=dict(row,matched_search_terms=list(row.get("matched_search_terms",[])))
        else:
            for term in row.get("matched_search_terms",[]):
                if term not in unique[key]["matched_search_terms"]:
                    unique[key]["matched_search_terms"].append(term)
    return list(unique.values())
