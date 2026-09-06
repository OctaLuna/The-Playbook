# Plan de implementación: Track Record Público del Modelo

**Basado en:** `specs/003-track-record-publico/spec.md`
**Stack propuesto por el usuario:** El definido en `docs/project_spec.md` (secciones 4, 5 y 9) — FastAPI + SQLAlchemy 2.0 async sobre PostgreSQL 16, Celery + Redis para el recálculo periódico, reutilizando `backend/ml/evaluation/` (log-loss, Brier score, backtesting cronológico) ya existente para 001.

## Resumen técnico

Esta feature agrega, en un panel público, el desempeño real del modelo sobre los últimos 50 partidos predichos (RF-006), comparado contra el baseline de log-loss implícito del mercado (RF-004), filtrable por liga (RF-007). Lee `Partido.resultado_real` y `Predicción` (ambos persistidos por 001) una vez que el partido ya se jugó, calcula el acierto/Brier/log-loss por partido, y expone tanto el agregado como el detalle partido a partido (Historia 2, auditoría).

Un job periódico diario de Celery (`backend/workers/tasks/update_track_record.py`) recalcula el agregado tras cada jornada — nunca se recalcula de forma síncrona dentro del endpoint GET (Artículo VI). Cada evaluación queda asociada a la `version_modelo` que generó la predicción original (ya persistida en 001), de modo que un reentrenamiento a mitad de la ventana de 50 partidos no mezcla silenciosamente el desempeño de dos versiones distintas. Las cuotas de mercado se usan exclusivamente como referencia interna de comparación — esta feature nunca expone un comparador de casas de apuestas independiente (RF-005, Artículo V).

## Fase -1: Gates previos a la implementación

### Gate de simplicidad (Artículo VII)
- [x] ¿Se usan ≤3 proyectos/módulos? Sí — vive dentro de `backend/app/`, `backend/ml/evaluation/` (reutilizado, no duplicado) y `backend/workers/`, sin proyectos nuevos.
- [x] ¿No hay "future-proofing"? Sí — el filtro es solo por liga (RF-007 ya resuelto); no se construye un motor de filtros genérico para dimensiones no pedidas (equipo, mercado individual).

### Gate anti-abstracción (Artículo VIII)
- [x] ¿Se usa el framework directamente? Sí — se reutilizan las funciones de `backend/ml/evaluation/` (log-loss, Brier) ya existentes para 001, en vez de reimplementar una segunda vez las métricas para el track record.
- [x] ¿Una sola representación del modelo de datos? Sí — `EvaluaciónPredicción` es la única entidad que conecta `Predicción` (001) con `Partido.resultado_real`; no hay una segunda tabla paralela de "resultados" duplicada.

### Gate integration-first (Artículo IX)
- [x] Contratos definidos — ver `contracts/track-record-api.md`.
- [x] Pruebas de contrato para los 2 endpoints antes de implementar los routers, contra una instancia real de Postgres con datos de partidos ya finalizados (no mocks, viable aquí porque no depende de servicios externos costosos como Bedrock).

### Cumplimiento constitucional (Artículos IV-VI del proyecto)
- [x] **Artículo IV:** solo se evalúan partidos con `estado = jugado` y `resultado_real` ya lleno — nunca se calcula desempeño sobre un partido futuro o en curso.
- [x] **Artículo V:** las cuotas de mercado (`CuotaMercado`) se usan únicamente para el cálculo de `log_loss_mercado_contribution`; no existe ningún endpoint ni campo que exponga un comparador de casas de apuestas como funcionalidad independiente (RF-005).
- [x] **Artículo VI:** el recálculo del agregado corre vía Celery (`backend/workers/tasks/update_track_record.py`, job diario ya resuelto en Clarify); el endpoint `GET /api/track-record` solo lee la tabla `TrackRecordAgregado` ya calculada.

## Decisiones técnicas y su porqué

| Decisión | Alternativas consideradas | Por qué esta opción | Requisito que satisface |
|---|---|---|---|
| Job diario de Celery recalcula un agregado cacheado (`TrackRecordAgregado`) en vez de calcular on-the-fly en cada request | Calcular el agregado en tiempo real en el endpoint GET | Evita una agregación pesada (últimos 50 partidos × N ligas) en el path de request HTTP (Artículo VI); ya resuelto en Clarify | Historia 1, escenario 2 |
| Reutilizar `backend/ml/evaluation/` para Brier/log-loss en vez de reimplementar | Implementar cálculo de métricas propio para el track record | Garantiza que el panel público sea *exactamente* la misma métrica que usa el equipo internamente (CE-001); evita duplicar lógica ya cubierta por el test de split cronológico | RF-002, CE-001 |
| `version_modelo` (ya persistido en `Predicción` por 001) se copia a `EvaluaciónPredicción` en el momento de evaluar | Recalcular la versión del modelo a partir de la fecha de la predicción | Trazabilidad directa sin depender de inferir qué versión estaba activa en una fecha dada | Caso límite de reentrenamiento a mitad de ventana |
| Partido sin cuota de mercado: se excluye solo de `log_loss_mercado_contribution`, cuenta igual para accuracy/Brier propios | Excluir el partido de todo el track record | El % de aciertos y Brier del modelo no dependen de que exista una cuota; excluir de todo perdería datos sin necesidad (ya resuelto en Clarify) | Caso límite de cuota faltante |
| Filtro por liga vía query param + índice compuesto `(liga, fecha_partido)` en Postgres | Pre-calcular un agregado separado por liga en Celery | Un solo agregado global + filtro a demanda es más simple (Artículo VII) mientras el volumen de partidos evaluados sea manejable; se puede revisar si el volumen crece | RF-007 |

## Modelo de datos (resumen — detalle en data-model.md)
Tres entidades: `EvaluaciónPredicción` (1:1 con Predicción de 001, calculada solo para partidos jugados), `TrackRecordAgregado` (tabla cacheada, recalculada diariamente, una fila por combinación liga/global) y `CuotaMercado` (cuota histórica u operativa asociada a un partido, usada solo como baseline). Detalle completo en `data-model.md`.

## Contratos (resumen — detalle en contracts/)
Dos endpoints de solo lectura: el agregado del track record (filtrable por liga) y el detalle paginado partido a partido para auditoría. Detalle completo en `contracts/track-record-api.md`.

## Orden de creación de archivos (test-first, obligatorio)
1. `contracts/track-record-api.md` — ya definido en este plan.
2. Tests, en este orden:
   - Pruebas de contrato de los 2 endpoints (`backend/tests/contract/test_track_record_api.py`)
   - Prueba de integración: el job diario de Celery recalcula `TrackRecordAgregado` correctamente tras marcar un partido como jugado (`backend/tests/integration/test_update_track_record.py`)
   - Prueba de integración: un partido sin `CuotaMercado` cuenta para accuracy/Brier pero no para la comparación de mercado
   - Pruebas unitarias de la reutilización de `backend/ml/evaluation/` para el cálculo por partido
3. Código fuente, en este orden: modelos SQLAlchemy (`EvaluaciónPredicción`, `TrackRecordAgregado`, `CuotaMercado`) → `backend/app/services/track_record_service.py` (usa `backend/ml/evaluation/`) → `backend/workers/tasks/update_track_record.py` → routers de `backend/app/api/track_record`.

## Registro de complejidad
Ningún gate de la Fase -1 falló — no aplica registro de complejidad.

## Validación / Quickstart (resumen — detalle en quickstart.md)
Los escenarios clave: (1) ver el agregado de los últimos 50 partidos, (2) auditar un partido individual, (3) ver la comparación log-loss vs. mercado, (4) confirmar que un partido pospuesto no cuenta hasta que se juegue, (5) confirmar que un partido sin cuota cuenta para accuracy pero no para la comparación de mercado, (6) filtrar por liga. Detalle paso a paso en `quickstart.md`.
