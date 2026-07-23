import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def fetch():
    try:
        resp = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    jobs = []
    for item in data:
        if not isinstance(item, dict) or "id" not in item or "position" not in item:
            continue
        jobs.append({
            "source": "remoteok",
            "id": str(item["id"]),
            "title": item.get("position", ""),
            "company": item.get("company", "Confidencial"),
            "location": item.get("location") or "Remoto",
            "url": item.get("url") or item.get("apply_url", ""),
            "description": item.get("description", "")[:2000],
            "posted_at": item.get("date", ""),
        })
    return jobs
