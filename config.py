import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GMAIL_TO = os.getenv("GMAIL_TO", GMAIL_ADDRESS)

GROQ_TOKEN = os.getenv("GROQ_TOKEN", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
# Cuantas vacantes se mandan juntas en un solo prompt a Groq (baja mucho la cantidad
# de requests y evita el 429 de rate limit del tier gratis).
GROQ_BATCH_SIZE = int(os.getenv("GROQ_BATCH_SIZE", "8"))
# Segundos minimos entre llamadas a Groq (throttle preventivo, no solo reactivo al 429).
GROQ_MIN_INTERVAL_SECONDS = float(os.getenv("GROQ_MIN_INTERVAL_SECONDS", "2.5"))
GROQ_MAX_RETRIES = int(os.getenv("GROQ_MAX_RETRIES", "4"))
# Si Groq devuelve un Retry-After mayor a esto (cuota horaria/diaria agotada,
# no rate limit transitorio), no tiene sentido dormir esa espera dentro de
# una corrida: se cae al fallback por palabra clave de inmediato.
GROQ_MAX_RETRY_AFTER_SECONDS = float(os.getenv("GROQ_MAX_RETRY_AFTER_SECONDS", "20"))
# Tope de candidatos juzgados por Groq en una sola corrida (ver main.py). Con
# GROQ_BATCH_SIZE=8 y GROQ_MIN_INTERVAL_SECONDS=2.5, 60 candidatos caben
# comodos dentro del timeout de 12 min del workflow de GitHub Actions incluso
# si varios lotes pegan en rate limit y hacen backoff completo.
MAX_CANDIDATES_PER_RUN = int(os.getenv("MAX_CANDIDATES_PER_RUN", "60"))

POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "15"))

# Idiomas en orden de prioridad para el correo digest y el frontend (primero los que
# encajan mejor con "idioma de trabajo: espanol" del perfil).
LANGUAGE_PRIORITY = ["es", "en"]

# Remotive pide explicitamente no llamar su API mas de ~4 veces al dia.
REMOTIVE_MIN_HOURS_BETWEEN_FETCH = 6

# HN "Who is hiring" trae un arbol de cientos de comentarios: se throttlea
# para no re-descargarlo entero en cada corrida de 15 min.
HN_WHOISHIRING_MIN_HOURS_BETWEEN_FETCH = float(os.getenv("HN_WHOISHIRING_MIN_HOURS_BETWEEN_FETCH", "6"))

# Adzuna: registro gratis en https://developer.adzuna.com/ (1000 llamadas/mes).
# Sin credenciales, la fuente se salta sola.
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_MIN_HOURS_BETWEEN_FETCH = float(os.getenv("ADZUNA_MIN_HOURS_BETWEEN_FETCH", "8"))

# Jooble: key gratis inmediata en https://jooble.org/api/about.
# Sin credencial, la fuente se salta sola.
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "")
JOOBLE_MIN_HOURS_BETWEEN_FETCH = float(os.getenv("JOOBLE_MIN_HOURS_BETWEEN_FETCH", "6"))

# The Muse: funciona sin key (limite bajo); con key gratis de
# https://www.themuse.com/developers/api/v2 sube el limite a 3600 req/hora.
THEMUSE_API_KEY = os.getenv("THEMUSE_API_KEY", "")

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "vacantes_vistas.db"))

# Perfil usado por el LLM para juzgar si una vacante encaja de verdad,
# no solo por coincidencia de palabras sueltas (ej: "desarrollador de negocios" no es dev).
CANDIDATE_PROFILE = """
Ingeniero en Sistemas con ~4 años de experiencia. Backend: Laravel (PHP), Python (FastAPI, Django),
Go (Gin), Java (Spring Boot), Node.js. Frontend: Vue 3. Bases de datos: PostgreSQL, MySQL, Oracle,
SurrealDB, CouchDB. IA/LLMs: integración y orquestación con Claude, OpenAI y Groq, NLP, prompt
engineering. Big Data: PySpark, pipelines ETL. DevOps: Docker, CI/CD, GitHub Actions.
Busca roles de: Backend Developer, Full Stack Developer, Laravel Developer, Python/FastAPI Developer,
Go Developer, AI/LLM Engineer, Software Engineer. Modalidad: remoto (idealmente hispanohablante o
amigable con Latinoamérica) o presencial/híbrido en Tegucigalpa / Francisco Morazán, Honduras.
Idioma de trabajo: español.
""".strip()

# Palabras clave para el filtro barato (evita gastar llamadas al LLM en resultados obviamente ajenos).
KEYWORD_PREFILTER = [
    "developer", "desarrollador", "desarrolladora", "programador", "programadora",
    "backend", "back-end", "back end", "full stack", "fullstack", "full-stack",
    "software engineer", "ingeniero de software", "ingeniera de software",
    "laravel", "php", "python", "fastapi", "django", "golang", " go ", "gin",
    "java", "spring", "node.js", "nodejs", "vue", "javascript", "typescript",
    "inteligencia artificial", " ia ", " ai ", "llm", "machine learning", "nlp",
    "devops", "api rest", "microservicios", "postgresql", "mysql", "sql",
]

HONDURAS_LOCATION_HINTS = [
    "francisco morazán", "francisco morazan", "tegucigalpa", "distrito central", "remoto", "remote",
]
