import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

KEYWORDS = [
    "backend developer",
    "laravel",
    "python developer",
    "golang developer",
    "full stack developer",
    "AI engineer",
]


def fetch():
    jobs = []
    seen_ids = set()
    for keyword in KEYWORDS:
        try:
            resp = requests.get(
                "https://himalayas.app/jobs/api/search",
                params={"q": keyword, "limit": 20},
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for item in data.get("jobs", []):
            job_id = item.get("guid") or item.get("applicationLink", "")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            locations = item.get("locationRestrictions") or []
            location = ", ".join(locations) if locations else "Remoto (mundial)"

            jobs.append({
                "source": "himalayas",
                "id": job_id,
                "title": item.get("title", ""),
                "company": item.get("companyName", "Confidencial"),
                "location": location,
                "url": item.get("applicationLink", ""),
                "description": (item.get("excerpt") or item.get("description", "") or "")[:2000],
                "posted_at": str(item.get("pubDate", "")),
            })

    return jobs
