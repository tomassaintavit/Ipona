# Reglas del juego ipOna

## Qué es

Juego de predicciones deportivas para un grupo privado de amigos (<6 jugadores).
Cada día el sistema muestra entre 2 y 10 eventos seleccionados (nunca todos los
partidos del día). Los jugadores predicen el resultado antes del inicio de cada
evento. Una IA llamada "ipona-ia" también predice y compite en la tabla como un
jugador más.

## Deportes y competencias

- Fútbol masculino: Liga Profesional Argentina, Premier League, Champions League,
  Copa Libertadores, Copa Sudamericana, Serie A, LaLiga
- NBA
- Fórmula 1

## Cómo se predice

- Fútbol y NBA: marcador exacto (goles/puntos de cada equipo)
- Fórmula 1: el podio completo en orden (1°, 2° y 3°)

Solo se puede predecir antes de que empiece el evento. Se puede cambiar la
predicción cuantas veces se quiera hasta el inicio.

## Puntuación

Fútbol y NBA:

- Marcador exacto: 3 puntos
- Acertar el resultado (gana / empata / pierde): 1 punto
- Fallar: 0 puntos

Fórmula 1:

- 1 punto por cada piloto correctamente ubicado en su posición exacta del podio
  (máximo 3 puntos)

## Tabla de posiciones

Suma de puntos de todas las predicciones puntuadas de cada jugador, incluyendo
la IA. Se actualiza automáticamente al finalizar los partidos (hasta 1 hora
después puede demorar).

## Estadísticas

Cada jugador ve su precisión total y por deporte (aciertos sobre predicciones
puntuadas). La IA muestra además los tokens consumidos.

## Asistente de chat

Los usuarios logueados pueden hacer hasta 10 preguntas por hora al asistente.
El asistente responde sobre datos del juego: partidos jugados, tabla,
predicciones, próximos eventos y precisión de jugadores. No sabe información
que no esté en la base de datos del juego ni cubre temas ajenos a ipOna.

## Otras reglas

- Registro solo por invitación del grupo; no hay registro público masivo
- No hay apuestas ni premios de dinero real
- Las predicciones son pre-partido; no hay apuestas en vivo
