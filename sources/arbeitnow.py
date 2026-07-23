import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PAGES = 2


def fetch():
    jobs = []
    for page in range(1, PAGES + 1):
        try:
            resp = requests.get(
                "https://www.arbeitnow.com/api/job-board-api",
                params={"page": page},
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for item in data.get("data", []):
            jobs.append({
                "source": "arbeitnow",
                "id": item.get("slug", ""),
                "title": item.get("title", ""),
                "company": item.get("company_name", "Confidencial"),
                "location": "Remoto" if item.get("remote") else (item.get("location") or ""),
                "url": item.get("url", ""),
                "description": (item.get("description", "") or "")[:2000],
                "posted_at": str(item.get("created_at", "")),
            })

        if not data.get("links", {}).get("next"):
            break

    return jobs
