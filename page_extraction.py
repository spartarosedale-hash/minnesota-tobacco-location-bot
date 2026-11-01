"""Extract candidate street addresses and structured business hints from fetched HTML."""
import json,re
from bs4 import BeautifulSoup

ADDRESS=re.compile(r"\b\d{1,6}\s+(?:(?:N|S|E|W|North|South|East|West)\s+)?(?:[A-Za-z0-9.-]+\s+){1,6}?(?:St(?:reet)?|Ave(?:nue)?|Rd|Road|Dr(?:ive)?|Blvd|Boulevard|Ln|Lane|Hwy|Highway|Way|Ct|Court|Pkwy|Parkway)\b",re.I)
RELEVANT=re.compile(r"\b(tobacco|smoke shop|vape|retail|for lease|vacant|license)\b",re.I)

def extract(html,city):
    soup=BeautifulSoup(html,"html.parser")
    candidates=[]
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            raw=json.loads(script.string or script.get_text())
            nodes=raw if isinstance(raw,list) else [raw]
            for node in nodes:
                if not isinstance(node,dict):continue
                if isinstance(node.get("@graph"),list):nodes.extend(node["@graph"])
                address=node.get("address")
                if isinstance(address,dict):
                    street=address.get("streetAddress","")
                    locality=address.get("addressLocality","")
                    if street and locality.casefold()==city.casefold() and ADDRESS.search(street):
                        candidates.append({"address":street,"name":node.get("name"),"evidence":"JSON_LD_ADDRESS"})
        except (ValueError,TypeError):pass
    for tag in soup(["script","style","nav","footer"]):tag.decompose()
    text=" ".join(soup.stripped_strings)
    if city.casefold() in text.casefold() and RELEVANT.search(text):
        for match in list(ADDRESS.finditer(text))[:12]:
            candidates.append({"address":match.group(0),"name":None,"evidence":"PAGE_TEXT_ADDRESS"})
    seen=set()
    unique=[]
    for item in candidates:
        key=item["address"].casefold()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:12]
