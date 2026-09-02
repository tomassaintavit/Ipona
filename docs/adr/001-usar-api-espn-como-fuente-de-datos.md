# 001: Usar la API de ESPN como fuente de datos deportivos

**Status**: Accepted
**Date**: 2026-08-23
**Deciders**: Tomás (dueño del proyecto), ox-alpha (agente)
**Tags**: api, integraciones, datos-deportivos, arquitectura

---

## Context

Ipona necesita una fuente de datos de partidos/eventos próximos y resultados para:

- Fútbol masculino: Liga Profesional Argentina, Premier League, Champions League,
  Copa Libertadores, Copa Sudamericana, Serie A, LaLiga
- NBA
- Formula 1 (con resultados por posición/podio)

Restricciones duras: costo $0 obligatorio, sin tarjeta de crédito, grupo <6 usuarios,
selección curada de 2–6 eventos/día (bajo volumen de consultas).

Se evaluaron empíricamente 4 proveedores (spike del 2026-08-23):

1. **api-sports.io** — key free registrada y probada. El plan Free bloquea la temporada
   actual para fixtures: `"Free plans do not have access to this season, try from 2022
   to 2024"`. Solo expone metadata de ligas. Descartado como fuente principal.
2. **TheSportsDB** (key gratuita `123`) — `all_leagues.php` devuelve solo ~5 ligas,
   `eventsnextleague.php` devuelve 1 evento, `eventsday.php` devuelve 3 eventos
   arbitrarios, y la Liga Profesional Argentina no es accesible en el tier gratuito.
3. **football-data.org** — tier gratuito limitado a 12 competiciones de fútbol europeo;
   no cubre liga argentina, Libertadores, Sudamericana, NBA ni F1.
4. **API pública de ESPN** (`site.api.espn.com`) — verificada con requests reales:
   cubre las 10 competencias objetivo, incluye eventos próximos, resultados finales y,
   para F1, el orden de llegada de los 22 pilotos (campo `order`). No requiere API key.

---

## Decision

**Usaremos la API pública de ESPN como fuente principal de datos deportivos porque es
la única opción con costo $0 que cubre todas las competencias objetivo, incluidos los
resultados por posición de F1.**

Detalles de implementación:

- Endpoints base: `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard`
  (y equivalentes por deporte: `soccer/arg.1`, `soccer/conmebol.libertadores`,
  `basketball/nba`, `racing/f1`, etc.)
- Todo acceso a datos deportivos pasa por una **capa adaptadora** (`SportsDataProvider`)
  con interfaz propia del dominio (eventos, resultados, posiciones), de modo que el
  proveedor pueda reemplazarse sin tocar lógica de negocio.
- Cache agresiva de respuestas para minimizar dependencia de disponibilidad.
- La API key gratuita de api-sports.io queda registrada en `.env` pero sin uso activo.

---

## Consequences

### Positive

- Cobertura completa de las 10 competencias objetivo a costo $0
- Sin API key ni registro (menos secretos que gestionar)
- Resultados de F1 por posición disponibles para el scoring propio
- Baja latencia y sin límites diarios estrictos documentados

### Negative

- API no oficial: sin SLA, sin contrato de estabilidad, formato puede cambiar
- Estructura de respuesta verbosa (requiere mapeo al modelo del dominio)

### Risks

- Cambio o cierre de endpoints no oficiales (mitigación: capa adaptadora +
  api-sports.io documentado como plan B; migración = solo reimplementar el adaptador)
- Rate limiting no documentado ante abuso (mitigación: cache + polling programado
  de baja frecuencia, coherente con selección curada de 2–6 eventos/día)

### Tradeoffs

- Aceptamos depender de una API no oficial para ganar cobertura total a costo $0

---

## Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| api-sports.io | API oficial estable, multideporte, key free ya registrada | Free plan bloquea temporada actual (verificado) | Sin partidos actuales no sirve para predicciones |
| TheSportsDB | Simple, sin registro | Tier free muy recortado; sin liga argentina accesible | Insuficiente incluso para prototipo |
| football-data.org | Datos de fútbol confiables | Solo 12 competencias europeas; sin NBA/F1 | No cubre el alcance multideporte |
| Plan B: pagar api-sports.io ($10/mes) | Estabilidad contractual | Viola restricción $0 | Reservado como contingencia |

---

## Links

- Related ADRs: —
- Issues/PRs: —
- External:
  - https://site.api.espn.com/apis/site/v2/sports/soccer/arg.1/scoreboard (verificado)
  - https://www.api-football.com/pricing (limitación de temporadas en free)

---

## Notes

Spike realizado el 2026-08-23 con requests reales contra los 4 proveedores.
La key gratuita de api-sports.io (variable `API_SPORTS` en `.env`) se conserva para
el plan B. Revisar este ADR si ESPN cambia su estructura o si se detectan bloqueos.
