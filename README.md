# ipOna

Juego de predicciones deportivas para un grupo privado de amigos (<6 jugadores) con un competidor IA que predice usando datos históricos. Todo corre en servicios gratuitos.

Predecí el resultado de partidos de fútbol (Liga Profesional Argentina, Premier, Champions, Libertadores, Sudamericana, Serie A, LaLiga), NBA y F1. Sumá puntos por marcador exacto o por acertar quién gana/empata/pierde. En F1 se predice el podio. La IA (`ipona-ia`) compite en la tabla como un jugador más.

---

## Stack

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI (async) |
| Base de datos | PostgreSQL 16 (Docker en dev; Neon/Supabase en prod) |
| Frontend | PWA con React 19 + Vite, servida por FastAPI |
| Datos deportivos | API pública de ESPN ([ADR-001](docs/adr/001-usar-api-espn-como-fuente-de-datos.md)) |
| LLM | Cerebras / Groq vía SDK OpenAI (`openai/gpt-oss-120b`), con failover |
| Jobs | APScheduler embebido |
| Tests | pytest |

## Cómo levantar el proyecto

### Requisitos

- Docker
- Python 3.12 con virtualenv en `venv/` en la raíz del repo

### 1. Levantar la base de datos

```bash
docker compose up -d db
```

### 2. Instalar dependencias (solo la primera vez)

```bash
venv/bin/pip install -r backend/requirements-dev.txt
```

### 3. Aplicar migraciones

```bash
cd backend
../venv/bin/alembic upgrade head
```

### 4. Construir el frontend (solo la primera vez o al cambiar la UI)

```bash
# requiere Node 18+
cd frontend
npm install
npm run build   # genera frontend/dist/, que es lo que sirve FastAPI
```

### 5. Arrancar el servidor

```bash
# desde backend/
../venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

Listo. Abrí **http://localhost:8000** — ahí vive la PWA completa.

Para probar desde el celular en tu red local:

```bash
../venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

y entrá a `http://<tu-ip-local>:8000`.

> Si la PWA ya estaba instalada y no ves los cambios: DevTools → Application → Clear site data.

### Variables de entorno

El `.env` en la raíz del repo (gitignored):

| Variable | Descripción |
|---|---|
| `API_SPORTS` | Key de api-sports.io (plan B de datos, hoy sin uso activo) |
| `CEREBRAS_API_KEY` | Clave de [cerebras.ai](https://cloud.cerebras.ai) |
| `GROQ_API_KEY` | Clave de [console.groq.com](https://console.groq.com) |
| `SCHEDULER_ENABLED` | `true`/`false` — jobs automáticos (default: true) |
| `SECRET_KEY` | Secreto JWT — **obligatorio en producción** |

## Qué hace solo el sistema

Con el servidor corriendo, APScheduler automatiza el ciclo:

| Hora (UTC) | Job |
|---|---|
| 06:00 | Sincroniza eventos del día desde ESPN |
| 06:15 | Genera las predicciones del LLM |
| cada 1 h | Consulta resultados y puntúa predicciones |

Todo también se puede gatear a mano:

```bash
curl -X POST http://localhost:8000/llm/predict        # predicciones IA
curl -X POST http://localhost:8000/leaderboard/update # puntuar resultados
```

## Estructura del repo

```
backend/
├── app/
│   ├── main.py           # FastAPI + montaje PWA
│   ├── core/             # config, seguridad (JWT/bcrypt), rate limiting
│   ├── auth/             # registro y login
│   ├── users/            # perfil actual
│   ├── sports/           # adaptador ESPN (provider pattern)
│   ├── events/           # sincronización y selección curada diaria (2–10)
│   ├── predictions/      # alta y consulta de predicciones
│   ├── scoring/          # puntos, actualización de resultados, tabla
│   ├── llm/              # jugador IA (Cerebras/Groq + contexto histórico)
│   ├── stats/            # precisión por usuario/deporte y tokens
│   ├── scheduler.py      # jobs automáticos
│   └── db/               # engine y modelos SQLAlchemy
├── alembic/              # migraciones
└── tests/
frontend/                 # PWA en React + Vite (el build va a frontend/dist/)
docs/adr/                 # decisiones de arquitectura
.ai/                      # estándares de ingeniería con IA (gobernanza)
```

## Tests

```bash
cd backend
../venv/bin/python -m pytest -v
```

Requieren Docker con Postgres levantado (los tests de integración resetean las tablas).

## Documentación de la API

Con el server corriendo: **http://localhost:8000/docs** (Swagger interactivo).
