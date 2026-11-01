"""Official licensing evidence tracker. Counts are never inferred from search hits."""
import re
import requests
from bs4 import BeautifulSoup

PATTERNS={
 "active_license_holders":r"\b(\d{1,4})\s+(?:active|current|licensed)\s+(?:tobacco|retail tobacco)\s+(?:license\s*holders?|licenses?|retailers?)\b",
 "new_applications":r"\b(\d{1,4})\s+new\s+(?:tobacco\s+)?license\s+applications?\b",
}
def inspect_official_source(source,fetch=requests.get):
    row={"url":source["url"],"authority":source["name"],"status":"unavailable",
         "active_license_holders":None,"new_applications":None,"evidence":[]}
    try:
        r=fetch(source["url"],timeout=18,headers={"User-Agent":"MinnesotaRetailResearchBot/1.0"})
        r.raise_for_status()
        if "html" not in r.headers.get("Content-Type","").lower():
            row["status"]="non_html";return row
        soup=BeautifulSoup(r.text[:500000],"html.parser")
        for tag in soup(["script","style","nav","footer"]):tag.decompose()
        text=" ".join(soup.stripped_strings)
        row["status"]="page_read_no_explicit_counts"
        for field,pattern in PATTERNS.items():
            matches=list(re.finditer(pattern,text,re.I))
            if len(matches)==1:
                match=matches[0]
                row[field]=int(match.group(1))
                row["evidence"].append({"field":field,"quote":text[max(0,match.start()-65):match.end()+65]})
                row["status"]="candidate_counts_require_review"
    except (requests.RequestException,ValueError) as exc:
        row["error"]=str(exc)[:160]
    return row

def licensing_snapshot(sources,fetch=requests.get):
    records=[inspect_official_source(s,fetch) for s in sources]
    return {"sources":records,"verified_active_license_holders":None,
        "verified_new_applications":None,"verification":"Counts extracted from web pages are candidates only; official license rosters or dated municipal records must confirm them."}
