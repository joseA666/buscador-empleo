import re

import requests

import config

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PAGES = [0, 1]


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch():
    jobs = []
    for page in PAGES:
        params = {"page": page, "location": "Flexible / Remote"}
        if config.THEMUSE_API_KEY:
            params["api_key"] = config.THEMUSE_API_KEY
        try:
            resp = requests.get(
                "https://www.themuse.com/api/public/jobs",
                params=params,
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for item in data.get("results", []):
            job_id = str(item.get("id", ""))
            if not job_id:
                continue

            locations = ", ".join(l.get("name", "") for l in (item.get("locations") or []))

            jobs.append({
                "source": "themuse",
                "id": job_id,
                "title": item.get("name", ""),
                "company": (item.get("company") or {}).get("name", "Confidencial"),
                "location": locations or "Remoto",
                "url": (item.get("refs") or {}).get("landing_page", ""),
                "description": _strip_html(item.get("contents", ""))[:2000],
                "posted_at": item.get("publication_date", ""),
            })

    return jobs
