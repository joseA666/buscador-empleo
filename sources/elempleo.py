import html
import json
import re

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

SEARCH_SLUGS = [
    "trabajo-desarrollador-backend-modalidad-remoto",
    "trabajo-programador-modalidad-remoto",
    "trabajo-laravel",
    "trabajo-python-modalidad-remoto",
]

# Cada oferta trae su propio JSON en el atributo data-ga4-offerdata del div
# contenedor, mas confiable que encadenar selectores CSS.
ITEM_RE = re.compile(r'data-url="([^"]+)" data-ga4-offerdata="([^"]+)"')


def fetch():
    jobs = []
    seen_ids = set()
    for slug in SEARCH_SLUGS:
        try:
            resp = requests.get(f"https://www.elempleo.com/co/ofertas-empleo/{slug}", headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException:
            continue

        for path, raw_data in ITEM_RE.findall(resp.text):
            try:
                data = json.loads(html.unescape(raw_data))
            except ValueError:
                continue

            job_id = str(data.get("id") or "")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = data.get("title", "")
            company = data.get("company") or "Confidencial"
            location = data.get("location") or "Colombia"
            salary = data.get("salary", "")

            jobs.append({
                "source": "elempleo",
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "url": f"https://www.elempleo.com{path}",
                "description": f"{title} - {company} - {location} - {salary}".strip(" -"),
                "posted_at": "",
            })

    return jobs
