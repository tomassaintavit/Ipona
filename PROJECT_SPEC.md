# Project Specification

Version: 0.1.0

## Purpose

Este documento define el contexto, objetivos, restricciones y decisiones técnicas de **Ipona**.

Los agentes de IA DEBEN leer este documento antes de planificar o implementar cambios.

---

# Project Overview

## Project Name

**Ipona** (juego de palabras con "Opina")

---

## Problem Statement

No existe un sistema simple y sin costo para que un grupo pequeño de amigos compita prediciendo resultados deportivos de múltiples deportes (fútbol, NBA, F1), con un jugador LLM como competidor adicional que mejora sus predicciones usando datos históricos.

Ipona resuelve esto: un juego web de predicciones deportivas con tabla de posiciones, autenticación y un competidor IA, corriendo íntegramente en servicios gratuitos.

---

## Objectives

1. Predicciones de partidos/eventos próximos de múltiples deportes vía APIs deportivas
2. **Selección curada de eventos**: el sistema muestra entre 2 y 10 partidos por día (no todos los del día), para minimizar la carga de predicción del usuario
3. Tabla de posiciones con puntuación automática al finalizar partidos
4. Autenticación de usuarios (grupo privado <6)
5. Jugador LLM que predice usando datos históricos/estadísticas y mejora con el tiempo
6. Estadísticas: historial de aciertos, precisión por usuario y del LLM, rendimiento por deporte

---

## Non-Objectives

- ❌ Apuestas con dinero real o premios monetarios
- ❌ Registro abierto al público / onboarding masivo
- ❌ Apps móviles nativas (solo PWA)
- ❌ Predicciones en vivo durante el partido (solo pre-partido)
- ❌ Streaming o datos minuto a minuto
- ❌ Integraciones sociales (chat, compartir en redes)
- ❌ Mostrar todos los partidos del día (solo una selección curada de 2 a 10 por día)

---

# Users and Stakeholders

## Target Users

Grupo privado de amigos (<6 usuarios). Sin registros abiertos.

## Stakeholders

- Dueño/admin/jugador (único mantenedor)
- Jugadores (amigos)
- Sistemas externos: APIs deportivas, Cerebras, Groq

---

# Technical Context

## Technology Stack

- **Backend**: Python 3.12 + FastAPI (endpoints async)
- **Base de datos**: PostgreSQL en free tier (Neon o Supabase)
- **Frontend**: PWA (web responsive, usable desde celular)
- **LLM**: Cerebras y Groq vía SDK OpenAI (ambas compatibles), con registro de tokens (`usage`) por llamada
- **Jobs**: APScheduler embebido en FastAPI
- **Infra**: Docker para desarrollo; deploy en servicios gratuitos (Render/Railway/Fly.io)
- **Tests**: pytest

## Architecture Overview

Monolito modular con API REST:

- Un solo servicio FastAPI: API + lógica de negocio + scheduler
- Componentes: auth, partidos/resultados (APIs deportivas), selección curada diaria de eventos, predicciones, scoring/tabla, jugador LLM, estadísticas
- Flujo: API deportiva → cache/DB → selección curada del día → usuarios y LLM predicen → job programado consulta resultados → calcula puntos → actualiza tabla
- Estructura: `backend/` (FastAPI), `frontend/` (PWA), `.ai/` (gobernanza)

---

# Development Constraints

## Mandatory Technologies

- Servicios 100% gratuitos (costo $0)
- Interfaz en español
- Cerebras y Groq como proveedores LLM
- Selección curada de 2 a 10 eventos por día (no catálogo completo)

## Forbidden Technologies

- LangChain u otros frameworks LLM pesados (se usa SDK OpenAI directo)
- Apps móviles nativas
- Servicios de pago

## Performance Requirements

- Latencia p95 < 2s en endpoints web
- Actualización de resultados hasta 1h después del partido (aceptable)
- Disponibilidad "best effort" (free tiers)

## Security Requirements

- Auth JWT, passwords hasheadas (bcrypt/argon2)
- Secrets solo en variables de entorno
- HTTPS (del proveedor de deploy)
- Rate limiting básico en login y endpoints LLM
- Datos mínimos: email + username

---

# Success Criteria

- El grupo puede registrarse/loguearse y predecir los eventos seleccionados del día (entre 2 y 10)
- Resultados calculados automáticamente; tabla siempre actualizada
- Scoring por marcador exacto **y** por acierto de resultado (gana/pierde/empata) en fútbol y NBA; formato propio para F1 (podio/posiciones)
- El LLM participa en la tabla como un jugador más y sus predicciones usan datos históricos
- Estadísticas visibles por usuario/deporte
- Costo mensual: $0

---

# Project Status

Ver `PROJECT_STATUS.md` para el estado vivo del proyecto.

Estado inicial: sin código de aplicación.

Decisión de datos deportivos: **API pública de ESPN como fuente principal**, con capa
adaptadora y api-sports.io como plan B — ver ADR `docs/adr/001-usar-api-espn-como-fuente-de-datos.md`.

Riesgos conocidos:
- Sleep de free tiers → mitigar con ping externo o aceptar retrasos
- Límites de APIs deportivas (~100 req/día) → cache + polling inteligente; la selección curada reduce consumo
- Cobertura parcial de ligas de fútbol aceptada (iremos con las disponibles)
- Calidad del LLM iterativa: empezar con contexto estadístico en prompts, no fine-tuning
- Backups manuales del Postgres gratuito
