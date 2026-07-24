import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

SOURCE_LABELS = {
    "computrabajo": "Computrabajo Honduras",
    "tecoloco": "Tecoloco Honduras",
    "remoteok": "RemoteOK",
    "jobicy": "Jobicy",
    "remotive": "Remotive",
    "arbeitnow": "Arbeitnow",
    "himalayas": "Himalayas",
    "torre": "Torre",
    "remotejobsorg": "RemoteJobs.org",
    "hn_whoishiring": "HN Who's Hiring",
    "adzuna": "Adzuna",
    "jooble": "Jooble",
    "themuse": "The Muse",
}

LANGUAGE_LABELS = {"es": "Espanol", "en": "Ingles", "other": ""}


def _language_rank(language: str) -> int:
    try:
        return config.LANGUAGE_PRIORITY.index(language)
    except ValueError:
        return len(config.LANGUAGE_PRIORITY)


def _job_card_html(job: dict, reason: str, language: str) -> str:
    fuente = SOURCE_LABELS.get(job["source"], job["source"])
    lang_label = LANGUAGE_LABELS.get(language, "")
    badge = f' &middot; <span style="color:#0a7d32;">{lang_label}</span>' if lang_label else ""
    return f"""
    <div style="border:1px solid #e5e5e5; border-radius:8px; padding:16px; margin-bottom:14px;">
      <h3 style="margin:0 0 6px; color:#111;">{job['title']}</h3>
      <p style="color:#555; font-size:14px; margin:0 0 8px;">
        <strong>{job['company']}</strong> &middot; {job['location']}<br>
        Fuente: {fuente}{badge}{f" &middot; {job['posted_at']}" if job.get('posted_at') else ""}
      </p>
      <p style="background:#f4f4f4; padding:10px; border-radius:6px; font-size:13px; color:#333; margin:0 0 10px;">
        {reason}
      </p>
      <a href="{job['url']}"
         style="display:inline-block; padding:8px 16px; background:#111;
                color:#fff; text-decoration:none; border-radius:6px; font-weight:bold; font-size:13px;">
        Ver oferta y postular &rarr;
      </a>
    </div>
    """


def send_digest(matches: list[dict]) -> bool:
    """matches: lista de {job, reason, language}. Manda UN solo correo con todas las
    vacantes nuevas de la corrida, ordenadas priorizando espanol."""
    if not matches:
        return True
    if not config.GMAIL_ADDRESS or not config.GMAIL_APP_PASSWORD:
        print(f"[aviso] Gmail no configurado, no se enviaron {len(matches)} vacantes")
        return False

    ordered = sorted(matches, key=lambda m: _language_rank(m["language"]))

    subject = f"{len(matches)} vacante{'s' if len(matches) != 1 else ''} nueva{'s' if len(matches) != 1 else ''} para vos"
    cards = "".join(_job_card_html(m["job"], m["reason"], m["language"]) for m in ordered)
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color:#111;">{subject}</h2>
      {cards}
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.GMAIL_TO
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.sendmail(config.GMAIL_ADDRESS, config.GMAIL_TO, msg.as_string())
        return True
    except smtplib.SMTPException as exc:
        print(f"[error] no se pudo enviar el correo: {exc}")
        return False


def send_test_email():
    return send_digest([{
        "job": {
            "title": "Vacante de prueba",
            "company": "Buscador de Empleo",
            "location": "Tegucigalpa, Honduras",
            "source": "computrabajo",
            "url": "https://example.com",
            "posted_at": "",
        },
        "reason": "Este es un correo de prueba para confirmar que la configuracion de Gmail funciona.",
        "language": "es",
    }])
