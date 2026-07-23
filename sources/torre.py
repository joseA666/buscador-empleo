import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Content-Type": "application/json"}

SIZE = 40


def fetch():
    try:
        resp = requests.post(
            "https://search.torre.co/opportunities/_search",
            headers=HEADERS,
            json={"size": SIZE, "aggregate": False, "sort": "creation-date",
                  "query": {"and": [{"term": {"remote": True}}]}},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    jobs = []
    for item in data.get("results", []):
        job_id = item.get("id")
        if not job_id:
            continue

        orgs = item.get("organizations") or []
        company = orgs[0].get("name", "Confidencial") if orgs else "Confidencial"

        locations = item.get("locations") or []
        location = ", ".join(locations) if locations else ("Remoto" if item.get("remote") else "")

        skills = ", ".join(s.get("name", "") for s in (item.get("skills") or []))
        description = f"{item.get('tagline', '')} Skills: {skills}".strip()

        jobs.append({
            "source": "torre",
            "id": str(job_id),
            "title": item.get("objective", ""),
            "company": company,
            "location": location or "Remoto",
            "url": f"https://torre.co/jobs/{job_id}",
            "description": description[:2000],
            "posted_at": item.get("created", ""),
        })

    return jobs
