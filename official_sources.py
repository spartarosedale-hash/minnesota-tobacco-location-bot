"""Verified public starting points for licensing research (not license-holder lists)."""
SOURCES={
 "Zimmerman":[{"name":"Sherburne County tobacco licensing","url":"https://www.co.sherburne.mn.us/205/Other-Licenses","kind":"official_licensing_authority"}],
 "Litchfield":[{"name":"City of Litchfield licensing","url":"https://www.ci.litchfield.mn.us/2204/Licenses","kind":"official_licensing_authority"}],
}
def for_city(city):
    return [dict(x,city=city,licensee_list_available=False,verification="AUTHORITY_PAGE_ONLY") for x in SOURCES.get(city,[])]
