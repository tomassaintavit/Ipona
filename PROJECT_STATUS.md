# Project Status — ipOna

Version: 0.1.0

## Purpose

Este documento registra el estado vivo del proyecto. Se actualiza al completar tareas significativas.

---

# Overview

| Field | Value |
|-------|-------|
| Project Name | ipOna (juego de predicciones deportivas) |
| Last Updated | 2026-09-02 |
| Current Phase | Maintenance (v1 en producción) |
| Overall Progress | ~90% del alcance v1 |

**Producción**: https://ipona.onrender.com · DB: Supabase · Anti-sleep: cron-job.org cada 10 min

---

# Features

## Completed

- [x] Adaptador ESPN con capa de abstracción (SportsDataProvider) — 2026-08-23
- [x] Selección curada diaria (2–6 eventos, diversidad de ligas) + endpoint /events/today — 2026-08-24
- [x] PostgreSQL + SQLAlchemy async + Alembic (Docker en dev) — 2026-08-24
- [x] Auth JWT + bcrypt + rate limiting — 2026-08-24
- [x] Predicciones por deporte (marcador o podio F1) con edición hasta el inicio — 2026-08-24
- [x] Motor de scoring (3/1 pts fútbol-NBA, 1 pt posición F1) + tabla de posiciones — 2026-08-24
- [x] Jugador IA "Cris el pulpo Paul" (Cerebras/Groq, contexto histórico, registro de tokens) — 2026-08-24
- [x] Scheduler embebido (sync 06:00 UTC, Cris 06:15 UTC, resultados cada 1h) — 2026-08-24
- [x] Estadísticas por usuario/deporte + tokens del LLM — 2026-08-24
- [x] PWA React + Vite (tema oscuro/púrpura, branding, auth separada) — 2026-08-25
- [x] Chatbot "Cris" con function calling sobre la DB + reglas desde archivo editable — 2026-08-25
- [x] Favorito según casas de apuestas (ESPN odds) como contexto del LLM — 2026-08-25
- [x] Deploy producción: Render + Supabase + cron anti-sleep — 2026-08-25
- [x] Código de invitación obligatorio para registro — 2026-08-25
- [x] Fixes de scoring en producción (estado stale + zona horaria ESPN) — 2026-08-25
- [x] Ventana de fechas ±1 día para sincronización ESPN (corrige timezone mismatch) — 2026-09-02
- [x] 18 ligas de fútbol: ligas principales + copas nacionales (ARG, ENG, ITA, ESP, GER, FRA) + UEFA — 2026-09-02
- [x] Selección curada ajustada a 2–6 eventos/día — 2026-09-02
- [x] Tabla por períodos (global / semanal / mensual) — 2026-09-02
- [x] Batallas diarias: duelos 1v1 aleatorios (tríos si hay impar), la IA participa, mensaje del ganador, resolución automática — 2026-09-02

## Planned

- [ ] Mejora LLM: head-to-head en el contexto — Priority: Medium
- [ ] Mejora LLM: auto-revisión de aciertos/errores recientes de Cris — Priority: Medium
- [ ] Baseline de evaluación: comparar precisión de Cris vs estrategia ingenua — Priority: High (antes de optimizar más)
- [ ] Mejora LLM: posición en tabla real de las ligas — Priority: Low
- [ ] The Odds API como fuente complementaria de favoritos — Priority: Low
- [ ] Notificaciones web push a usuarios ("hay eventos nuevos") — Priority: Low
- [ ] Grafana Cloud free tier + logging JSON estructurado — Priority: Low (diferido)

---

# Technical Debt

| Item | Severity | Description | Target Resolution |
|------|----------|-------------|-------------------|
| TD-001 | Low | Esquema HTTPBearer no declarado → Swagger /docs no permite autorizar endpoints protegidos | Próxima sesión |
| TD-002 | Low | Logo SVG/PNG pesa ~3MB; exportar versión liviana | Próxima sesión |
| TD-003 | Medium | Rotar contraseña de Supabase (quedó expuesta en conversación) | Ya |
| TD-004 | Low | Recuperación de contraseña manual vía SQL; evaluar flujo email (Resend/Brevo) si hace falta | Backlog |
| TD-005 | Low | Desempates en tabla por orden de inserción; definir criterio (ej. menos predicciones) | Cuando importe |
| TD-006 | Low | Service worker requiere bump manual de caché en cada cambio de front | Considerar automatizar |

---

# Decisions Log

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| ADR-001 | Usar API de ESPN como fuente de datos (plan B: api-sports.io) | Accepted | 2026-08-23 |

Otras decisiones relevantes (sin ADR formal):
- Monolito modular FastAPI + React/Vite sin framework CSS (CSS propio; Radix UI cuando se necesite un componente complejo)
- LLM: SDK OpenAI directo sobre Cerebras/Groq con failover (LangChain prohibido por spec)
- Scoring: marcador exacto 3 pts, resultado 1 pt, F1 1 pt por posición exacta del podio
- Registro cerrado con INVITE_CODE por variable de entorno
- Chat efímero (sin persistencia de conversaciones)
- Reglas del juego en docs/reglas-del-juego.md inyectadas al prompt del asistente

---

# Blockers & Risks

| ID | Description | Impact | Mitigation | Owner |
|----|-------------|--------|------------|-------|
| R-001 | API ESPN no oficial (sin SLA, puede cambiar) | Medium | Capa adaptadora + api-sports.io documentado como plan B (ADR-001) | Tomás |
| R-002 | Sleep de Render free tier pausa el scheduler | Medium | cron-job.org pings /health cada 10 min ✅ activo | Tomás |
| R-003 | Cuotas LLM (Groq/Cerebras) pueden agotarse | Low | Failover entre proveedores; monitorear llm_calls y consolas | Tomás |
| R-004 | Postgres gratuito sin backups automáticos | Medium | Backup manual periódico (pendiente rutina) | Tomás |

---

# Metrics

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Tests | 79 passed | >80% cobertura | ↑ |
| Costo mensual | $0 | $0 | → |
| Disponibilidad | Best effort (free tiers) | — | → |

---

# Notes

- Actualizar este archivo tras cada tarea significativa (DONE-040)
- Lecciones aprendidas del primer deploy: caracteres especiales en DATABASE_URL (% → escapar en Alembic), IPv4-only en Render → usar Session Pooler de Supabase, httpx era dependencia de runtime oculta por requirements-dev, ESPN lista partidos nocturnos UTC bajo fecha local de la liga
- Fix timezone: `get_day_events` ahora consulta rango ±1 día (no solo la fecha UTC), corrigiendo la regresión donde partidos nocturnos quedaban fuera de la sincronización
- ESPN soporta `dates=YYYYMMDD-YYYYMMDD` nativamente, reduciendo N requests por liga a 1 request por liga
- Batallas: el emparejamiento se hace dentro del job de sync (06:00 UTC, idempotente por fecha); la resolución corre en el job de resultados. Modelo `battles` con `extra_user_id` para tríos. Ver `docs/reglas-del-juego.md`
