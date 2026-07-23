import json
import time

import requests

import config

try:
    from langdetect import detect as _detect_lang, DetectorFactory
    DetectorFactory.seed = 0
except ImportError:
    _detect_lang = None

_last_call_at = 0.0


def keyword_prefilter(job: dict) -> bool:
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    return any(kw in text for kw in config.KEYWORD_PREFILTER)


def detect_language(job: dict) -> str:
    """'es', 'en' o 'other'. Nunca falla: si no se puede detectar, devuelve 'other'."""
    if _detect_lang is None:
        return "other"
    text = f"{job.get('title', '')} {job.get('description', '')}".strip()[:500]
    if len(text) < 10:
        return "other"
    try:
        lang = _detect_lang(text)
    except Exception:
        return "other"
    return lang if lang in ("es", "en") else "other"


def _throttle():
    global _last_call_at
    wait = config.GROQ_MIN_INTERVAL_SECONDS - (time.time() - _last_call_at)
    if wait > 0:
        time.sleep(wait)


def _call_groq(payload: dict) -> dict:
    """POST a Groq con reintentos y backoff exponencial ante 429/errores transitorios."""
    last_exc = None
    for attempt in range(config.GROQ_MAX_RETRIES):
        _throttle()
        global _last_call_at
        _last_call_at = time.time()
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {config.GROQ_TOKEN}"},
                json=payload,
                timeout=30,
            )
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", 2 ** attempt * 3))
                print(f"[aviso] Groq 429 (rate limit), esperando {retry_after:.0f}s (intento {attempt + 1}/{config.GROQ_MAX_RETRIES})")
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Groq no respondio tras {config.GROQ_MAX_RETRIES} intentos: {last_exc}")


def _fallback_batch(jobs: list[dict]) -> list[dict]:
    return [
        {
            "match": keyword_prefilter(job),
            "reason": "Coincidencia por palabra clave (Groq no disponible)",
            "language": detect_language(job),
        }
        for job in jobs
    ]


def llm_judge_batch(jobs: list[dict]) -> list[dict]:
    """Juzga un lote de vacantes en una sola llamada a Groq. Devuelve una lista alineada
    por indice con {match, reason, language}. Si Groq falla, cae a prefiltro + deteccion
    de idioma local (nunca deja de devolver un resultado por cada job de entrada)."""
    if not jobs:
        return []
    if not config.GROQ_TOKEN:
        return _fallback_batch(jobs)

    vacantes_txt = "\n\n".join(
        f"[{i}] Titulo: {job.get('title')}\n"
        f"Empresa: {job.get('company')}\n"
        f"Ubicacion: {job.get('location')}\n"
        f"Descripcion: {(job.get('description') or '')[:1000]}"
        for i, job in enumerate(jobs)
    )

    prompt = f"""Eres un asistente que filtra vacantes de empleo para un candidato especifico.

PERFIL DEL CANDIDATO:
{config.CANDIDATE_PROFILE}

Te paso una lista de vacantes numeradas del 0 al {len(jobs) - 1}. Para CADA UNA, responde si
encaja de verdad con el perfil, y en que idioma esta escrita la vacante (titulo+descripcion).

VACANTES:
{vacantes_txt}

Responde SOLO con un JSON valido, sin texto adicional, con este formato exacto (un objeto por
cada indice, en el mismo orden 0..{len(jobs) - 1}):
{{"results": [{{"index": 0, "match": true o false, "reason": "frase corta en espanol", "language": "es|en|other"}}, ...]}}

Marca match=true solo si el puesto es realmente de desarrollo de software / IA para el perfil
descrito (ignora vacantes de "desarrollador de negocios", ventas, marketing u otras que solo
comparten una palabra pero no son roles tecnicos). Marca match=false si la ubicacion no es
razonable (ni remoto amigable con Latinoamerica/hispanohablante, ni Tegucigalpa/Francisco
Morazan, Honduras)."""

    try:
        data = _call_groq({
            "model": config.GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        })
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        by_index = {int(r["index"]): r for r in parsed.get("results", [])}
        out = []
        for i, job in enumerate(jobs):
            r = by_index.get(i)
            if r is None:
                out.append({"match": keyword_prefilter(job), "reason": "Groq no devolvio resultado para esta vacante", "language": detect_language(job)})
            else:
                lang = r.get("language") if r.get("language") in ("es", "en") else detect_language(job)
                out.append({"match": bool(r.get("match")), "reason": r.get("reason", ""), "language": lang})
        return out
    except Exception as exc:
        print(f"[aviso] Groq fallo ({exc}), usando prefiltro por palabra clave para este lote")
        return _fallback_batch(jobs)
