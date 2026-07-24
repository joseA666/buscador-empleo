import hashlib

import requests

import config
import state

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Content-Type": "application/json"}

QUERIES = [
    {"keywords": "backend developer", "location": "remote"},
    {"keywords": "desarrollador", "location": "Honduras"},
]


def fetch():
    if not config.JOOBLE_API_KEY:
        return []
    if state.hours_since_last_fetch("jooble") < config.JOOBLE_MIN_HOURS_BETWEEN_FETCH:
        return []

    jobs = []
    for query in QUERIES:
        try:
            resp = requests.post(
                f"https://jooble.org/api/{config.JOOBLE_API_KEY}",
                headers=HEADERS,
                json=query,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for item in data.get("jobs", []):
            link = item.get("link", "")
            if not link:
                continue
            job_id = str(item.get("id") or hashlib.sha1(link.encode()).hexdigest()[:16])

            jobs.append({
                "source": "jooble",
                "id": job_id,
                "title": item.get("title", ""),
                "company": item.get("company") or "Confidencial",
                "location": item.get("location") or "Remoto",
                "url": link,
                "description": (item.get("snippet", "") or "")[:2000],
                "posted_at": item.get("updated", ""),
            })

    state.mark_fetched("jooble")
    return jobs
