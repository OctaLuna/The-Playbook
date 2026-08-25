# Quickstart: Validación manual de Track Record Público

**Basado en:** `specs/003-track-record-publico/spec.md` y `plan.md`

## Escenario 1 — Ver el agregado de los últimos 50 partidos
1. Levantar el stack local (`docker-compose up`) con al menos 50 partidos ya marcados como `jugado` y con `Predicción` asociada.
2. Ejecutar manualmente el job `update_track_record`.
3. Llamar `GET /api/track-record`.
4. Verificar: `hit_rate`, `avg_brier_score`, `avg_log_loss` y `matches_included = 50` (o menos, si aún no hay 50 disponibles).

## Escenario 2 — Auditar un partido individual
1. Llamar `GET /api/track-record/matches` y tomar un `match_id` de la respuesta.
2. Verificar: `predicted_1x2` (la predicción original) y `real_result` aparecen juntos, permitiendo comparar visualmente.

## Escenario 3 — Comparación log-loss vs. mercado
1. Asegurarse de que al menos algunos de los partidos evaluados tengan `CuotaMercado` cargada.
2. Llamar `GET /api/track-record`.
3. Verificar: `avg_market_log_loss` está presente y es comparable a `avg_log_loss`.

## Escenario 4 — Partido pospuesto no cuenta hasta que se juegue
1. Marcar un partido con predicción como `estado = pospuesto`.
2. Ejecutar el job `update_track_record`.
3. Verificar: ese partido no aparece en `matches_included` ni afecta `hit_rate`/`avg_brier_score` hasta que su estado cambie a `jugado`.

## Escenario 5 — Partido sin cuota de mercado
1. Marcar un partido evaluado con `tiene_cuota_mercado = false`.
2. Llamar `GET /api/track-record`.
3. Verificar: ese partido sí cuenta para `hit_rate` y `avg_brier_score`, pero no para `avg_market_log_loss`.

## Escenario 6 — Filtrar por liga
1. Llamar `GET /api/track-record?league=laliga`.
2. Verificar: los valores devueltos corresponden solo a partidos de LaLiga, distintos del agregado global.
