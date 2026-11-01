"""Read candidate source pages and retain evidence without asserting business is open."""
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def verify_candidates(candidates,fetch=requests.get,max_pages=12):
    results=[]
    errors=[]
    for candidate in candidates[:max_pages]:
        row=dict(candidate)
        url=row.get("url","")
        host=urlparse(url)
        row["evidence_status"]="SOURCE_NOT_CHECKED"
        row["operating_status"]="UNKNOWN"
        row["license_status"]="UNKNOWN"
        if host.scheme!="https" or not host.hostname or host.hostname in ("localhost",) or host.hostname.endswith((".local",".internal")):
            row["evidence_status"]="INVALID_SOURCE_URL"
            results.append(row)
            continue
        try:
            response=fetch(url,timeout=12,headers={"User-Agent":"MinnesotaRetailResearch/1.0"})
            response.raise_for_status()
            if "html" not in response.headers.get("Content-Type","").lower():
                row["evidence_status"]="NON_HTML_SOURCE"
            else:
                soup=BeautifulSoup(response.text[:300000],"html.parser")
                for element in soup(["script","style","nav","footer"]): element.decompose()
                body=" ".join(soup.stripped_strings).casefold()
                address=row.get("address_candidate")
                street=address.split(",")[0].casefold() if address else ""
                name=(row.get("title") or "").casefold()
                row["evidence_status"]="SOURCE_READ"
                row["address_mentioned_in_source"]=bool(street and street in body)
                row["title_mentioned_in_source"]=bool(name and name in body)
                if row["address_mentioned_in_source"]:
                    row["evidence_status"]="SOURCE_MENTIONS_ADDRESS_UNVERIFIED"
            row["source_checked"]=True
        except (requests.RequestException,ValueError) as exc:
            row["evidence_status"]="SOURCE_UNAVAILABLE"
            errors.append({"url":url,"error":str(exc)[:120]})
        results.append(row)
    return {"candidates":results,"errors":errors,"policy":"Source text and geocoding alone do not confirm a current license, operating shop, or active vacancy."}
