# Tareas: Track Record Público del Modelo

**Fuente:** `plan.md` (+ `data-model.md`, `contracts/track-record-api.md`, `quickstart.md`)
**Convención:** `[P]` = se puede ejecutar en paralelo con otras tareas `[P]`
del mismo grupo (no comparten archivos ni dependen entre sí).

## Grupo 1 — Contratos y pruebas (test-first)
- [ ] T001 [P] Prueba de contrato GET `/api/track-record` (con y sin filtro `league`) en `backend/tests/contract/test_track_record_api.py`
- [ ] T002 [P] Prueba de contrato GET `/api/track-record/matches` (paginado, filtro `league`) en `backend/tests/contract/test_track_record_api.py`
- [ ] T002b [P] Prueba de contrato negativa: RF-005 — verificar que ninguna respuesta de `/api/track-record` ni `/api/track-record/matches` incluye cuotas individuales por casa de apuestas (ej. un campo `bookmaker_odds` o similar); solo debe existir el agregado `avg_market_log_loss` (hallazgo #5 de Analyze)
- [ ] T003 Confirmar que T001-T002 fallan (fase Red) antes de continuar

## Grupo 2 — Modelo de datos
- [ ] T004 [P] Crear modelo SQLAlchemy `EvaluaciónPredicción` en `backend/app/models/evaluacion_prediccion.py` (incluye `version_modelo`, `tiene_cuota_mercado`)
- [ ] T005 [P] Crear modelo SQLAlchemy `TrackRecordAgregado` en `backend/app/models/track_record_agregado.py` (fila `liga = null` para el agregado global)
- [ ] T006 [P] Crear modelo SQLAlchemy `CuotaMercado` en `backend/app/models/cuota_mercado.py`
- [ ] T007 Migración Alembic para las 3 tablas (depende de T004-T006)
- [ ] T008 [P] Crear schemas Pydantic (`TrackRecordSummaryOut`, `TrackRecordMatchOut`) en `backend/app/schemas/track_record.py`, siguiendo `contracts/track-record-api.md`

## Grupo 3 — Implementación (hace pasar las pruebas del Grupo 1)
- [ ] T009 Implementar `app/services/track_record_service.py`: reutiliza `ml/evaluation/` (log-loss, Brier) ya existente para 001 — no reimplementar las métricas
- [ ] T010 Implementar el cálculo de `log_loss_mercado_contribution` a partir de `CuotaMercado`, solo cuando `tiene_cuota_mercado = true`
- [ ] T011 Implementar `workers/tasks/update_track_record.py`: job diario de Celery que recalcula `TrackRecordAgregado` (global y por liga) a partir de partidos con `estado = jugado`
- [ ] T012 Implementar routers de `app/api/track_record.py` (2 endpoints, filtro `league`) — solo lectura de `TrackRecordAgregado`/`EvaluaciónPredicción`, debe hacer pasar T001-T002

## Grupo 4 — Integración
- [ ] T013 Prueba de integración: Historia 1, escenario 1 — agregado de los últimos 50 partidos con `hit_rate`, `avg_brier_score`, `avg_log_loss`
- [ ] T014 Prueba de integración: Historia 1, escenario 2 — el job diario actualiza `TrackRecordAgregado` tras marcar un nuevo partido como jugado
- [ ] T015 Prueba de integración: Historia 2 — el detalle partido a partido muestra `predicted_1x2` y `real_result` juntos
- [ ] T016 Prueba de integración: Historia 3 — `avg_market_log_loss` se calcula correctamente y es comparable a `avg_log_loss`
- [ ] T017 Prueba de integración: caso límite — partido `pospuesto` no se incluye en `matches_included` hasta que cambia a `jugado`
- [ ] T017b Prueba de integración: caso límite — simular un reentrenamiento a mitad de la ventana de 50 partidos (dos `version_modelo` distintas dentro del mismo período) y verificar que `EvaluaciónPredicción` conserva la versión correcta por partido, y que `GET /api/track-record/matches` la refleja sin mezclar versiones (hallazgo #6 de Analyze)
- [ ] T018 Prueba de integración: caso límite — partido sin `CuotaMercado` cuenta para `hit_rate`/`avg_brier_score` pero no para `avg_market_log_loss`
- [ ] T019 Verificar que esta feature reutiliza (no reintroduce) el test existente en `ml/features/` que bloquea columnas de odds en el feature set de entrenamiento (Artículo V) — confirma que no se abre una vía nueva de fuga de cuotas hacia el modelo

## Grupo 5 — Pulido
- [ ] T020 [P] Manejo del caso `matches_included < 50` (aún no hay suficientes partidos jugados para completar la ventana) en la respuesta de `GET /api/track-record`
- [ ] T021 [P] Actualizar `quickstart.md` con comandos definitivos una vez implementado
- [ ] T022 [P] Registrar en `docs/adr/` la decisión de excluir partidos sin cuota solo del baseline de mercado (trazabilidad para la defensa académica)

---
**Regla:** cada tarea debe ser lo bastante concreta para completarla sin
volver a abrir `spec.md`. Si una tarea requiere una decisión no tomada en el
plan, regresa a `/plan` (o pide clarificación) antes de marcarla lista.
