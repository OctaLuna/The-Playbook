# Tareas: Predicción de Partido (1X2, Over/Under, BTTS, xG y Confianza)

**Fuente:** `plan.md` (+ `data-model.md`, `contracts/matches-api.md`, `quickstart.md`)
**Convención:** `[P]` = se puede ejecutar en paralelo con otras tareas `[P]`
del mismo grupo (no comparten archivos ni dependen entre sí).

## Grupo 1 — Contratos y pruebas (test-first)
- [ ] T001 [P] Prueba de contrato GET `/api/leagues` en `backend/tests/contract/test_leagues.py` — [RF-008]
- [ ] T002 [P] Prueba de contrato GET `/api/matches/upcoming` (con filtro `league` y paginación) en `backend/tests/contract/test_matches_upcoming.py` — [RF-008]
- [ ] T003 [P] Prueba de contrato GET `/api/matches/{match_id}` (incluye caso 404) en `backend/tests/contract/test_match_detail.py` — [RF-006]
- [ ] T004 [P] Prueba de contrato GET `/api/matches/{match_id}/prediction` (incluye caso 404 sin predicción generada) en `backend/tests/contract/test_match_prediction.py` — [RF-001, RF-002, RF-003, RF-004, RF-005]
- [ ] T005 Confirmar que T001-T004 fallan (fase Red) antes de continuar — [Art. III]

## Grupo 2 — Modelo de datos
- [ ] T006 [P] Crear modelo SQLAlchemy `Partido` en `backend/app/models/partido.py` (enum `liga` con las 5 ligas, enum `estado`: programado/jugado/pospuesto/cancelado) — [RF-008]
- [ ] T007 [P] Crear modelo SQLAlchemy `Equipo` en `backend/app/models/equipo.py` (incluye `tiene_historial_suficiente`) — [RF-001, RF-010]
- [ ] T008 [P] Crear modelo SQLAlchemy `Predicción` en `backend/app/models/prediccion.py` (incluye `top_shap_features` como campo interno JSON, `version_modelo`) — [RF-001, RF-002, RF-003, RF-004]
- [ ] T009 [P] Crear modelo SQLAlchemy `CalibraciónHistórica` en `backend/app/models/calibracion_historica.py` — [RF-005, RF-005b]
- [ ] T010 Migración Alembic inicial para las 4 tablas (depende de T006-T009) — [RF-001, RF-005, RF-008]
- [ ] T011 [P] Crear schemas Pydantic (`MatchOut`, `PredictionOut`, `LeagueOut`) en `backend/app/schemas/matches.py`, siguiendo exactamente los contratos de `contracts/matches-api.md` (sin incluir `top_shap_features`, que es interno) — [RF-006, RF-008]

## Grupo 3 — Implementación (hace pasar las pruebas del Grupo 1)
- [ ] T012 Implementar `backend/ml/ensemble/predict.py`: combina Dixon-Coles + XGBoost por promedio ponderado, pesos leídos desde MLflow (sección 6.4 de project_spec.md) — [RF-001, RF-002, RF-003, RF-004]
- [ ] T013 Implementar `backend/ml/evaluation/calibration.py`: lookup de `CalibraciónHistórica` por (mercado, rango de probabilidad) → nivel de confianza; default "baja" si `n_observaciones` está bajo el umbral — [RF-005, RF-005b]
- [ ] T014 Implementar `backend/app/services/predictions_service.py`: orquesta lectura de `Partido`/`Equipo`/`Predicción`, arma `low_data_warning` (a partir de `tiene_historial_suficiente`) y `head_to_head_available` — [RF-006]
- [ ] T015 Implementar routers de `backend/app/api/matches.py` para los 4 endpoints — delgados, delegan a `predictions_service` — debe hacer pasar T001-T004 — [RF-006, RF-008]
- [ ] T016 Implementar `backend/workers/tasks/generate_predictions.py`: tarea Celery que genera predicciones para partidos dentro de la ventana de 24h antes del kickoff (RF-007), persiste `Predicción` incl. `top_shap_features` y `version_modelo`

## Grupo 4 — Integración
- [ ] T017 Prueba de integración: Historia 1, escenario 1 — partido con datos suficientes devuelve 1X2 que suma 1.0 — [RF-001]
- [ ] T018 Prueba de integración: Historia 1, escenario 2 — equipo con `tiene_historial_suficiente = false` devuelve `low_data_warning: true` — [RF-010]
- [ ] T019 Prueba de integración: Historia 4, escenario 2 — rango de probabilidad sin calibración suficiente devuelve `confidence: "baja"` por defecto — [RF-005b]
- [ ] T020 Prueba de integración: caso límite — partido marcado `pospuesto` conserva su predicción original y devuelve `status: "postponed"` — [RF-009]
- [ ] T021 Prueba de integración: caso límite — partido sin head-to-head previo devuelve `head_to_head_available: false` — [RF-010]
- [ ] T022 Verificar que el pipeline de esta feature efectivamente reutiliza (no reescribe) el test existente en `backend/ml/features/` que bloquea columnas de odds en el feature set (Artículo V)

## Grupo 5 — Pulido
- [ ] T023 [P] Manejo de errores 404 documentado (partido inexistente, predicción aún no generada) en las respuestas de `backend/app/api/matches.py` — [RF-006]
- [ ] T024 [P] Actualizar `quickstart.md` reemplazando los comandos de ejemplo por los definitivos una vez implementado — [Art. IX]
- [ ] T025 [P] Registrar en MLflow los pesos finales del ensamble (sección 6.4) como evidencia para la defensa académica — [Art. II]

---
**Regla:** cada tarea debe ser lo bastante concreta para completarla sin
volver a abrir `spec.md`. Si una tarea requiere una decisión no tomada en el
plan, regresa a `/plan` (o pide clarificación) antes de marcarla lista.
