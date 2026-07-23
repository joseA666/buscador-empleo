import argparse
import time
from datetime import datetime

import config
import export
import matching
import notifier
import state
import sources


def run_once(dry_run: bool = False):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Buscando vacantes...")
    jobs = sources.fetch_all()
    print(f"  {len(jobs)} vacantes obtenidas de todas las fuentes")

    nuevas = 0
    candidates = []
    for job in jobs:
        if state.already_seen(job["source"], job["id"]):
            continue
        nuevas += 1

        if not matching.keyword_prefilter(job):
            state.mark_seen(job, notified=False, language=matching.detect_language(job))
            continue
        candidates.append(job)

    matches = []
    for i in range(0, len(candidates), config.GROQ_BATCH_SIZE):
        batch = candidates[i:i + config.GROQ_BATCH_SIZE]
        results = matching.llm_judge_batch(batch)
        for job, result in zip(batch, results):
            if result["match"]:
                print(f"  [MATCH] {job['title']} - {job['company']} ({job['source']})")
                matches.append({"job": job, "reason": result["reason"], "language": result["language"]})
                state.mark_seen(job, notified=True, reason=result["reason"], language=result["language"])
            else:
                state.mark_seen(job, notified=False, reason=result["reason"], language=result["language"])

    if matches and not dry_run:
        notifier.send_digest(matches)

    export.write_frontend_data()

    print(f"  {nuevas} vacantes nuevas revisadas, {len(matches)} notificadas en 1 correo" if matches else f"  {nuevas} vacantes nuevas revisadas, 0 notificadas")


def main():
    parser = argparse.ArgumentParser(description="Buscador de vacantes de empleo")
    parser.add_argument("--loop", action="store_true", help="Ejecuta en bucle continuo")
    parser.add_argument("--dry-run", action="store_true", help="No envia correos, solo muestra en consola")
    parser.add_argument("--test-email", action="store_true", help="Envia un correo de prueba y termina")
    args = parser.parse_args()

    state.init_db()

    if args.test_email:
        ok = notifier.send_test_email()
        print("Correo de prueba enviado." if ok else "Fallo el envio, revisa GMAIL_ADDRESS / GMAIL_APP_PASSWORD en .env")
        return

    if args.loop:
        print(f"Modo continuo: revisando cada {config.POLL_INTERVAL_MINUTES} minutos. Ctrl+C para detener.")
        while True:
            try:
                run_once(dry_run=args.dry_run)
            except Exception as exc:
                print(f"[error] fallo en el ciclo: {exc}")
            time.sleep(config.POLL_INTERVAL_MINUTES * 60)
    else:
        run_once(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
