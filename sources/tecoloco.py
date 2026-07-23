import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

KEYWORDS = ["desarrollador", "programador", "laravel", "backend", "software", "sistemas"]


def fetch():
    jobs = []
    seen_ids = set()
    for keyword in KEYWORDS:
        try:
            resp = requests.get(
                "https://www.tecoloco.com.hn/empleos",
                params={"Keywords": keyword},
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        for card in soup.select(".job-card-mobile"):
            link_el = card.select_one("a.job-card-mobile__title, h2.job-card-mobile__title a")
            if not link_el:
                continue
            href = link_el.get("href", "")
            m = re.search(r"/(\d+)/", href)
            job_id = m.group(1) if m else href
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = link_el.get_text(strip=True)
            url = href if href.startswith("http") else f"https://www.tecoloco.com.hn{href}"

            company_el = card.select_one(".job-card-mobile__company-name")
            company = company_el.get_text(strip=True) if company_el else "Confidencial"

            location_el = card.select_one(".job-card-mobile__location")
            location = location_el.get_text(strip=True) if location_el else "Honduras"

            expiry_el = card.select_one(".job-card-mobile__expiry")
            expiry = expiry_el.get_text(strip=True) if expiry_el else ""

            jobs.append({
                "source": "tecoloco",
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "description": f"{title} - {company} - {location} - {expiry}",
                "posted_at": expiry,
            })

    return jobs
