import re

import requests

import config
import state

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch():
    # El thread mensual trae cientos de comentarios; se throttlea para no
    # re-descargar el arbol completo en cada corrida de 15 min.
    if state.hours_since_last_fetch("hn_whoishiring") < config.HN_WHOISHIRING_MIN_HOURS_BETWEEN_FETCH:
        return []

    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search_by_date",
            params={"tags": "story,author_whoishiring", "query": "Who is hiring", "hitsPerPage": 1},
            headers=HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        if not hits:
            return []
        thread_id = hits[0]["objectID"]

        resp = requests.get(
            f"https://hn.algolia.com/api/v1/items/{thread_id}", headers=HEADERS, timeout=30
        )
        resp.raise_for_status()
        thread = resp.json()
    except (requests.RequestException, ValueError, KeyError):
        return []

    jobs = []
    for comment in thread.get("children") or []:
        if comment.get("dead") or comment.get("deleted"):
            continue
        text = _strip_html(comment.get("text", ""))
        comment_id = comment.get("id")
        if not text or not comment_id:
            continue

        # Formato habitual: "Empresa | Ubicacion | Puesto | Remote". Si no
        # trae separadores, se usa el arranque del texto como titulo.
        titulo = text.split(" | ")[0][:150].strip() if " | " in text[:200] else text[:120].strip()

        jobs.append({
            "source": "hn_whoishiring",
            "id": str(comment_id),
            "title": titulo or "Vacante (HN Who's Hiring)",
            "company": "Ver descripcion",
            "location": "Remoto" if "remote" in text.lower() else "Ver descripcion",
            "url": f"https://news.ycombinator.com/item?id={comment_id}",
            "description": text[:2000],
            "posted_at": comment.get("created_at", ""),
        })

    state.mark_fetched("hn_whoishiring")
    return jobs
