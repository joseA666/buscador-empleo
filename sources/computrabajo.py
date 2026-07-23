import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

SEARCH_URLS = [
    "https://hn.computrabajo.com/trabajo-de-desarrollador-en-francisco-morazan",
    "https://hn.computrabajo.com/trabajo-de-programador-en-francisco-morazan",
    "https://hn.computrabajo.com/trabajo-de-laravel",
    "https://hn.computrabajo.com/trabajo-de-backend",
]


def fetch():
    jobs = []
    seen_ids = set()
    for search_url in SEARCH_URLS:
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        for article in soup.select("article.box_offer"):
            job_id = article.get("data-id")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title_el = article.select_one("a.js-o-link")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            url = href if href.startswith("http") else f"https://hn.computrabajo.com{href.split('#')[0]}"

            company_el = article.select_one("a[offer-grid-article-company-url]")
            company = company_el.get_text(strip=True) if company_el else "Confidencial"

            location_el = article.select_one("p.fs16.fc_base.mt5 span")
            location = location_el.get_text(strip=True) if location_el else "Honduras"

            modality_el = article.select_one(".fs13.mt15 span.dIB")
            modality = modality_el.get_text(strip=True) if modality_el else ""

            posted_el = article.select_one("p.fs13.fc_aux.mt15")
            posted = re.sub(r"\s+", " ", posted_el.get_text(strip=True)) if posted_el else ""

            jobs.append({
                "source": "computrabajo",
                "id": job_id,
                "title": title,
                "company": company,
                "location": f"{location} ({modality})" if modality else location,
                "url": url,
                "description": f"{title} - {company} - {location} - {modality} - Publicado: {posted}",
                "posted_at": posted,
            })

    return jobs
