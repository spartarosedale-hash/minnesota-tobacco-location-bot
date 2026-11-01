"""Reject search results that do not contain independent local evidence."""
import re
from urllib.parse import urlparse

BLOCKED={"microsoft.com","zimmermann.com","wikipedia.org","saksfifthavenue.com",
         "farfetch.com","net-a-porter.com","revolve.com","bergdorfgoodman.com"}
LOCAL_TERMS=re.compile(r"\b(MN|Minnesota|55398|55355|Sherburne|Meeker)\b",re.I)
TOPIC=re.compile(r"\b(tobacco|smoke shop|vape|retail|commercial|lease|licens(?:e|ing)|vacan(?:t|cy))\b",re.I)

def relevant(lead,city):
    host=(urlparse(lead.get("url","")).hostname or "").lower()
    if any(host==domain or host.endswith("."+domain) for domain in BLOCKED):return False
    text=" ".join(str(lead.get(k) or "") for k in ("title","snippet","url"))
    # Query text intentionally excluded: search terms are not evidence about a result.
    return bool(re.search(r"\b"+re.escape(city)+r"\b",text,re.I) and
                LOCAL_TERMS.search(text) and TOPIC.search(text))
