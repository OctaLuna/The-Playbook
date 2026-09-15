# Quickstart: Validación manual de Predicción de Partido

**Basado en:** `specs/001-prediccion-partido/spec.md` y `plan.md`

## Escenario 1 — Ver las 4 señales de un partido con datos suficientes
1. Levantar el stack local: `docker-compose up` (backend + Postgres + Redis).
2. Ejecutar el job de Celery `generate_predictions` manualmente para un partido de prueba de una de las 5 ligas con historial suficiente.
3. Llamar `GET /api/matches/{match_id}/prediction`.
4. Verificar: las probabilidades 1X2 suman 1.0, existen `over_under_2_5`, `btts`, `xg.home`/`xg.away`, y `confidence` es uno de alta/media/baja.

## Escenario 2 — Aviso de baja confiabilidad con datos insuficientes
1. Usar un equipo marcado con `tiene_historial_suficiente = false` (ej. recién ascendido, con menos de una temporada de datos).
2. Generar la predicción y consultarla.
3. Verificar: la predicción existe igual, pero el response incluye `low_data_warning: true`.

## Escenario 3 — Línea O/U fuera de alcance
1. Intentar consultar cualquier endpoint pidiendo una línea distinta a 2.5 (ej. `?line=1.5`).
2. Verificar: el parámetro no existe en el contrato — no hay forma de pedirlo, confirmando que el MVP no lo soporta (decisión de Clarify).

## Escenario 4 — Partido pospuesto sigue visible
1. Marcar un partido con predicción ya generada con `estado = pospuesto`.
2. Consultar `GET /api/matches/{match_id}` y `GET /api/matches/{match_id}/prediction`.
3. Verificar: el partido devuelve `status: "postponed"`, y la predicción original sigue disponible sin cambios.

## Escenario 5 — Head-to-head no disponible
1. Usar un partido entre dos equipos sin historial de enfrentamientos previos (ej. uno recién ascendido).
2. Consultar la predicción.
3. Verificar: `head_to_head_available: false` en la respuesta.
