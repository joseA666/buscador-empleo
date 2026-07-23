import hashlib
import re
import xml.etree.ElementTree as ET

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

FEEDS = [
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
]


def fetch():
    jobs = []
    for feed_url in FEEDS:
        try:
            resp = requests.get(feed_url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except (requests.RequestException, ET.ParseError):
            continue

        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not title or not link:
                continue
            job_id = hashlib.sha1(link.encode()).hexdigest()[:16]
            description = re.sub(r"<[^>]+>", " ", item.findtext("description") or "")
            description = re.sub(r"\s+", " ", description).strip()[:2000]
            region = (item.findtext("region") or "Remoto").strip()

            # WWR titulos suelen venir como "Empresa: Puesto"
            if ":" in title:
                company, _, role = title.partition(":")
                company, role = company.strip(), role.strip()
            else:
                company, role = "Confidencial", title

            jobs.append({
                "source": "weworkremotely",
                "id": job_id,
                "title": role or title,
                "company": company,
                "location": region,
                "url": link,
                "description": description,
                "posted_at": (item.findtext("pubDate") or "").strip(),
            })

    return jobs
