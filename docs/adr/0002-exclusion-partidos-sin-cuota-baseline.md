# ADR 0002 — Exclusión de partidos sin cuota únicamente del baseline de mercado

**Estado:** Aceptado
**Fecha:** 2026-11-15
**Origen:** T022 de `specs/003-track-record-publico/tasks.md` · Hallazgo #5 de Analyze · RF-004
**Afecta a:** `specs/003-track-record-publico/` (`spec.md`, `data-model.md`, `plan.md`) · `backend/app/services/track_record_service.py`

## Contexto

En el panel público del Track Record (Feature 003), se comparan las métricas probabilísticas del modelo contra el consenso de mercado derivado de cuotas históricas u operativas (Bet365 / Football-Data.co.uk / API-Football).

En la práctica, ciertas ligas, divisiones o fechas pueden carecer de cuotas registradas para determinados partidos (por ejemplo, partidos reprogramados con poca liquidez, retrasos en la ingesta o falta de cobertura de bookmakers en la fuente secundaria).

Surgieron dos enfoques posibles para tratar los partidos sin cuota:
1. **Excluir el partido por completo** de la ventana de los últimos 50 partidos del track record público.
2. **Excluir el partido únicamente del cálculo de `avg_market_log_loss`**, manteniéndolo en el cómputo de `hit_rate`, `avg_brier_score` y `avg_log_loss` del modelo.

## Decisión

**Se adopta la opción 2: El partido sin cuota cuenta con total normalidad para el desempeño del modelo y se excluye únicamente del baseline de mercado.**

En términos del modelo de datos:
* La tabla `evaluaciones_prediccion` marca `tiene_cuota_mercado = false` y `log_loss_mercado_1x2 = null`.
* El campo `matches_included` refleja el total de partidos evaluados por el modelo dentro de la ventana de 50.
* El campo `market_baseline_matches` en la respuesta pública (`GET /api/track-record`) explicita exactamente sobre cuántos partidos con cuota se calculó el `avg_market_log_loss`.

## Justificación

1. **Integridad del Track Record del modelo:** El acierto y la calibración del modelo dependen exclusivamente de la predicción emitida y del resultado deportivo real (`goles_local`, `goles_visitante`). Excluir partidos válidos del track record distorsionaría la muestra de desempeño real prometida en el pilar 3 del product goal.
2. **Transparencia y no-sesgo:** Descartar partidos porque una casa de apuestas no publicó cuota crearía un sesgo de selección artificial (selection bias), eliminando potencialmente partidos atípicos o difíciles.
3. **Auditabilidad académica:** Al exponer de forma explícita `matches_included` junto a `market_baseline_matches`, el usuario y el tribunal examinador pueden verificar exactamente qué proporción de la muestra pudo contrastarse con el consenso de mercado.
4. **Respeto a la Constitución del proyecto:** La comparación utiliza cuotas normalizadas (descontando el overround) únicamente como referencia agregada, cumpliendo el Artículo V de `memory/constitution.md`.

## Consecuencias

* `TrackRecordAgregado.log_loss_mercado_promedio` promedia únicamente las filas con `tiene_cuota_mercado = true`.
* La API pública (`GET /api/track-record`) expone `market_baseline_matches` en el schema `MarketSummaryOut`, permitiendo a los clientes web y consumidores entender cuándo la muestra de mercado difiere del total de partidos predichos.
* Se evita cualquier fallo silencioso en el pipeline de recálculo diario cuando una fuente de cuotas no está disponible.
