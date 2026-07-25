import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# Red de sitios Computrabajo (misma plataforma/HTML en todos los paises). Honduras
# se busca sin filtro remoto porque el candidato tambien aplica presencial ahi; el
# resto son mercados donde solo interesa remoto amigable con LatAm.
_LATAM_TERMS = ("desarrollador", "programador", "laravel", "backend")

SITES = {
    "computrabajo": (
        "https://hn.computrabajo.com",
        [
            "trabajo-de-desarrollador-en-francisco-morazan",
            "trabajo-de-programador-en-francisco-morazan",
            "trabajo-de-laravel",
            "trabajo-de-backend",
        ],
        "Honduras",
    ),
    "computrabajo_mx": (
        "https://mx.computrabajo.com",
        [f"trabajo-de-{t}-en-remoto" for t in _LATAM_TERMS],
        "México",
    ),
    "computrabajo_co": (
        "https://co.computrabajo.com",
        [f"trabajo-de-{t}-en-remoto" for t in _LATAM_TERMS],
        "Colombia",
    ),
    "computrabajo_pe": (
        "https://pe.computrabajo.com",
        [f"trabajo-de-{t}-en-remoto" for t in _LATAM_TERMS],
        "Perú",
    ),
    "computrabajo_pa": (
        "https://pa.computrabajo.com",
        [f"trabajo-de-{t}-en-remoto" for t in _LATAM_TERMS],
        "Panamá",
    ),
}


def _fetch_site(source: str, base_url: str, slugs: list[str], location_fallback: str) -> list[dict]:
    jobs = []
    seen_ids = set()
    for slug in slugs:
        try:
            resp = requests.get(f"{base_url}/{slug}", headers=HEADERS, timeout=20)
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
            url = href if href.startswith("http") else f"{base_url}{href.split('#')[0]}"

            company_el = article.select_one("a[offer-grid-article-company-url]")
            company = company_el.get_text(strip=True) if company_el else "Confidencial"

            # El primer "p.fs16.fc_base.mt5" suele ser el de la calificacion de la
            # empresa (ej. "4.2"), no la ubicacion; se excluye con :not(.dFlex) para
            # no confundir el rating con la ubicacion real (le pasaba a sitios como
            # mx.computrabajo.com donde casi todas las empresas tienen rating).
            location_el = article.select_one("p.fs16.fc_base.mt5:not(.dFlex) span")
            location = location_el.get_text(strip=True) if location_el else location_fallback

            modality_el = article.select_one(".fs13.mt15 span.dIB")
            modality = modality_el.get_text(strip=True) if modality_el else ""

            posted_el = article.select_one("p.fs13.fc_aux.mt15")
            posted = re.sub(r"\s+", " ", posted_el.get_text(strip=True)) if posted_el else ""

            jobs.append({
                "source": source,
                "id": job_id,
                "title": title,
                "company": company,
                "location": f"{location} ({modality})" if modality else location,
                "url": url,
                "description": f"{title} - {company} - {location} - {modality} - Publicado: {posted}",
                "posted_at": posted,
            })

    return jobs


def fetch():
    jobs = []
    for source, (base_url, slugs, location_fallback) in SITES.items():
        jobs.extend(_fetch_site(source, base_url, slugs, location_fallback))
    return jobs
