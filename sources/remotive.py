import requests

import config
import state

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

CATEGORIES = ["software-dev"]


def fetch():
    # Remotive pide explicitamente no consultar su API mas de unas pocas veces al dia.
    if state.hours_since_last_fetch("remotive") < config.REMOTIVE_MIN_HOURS_BETWEEN_FETCH:
        return []

    jobs = []
    for category in CATEGORIES:
        try:
            resp = requests.get(
                "https://remotive.com/api/remote-jobs",
                params={"category": category},
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for item in data.get("jobs", []):
            jobs.append({
                "source": "remotive",
                "id": str(item.get("id", "")),
                "title": item.get("title", ""),
                "company": item.get("company_name", "Confidencial"),
                "location": item.get("candidate_required_location") or "Remoto",
                "url": item.get("url", ""),
                "description": (item.get("description", "") or "")[:2000],
                "posted_at": item.get("publication_date", ""),
            })

    state.mark_fetched("remotive")
    return jobs
