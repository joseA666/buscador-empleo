import json
import os
import re
from datetime import datetime, timezone

import state

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")

SOURCE_LABELS = {
    "computrabajo": "Computrabajo Honduras",
    "tecoloco": "Tecoloco Honduras",
    "remoteok": "RemoteOK",
    "jobicy": "Jobicy",
    "remotive": "Remotive",
    "arbeitnow": "Arbeitnow",
    "weworkremotely": "We Work Remotely",
    "himalayas": "Himalayas",
    "torre": "Torre",
}


def _clean_snippet(text: str, limit: int = 280) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def write_frontend_data(limit: int = 1000):
    os.makedirs(DOCS_DIR, exist_ok=True)
    rows = state.recent_jobs(limit=limit)

    jobs = [{
        "source": row["source"],
        "source_label": SOURCE_LABELS.get(row["source"], row["source"]),
        "title": row["title"],
        "company": row["company"],
        "location": row["location"],
        "url": row["url"],
        "description": _clean_snippet(row["description"]),
        "reason": row["reason"] or "",
        "language": row["language"] or "other",
        "posted_at": row["posted_at"] or "",
        "notified": bool(row["notified"]),
        "first_seen": row["first_seen"],
    } for row in rows]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(jobs),
        "jobs": jobs,
    }

    with open(os.path.join(DOCS_DIR, "jobs.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
