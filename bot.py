"""Monitor authorized public Minnesota retail vacancy source pages for changes."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
HEADERS = {"User-Agent": "MinnesotaRetailVacancyMonitor/0.1"}
KEYWORDS = ("available", "vacant", "for lease", "retail space", "commercial space", "sq ft", "square feet")


def permitted(url):
    parts = urlparse(url)
    if parts.scheme != "https" or not parts.netloc:
        return False
    try:
        response = requests.get(f"{parts.scheme}://{parts.netloc}/robots.txt", headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return False
        robots = RobotFileParser()
        robots.parse(response.text.splitlines())
        return robots.can_fetch(HEADERS["User-Agent"], url)
    except requests.RequestException:
        return False


def main():
    with (ROOT / "sources.csv").open(encoding="utf-8", newline="") as handle:
        sources = list(csv.DictReader(handle))
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    seen_file = data_dir / "seen.json"
    seen = json.loads(seen_file.read_text()) if seen_file.exists() else {}
    findings = []
    for source in sources:
        url = source["url"].strip()
        if not permitted(url):
            print(f"Skipped (robots/URL): {url}")
            continue
        try:
            response = requests.get(url, headers=HEADERS, timeout=25)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
            page_text = " ".join(soup.stripped_strings)
            if not any(word in page_text.lower() for word in KEYWORDS):
                continue
            fingerprint = hashlib.sha256(page_text.encode()).hexdigest()
            if seen.get(url) != fingerprint:
                findings.append({"city": source["city"], "source": source["source_name"], "url": url, "status": "page changed - manual verification required", "checked_at": datetime.now(timezone.utc).isoformat()})
            seen[url] = fingerprint
        except requests.RequestException as exc:
            print(f"Could not fetch {url}: {exc}")
    seen_file.write_text(json.dumps(seen, indent=2) + "\n")
    (data_dir / "latest_findings.json").write_text(json.dumps(findings, indent=2) + "\n")
    print(f"Sources configured: {len(sources)}. Changed candidate pages: {len(findings)}.")


if __name__ == "__main__":
    main()
