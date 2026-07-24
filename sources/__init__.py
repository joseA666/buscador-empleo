from . import (
    computrabajo, tecoloco, remoteok, jobicy, remotive, arbeitnow, himalayas, torre,
    remotejobsorg, hn_whoishiring, adzuna, jooble, themuse,
)

ALL_SOURCES = [
    computrabajo, tecoloco, remoteok, jobicy, remotive, arbeitnow, himalayas, torre,
    remotejobsorg, hn_whoishiring, adzuna, jooble, themuse,
]


def fetch_all():
    jobs = []
    for module in ALL_SOURCES:
        try:
            jobs.extend(module.fetch())
        except Exception as exc:
            print(f"[aviso] fuente {module.__name__} fallo: {exc}")
    return jobs
