# Buscador de Empleo

Revisa **9 fuentes** de empleo en busca de vacantes que encajen con tu perfil (backend, Laravel,
Python/FastAPI, Go, IA/LLMs), remoto o en Tegucigalpa / Francisco Morazán, y te avisa por Gmail
con un **correo digest único** por corrida (no uno por vacante).

## Fuentes

| Fuente | Cobertura |
|---|---|
| Computrabajo Honduras | Honduras |
| Tecoloco Honduras | Honduras |
| RemoteOK | Remoto, global |
| Jobicy | Remoto, global |
| Remotive | Remoto, global (se consulta max. cada 6h, piden no abusar de su API) |
| Arbeitnow | Remoto/presencial, mayormente Europa |
| We Work Remotely | Remoto, global |
| Himalayas | Remoto, global |
| Torre | LatAm y remoto, buena cobertura en español |

LinkedIn queda excluido a propósito (scrapearlo viola sus Términos de Servicio y puede banear la
cuenta/IP). Indeed y GetOnBoard tampoco se incluyeron: no tienen una API pública sin registro que
respete sus términos de uso para este caso de uso.

Un modelo de Groq revisa cada tanda de vacantes (en lotes, no una por una) antes de notificarte,
para descartar falsos positivos del tipo "Desarrollador de Negocios" (que no es un puesto técnico),
detectar el idioma de la vacante y explicarte en una frase por qué encaja contigo. Si Groq da rate
limit (429), el programa reintenta con backoff respetando el `Retry-After` de la API; si se agotan
los reintentos, cae a un filtro por palabra clave para esa tanda puntual.

## Frontend

Cada corrida regenera `docs/jobs.json`, que alimenta `docs/index.html`: una tabla filtrable por
fuente, idioma y si fue notificada, con buscador de texto. Se sirve gratis con GitHub Pages.

## Instalación local

```bash
cd /home/ariel/Documentos/buscador_empleo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env`:

1. **GMAIL_ADDRESS / GMAIL_APP_PASSWORD**: activa verificación en 2 pasos en tu cuenta de Gmail y
   genera una "contraseña de aplicación" en https://myaccount.google.com/apppasswords (tu
   contraseña normal de Gmail NO funciona para esto, Google la rechaza).
2. **GROQ_TOKEN**: gratis en https://console.groq.com/keys. Sin esto el programa sigue funcionando
   pero solo filtra por palabra clave, con bastantes más falsos positivos.

## Probar que el correo funciona

```bash
python3 main.py --test-email
```

## Ejecutar una sola revisión

```bash
python3 main.py
```

## Ejecutar en bucle continuo (revisa cada 15 min por defecto)

```bash
python3 main.py --loop
```

## Producción gratis: GitHub Actions + GitHub Pages

Ya desplegado en https://github.com/joseA666/buscador-empleo (repo público, para tener minutos de
Actions ilimitados sin pagar). `.github/workflows/buscar.yml` corre `main.py` cada 15 minutos en la
nube, commitea `vacantes_vistas.db` y `docs/jobs.json` de vuelta, y GitHub Pages sirve `docs/` como
sitio estático en **https://josea666.github.io/buscador-empleo/**.

Los secrets (`GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `GMAIL_TO`, `GROQ_TOKEN`) ya están cargados en
Settings → Secrets and variables → Actions. Para rotarlos: `gh secret set NOMBRE -R
joseA666/buscador-empleo`.

## Cómo decide qué te notifica

1. Cada fuente trae vacantes crudas (`sources/`).
2. Un filtro barato por palabra clave descarta lo obviamente ajeno sin gastar cuota de Groq.
3. Lo que pasa el filtro se manda a Groq en lotes de `GROQ_BATCH_SIZE` (junto con tu perfil,
   `config.CANDIDATE_PROFILE`) para que decida si de verdad es un puesto técnico relevante, con
   ubicación razonable, y en qué idioma está.
4. Las vacantes ya vistas (`vacantes_vistas.db`, SQLite local) no se vuelven a evaluar ni notificar.
5. Todo lo que sí encaja se manda en **un solo correo** ordenado priorizando español
   (`config.LANGUAGE_PRIORITY`).

## Ajustar el perfil o las fuentes de búsqueda

- `config.py`: perfil del candidato, palabras clave del prefiltro, intervalo de revisión, tamaño
  de lote y throttle de Groq.
- `sources/computrabajo.py`, `sources/tecoloco.py` y `sources/himalayas.py`: listas
  `SEARCH_URLS`/`KEYWORDS` con las búsquedas concretas que se consultan.
