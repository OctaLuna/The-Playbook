# Tareas: Track Record Público del Modelo

**Fuente:** `plan.md` (+ `data-model.md`, `contracts/track-record-api.md`, `quickstart.md`)
**Convención:** `[P]` = se puede ejecutar en paralelo con otras tareas `[P]`
del mismo grupo (no comparten archivos ni dependen entre sí).

## Grupo 1 — Contratos y pruebas (test-first)
- [ ] T001 [P] Prueba de contrato GET `/api/track-record` (con y sin filtro `league`; verifica que `markets` trae las tres entradas) en `backend/tests/contract/test_track_record_api.py` — [RF-001, RF-002, RF-006, RF-007]
- [ ] T002 [P] Prueba de contrato GET `/api/track-record/matches` (paginado, filtro `league`) en `backend/tests/contract/test_track_record_api.py` — [RF-003, RF-007]
- [ ] T002b [P] Prueba de contrato negativa: RF-005 — verificar que ninguna respuesta de `/api/track-record` ni `/api/track-record/matches` incluye cuotas individuales por casa de apuestas (ej. un campo `bookmaker_odds` o similar); solo debe existir el agregado `avg_market_log_loss` (hallazgo #5 de Analyze)
- [ ] T003 Confirmar que T001-T002 fallan (fase Red) antes de continuar — [Art. III]

## Grupo 2 — Modelo de datos
- [ ] T004 [P] Crear modelo SQLAlchemy `EvaluaciónPredicción` en `backend/app/models/evaluacion_prediccion.py`: acierto, Brier y log-loss **por cada uno de los tres mercados**, más `version_modelo` y `tiene_cuota_mercado` — [RF-001, RF-002, RF-003, RF-010]
- [ ] T005 [P] Crear modelo SQLAlchemy `TrackRecordAgregado` en `backend/app/models/track_record_agregado.py`: una fila por `(liga, mercado)`, con `liga = null` para el agregado global y `versiones_modelo` como array — [RF-001, RF-002, RF-007, RF-010]
- [ ] T006 [P] Crear modelo SQLAlchemy `CuotaMercado` en `backend/app/models/cuota_mercado.py` (guarda probabilidades implícitas, nunca la cuota cruda) — [RF-004]
- [ ] T007 Migración Alembic para las 3 tablas más sus restricciones: `unique(prediccion_id)`, `unique(liga, mercado, ventana_n)` y `unique(partido_id, fuente)` (depende de T004-T006) — [RF-001, RF-003, RF-004]
- [ ] T008 [P] Crear schemas Pydantic (`TrackRecordSummaryOut` con el array `markets`, `TrackRecordMatchOut`) en `backend/app/schemas/track_record.py`, siguiendo `contracts/track-record-api.md` — [RF-001, RF-003]

## Grupo 3 — Implementación (hace pasar las pruebas del Grupo 1)
- [ ] T009 Implementar `backend/app/services/track_record_service.py`: evalúa los tres mercados reutilizando `backend/ml/evaluation/` (log-loss, Brier) ya existente para 001 — no reimplementar las métricas — [RF-001, RF-002]
- [ ] T010 Implementar el cálculo de `log_loss_mercado_1x2` a partir de `CuotaMercado`, solo cuando `tiene_cuota_mercado = true` y aplicando la precedencia de fuentes de `data-model.md` — [RF-004]
- [ ] T011 Implementar `backend/workers/tasks/update_track_record.py`: job diario de Celery que recalcula `TrackRecordAgregado` para cada `(liga, mercado)` a partir de partidos con `estado = jugado`, excluyendo pospuestos y cancelados — [RF-001, RF-002, RF-006, RF-007, RF-008, RF-011]
- [ ] T012 Implementar routers de `backend/app/api/track_record.py` (2 endpoints, filtro `league`) — solo lectura de `TrackRecordAgregado`/`EvaluaciónPredicción`, debe hacer pasar T001-T002 — [RF-001, RF-003, RF-007]

## Grupo 4 — Integración
- [ ] T013 Prueba de integración: Historia 1, escenario 1 — el agregado de los últimos 50 partidos devuelve las **tres** entradas de `markets` (1x2, over_under_2_5, btts), cada una con `hit_rate`, `avg_brier_score` y `avg_log_loss` — [RF-001, RF-002]
- [ ] T013b Prueba de integración: un partido con `resultado_real` conocido produce el `acierto_over_under_2_5` y el `acierto_btts` correctos — con un caso de cada signo, no solo aciertos — [RF-001]
- [ ] T014 Prueba de integración: Historia 1, escenario 2 — el job diario actualiza `TrackRecordAgregado` tras marcar un nuevo partido como jugado — [RF-008]
- [ ] T015 Prueba de integración: Historia 2 — el detalle partido a partido muestra las tres predicciones y `real_result` juntos — [RF-003]
- [ ] T016 Prueba de integración: Historia 3 — `avg_market_log_loss` se calcula correctamente y es comparable a `avg_log_loss` en la entrada `1x2`, y es `null` en las otras dos — [RF-004]
- [ ] T017 Prueba de integración: caso límite — partido `pospuesto` no se incluye en ninguna métrica hasta que cambia a `jugado` — [RF-011]
- [ ] T017b Prueba de integración: caso límite — simular un reentrenamiento a mitad de la ventana de 50 partidos (dos `version_modelo` distintas dentro del mismo período) y verificar que `EvaluaciónPredicción` conserva la versión correcta por partido, que `GET /api/track-record/matches` la refleja sin mezclarlas, y que el agregado expone las dos en `model_versions` (hallazgo #6 de Analyze) — [RF-003, RF-010]
- [ ] T018 Prueba de integración: caso límite — partido sin `CuotaMercado` cuenta para `hit_rate`/`avg_brier_score` pero no para `avg_market_log_loss` — [RF-004]
- [ ] T019 Verificar que esta feature reutiliza (no reintroduce) el test existente en `backend/ml/features/` que bloquea columnas de odds en el feature set de entrenamiento (Artículo V) — confirma que no se abre una vía nueva de fuga de cuotas hacia el modelo

## Grupo 5 — Pulido
- [ ] T020 [P] Manejo del caso `matches_included < 50` (aún no hay suficientes partidos jugados para completar la ventana) en la respuesta de `GET /api/track-record` — [RF-006, RF-009]
- [ ] T021 [P] Actualizar `quickstart.md` con comandos definitivos una vez implementado — [Art. IX]
- [ ] T022 [P] Registrar en `docs/adr/` la decisión de excluir partidos sin cuota solo del baseline de mercado (trazabilidad para la defensa académica) — [RF-004]

---
**Regla:** cada tarea debe ser lo bastante concreta para completarla sin
volver a abrir `spec.md`. Si una tarea requiere una decisión no tomada en el
plan, regresa a `/plan` (o pide clarificación) antes de marcarla lista.
