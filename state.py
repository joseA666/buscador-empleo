import sqlite3
from contextlib import closing

import config


def init_db():
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vacantes_vistas (
                source TEXT NOT NULL,
                job_id TEXT NOT NULL,
                title TEXT,
                url TEXT,
                notified INTEGER NOT NULL DEFAULT 0,
                first_seen TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (source, job_id)
            )
        """)
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(vacantes_vistas)")}
        for col, ddl in [
            ("company", "TEXT"),
            ("location", "TEXT"),
            ("description", "TEXT"),
            ("reason", "TEXT"),
            ("language", "TEXT"),
            ("posted_at", "TEXT"),
        ]:
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE vacantes_vistas ADD COLUMN {col} {ddl}")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fuente_ultima_consulta (
                source TEXT PRIMARY KEY,
                last_fetch TEXT NOT NULL
            )
        """)
        conn.commit()


def already_seen(source: str, job_id: str) -> bool:
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        row = conn.execute(
            "SELECT 1 FROM vacantes_vistas WHERE source = ? AND job_id = ?",
            (source, job_id),
        ).fetchone()
        return row is not None


def mark_seen(job: dict, notified: bool, reason: str = "", language: str = ""):
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO vacantes_vistas
               (source, job_id, title, url, notified, company, location, description, reason, language, posted_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job["source"], job["id"], job.get("title", ""), job.get("url", ""), int(notified),
                job.get("company", ""), job.get("location", ""), job.get("description", ""),
                reason, language, job.get("posted_at", ""),
            ),
        )
        conn.commit()


def recent_jobs(limit: int = 500) -> list[dict]:
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM vacantes_vistas ORDER BY first_seen DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def hours_since_last_fetch(source: str) -> float:
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        row = conn.execute(
            "SELECT (julianday('now') - julianday(last_fetch)) * 24 FROM fuente_ultima_consulta WHERE source = ?",
            (source,),
        ).fetchone()
        return row[0] if row else float("inf")


def mark_fetched(source: str):
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO fuente_ultima_consulta (source, last_fetch) VALUES (?, datetime('now')) "
            "ON CONFLICT(source) DO UPDATE SET last_fetch = datetime('now')",
            (source,),
        )
        conn.commit()
