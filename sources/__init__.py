from . import computrabajo, tecoloco, remoteok, jobicy, remotive, arbeitnow, weworkremotely, himalayas, torre

ALL_SOURCES = [computrabajo, tecoloco, remoteok, jobicy, remotive, arbeitnow, weworkremotely, himalayas, torre]


def fetch_all():
    jobs = []
    for module in ALL_SOURCES:
        try:
            jobs.extend(module.fetch())
        except Exception as exc:
            print(f"[aviso] fuente {module.__name__} fallo: {exc}")
    return jobs
