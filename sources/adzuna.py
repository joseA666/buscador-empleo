import requests

import config
import state

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# Un query fijo y modesto por pais: con el throttle de config esto se queda
# muy por debajo de las 1000 llamadas/mes gratis de Adzuna.
QUERIES = [
    ("mx", "desarrollador backend"),
    ("us", "remote backend developer"),
]


def fetch():
    if not config.ADZUNA_APP_ID or not config.ADZUNA_APP_KEY:
        return []
    if state.hours_since_last_fetch("adzuna") < config.ADZUNA_MIN_HOURS_BETWEEN_FETCH:
        return []

    jobs = []
    for country, query in QUERIES:
        try:
            resp = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params={
                    "app_id": config.ADZUNA_APP_ID,
                    "app_key": config.ADZUNA_APP_KEY,
                    "results_per_page": 20,
                    "what": query,
                    "content-type": "application/json",
                },
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

            jobs.append({
                "source": "adzuna",
                "id": job_id,
                "title": item.get("title", ""),
                "company": (item.get("company") or {}).get("display_name", "Confidencial"),
                "location": (item.get("location") or {}).get("display_name", "") or "Remoto",
                "url": item.get("redirect_url", ""),
                "description": (item.get("description", "") or "")[:2000],
                "posted_at": item.get("created", ""),
            })

    state.mark_fetched("adzuna")
    return jobs
