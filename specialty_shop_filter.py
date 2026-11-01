"""Conservative specialty smoke/vape/tobacco/cigar shop identification."""
import re

SPECIALTY_TAGS={"tobacco","e-cigarette","vape","cigars","cigar","hookah"}
NAME_PATTERN=re.compile(r"\b(?:smoke\s*shop|vape\s*shop|vapor\s*shop|tobacco(?:\s*shop|\s*store)?|cigar(?:s|\s*shop|\s*lounge)?|smoke\s*&\s*vape|vape|vapors?|smokes?)\b",re.I)
EXCLUDE_PATTERN=re.compile(r"\b(?:dispensary|cannabis|marijuana|liquor|gas station|fuel|pharmacy|wholesale)\b",re.I)

def specialty_match(tags):
    name=(tags.get("name") or "").strip()
    if not name or EXCLUDE_PATTERN.search(name):return None
    category=(tags.get("shop") or "").strip().lower()
    if category in SPECIALTY_TAGS:return "specialty_osm_tag"
    if category in ("convenience","kiosk","newsagent","general","yes","") and NAME_PATTERN.search(name):
        return "specialty_name_match"
    return None
