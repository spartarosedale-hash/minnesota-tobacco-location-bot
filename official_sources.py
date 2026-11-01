"""Official licensing authorities; authority pages are not license rosters.

Always attribute a county-issued license to the store's municipality, not the
entire county. An authority assignment is not proof of an active license.
"""
SOURCES={
 "Zimmerman":[{"name":"Sherburne County tobacco licensing","url":"https://www.co.sherburne.mn.us/205/Other-Licenses","kind":"official_licensing_authority","authority_level":"county","county":"Sherburne"}],
 "Litchfield":[{"name":"City of Litchfield licensing","url":"https://www.ci.litchfield.mn.us/2204/Licenses","kind":"official_licensing_authority","authority_level":"city","county":"Meeker"}],
}
# County licensing jurisdiction can differ by city; verify against current
# local ordinances and county licensing pages before treating as definitive.
AUTHORITY_CANDIDATES={
 "Otsego":{"authority_level":"county","county":"Wright","authority":"Wright County","verification":"JURISDICTION_REQUIRES_OFFICIAL_CONFIRMATION"},
}
def for_city(city):
    return [dict(x,city=city,licensee_list_available=False,verification="AUTHORITY_PAGE_ONLY") for x in SOURCES.get(city,[])]

def authority_for_city(city):
    if city in AUTHORITY_CANDIDATES:
        return dict(AUTHORITY_CANDIDATES[city],city=city)
    sources=for_city(city)
    if sources:
        return {"city":city,"authority_level":sources[0].get("authority_level","unknown"),
                "county":sources[0].get("county"),"authority":sources[0]["name"],
                "verification":"AUTHORITY_PAGE_ONLY"}
    return {"city":city,"authority_level":"unknown","county":None,
            "authority":None,"verification":"NOT_YET_RESEARCHED"}

def store_municipality(record):
    """Never assign all county licensees to the requested city."""
    return (record.get("physical_city") or record.get("premises_city") or "").strip().casefold()

def license_identity(record):
    """Dedup key; jurisdiction and business premises, not mailing city."""
    return (str(record.get("license_id") or "").strip().casefold(),
            str(record.get("premises_address") or "").strip().casefold(),
            store_municipality(record))
