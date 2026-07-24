import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

CATEGORIES = ["programming", "devops"]


def fetch():
    jobs = []
    seen_ids = set()
    for category in CATEGORIES:
        try:
            resp = requests.get(
                "https://remotejobs.org/api/v1/jobs",
                params={"category": category, "limit": 50},
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for item in data.get("data", []):
            job_id = str(item.get("id", ""))
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            company = (item.get("company") or {}).get("name", "Confidencial")

            jobs.append({
                "source": "remotejobsorg",
                "id": job_id,
                "title": item.get("title", ""),
                "company": company,
                "location": item.get("location") or "Remoto",
                "url": item.get("apply_url") or item.get("url", ""),
                "description": (item.get("description", "") or "")[:2000],
                "posted_at": item.get("posted_at", ""),
            })

    return jobs
