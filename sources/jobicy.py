import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def fetch():
    try:
        resp = requests.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": 50},
            headers=HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    jobs = []
    for item in data.get("jobs", []):
        jobs.append({
            "source": "jobicy",
            "id": str(item.get("id", item.get("jobSlug", ""))),
            "title": item.get("jobTitle", ""),
            "company": item.get("companyName", "Confidencial"),
            "location": item.get("jobGeo") or "Remoto",
            "url": item.get("url", ""),
            "description": (item.get("jobExcerpt", "") or "")[:2000],
            "posted_at": item.get("pubDate", ""),
        })
    return jobs
