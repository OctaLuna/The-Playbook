# Tareas: Predicción de Partido (1X2, Over/Under, BTTS, xG y Confianza)

**Fuente:** `plan.md` (+ `data-model.md`, `ml-design.md`, `contracts/matches-api.md`, `quickstart.md`)
**Convención:** `[P]` = se puede ejecutar en paralelo con otras tareas `[P]`
del mismo grupo (no comparten archivos ni dependen entre sí).

## Grupo 0 — Arranque del stack

> Es el primer trabajo del proyecto. Sin él, `T001` no se puede escribir: no hay app FastAPI
> que importar, ni base de datos contra la que correr, ni dependencias declaradas. Las tareas
> `B0X` trazan a artículos de la constitución en vez de a un `RF-00X` porque son
> infraestructura, no capacidades de producto. Bloquean también a 002, 003 y 004.

- [ ] B01 Declarar las dependencias reales en `backend/pyproject.toml` (hoy `dependencies = []`): `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic-settings`, `celery`, `redis`, y `httpx` en el extra `dev` — [Art. IX]
- [ ] B02 `infra/docker-compose.yml`: PostgreSQL 16 con extensión **pgvector**, Redis, y healthchecks en ambos. Es el servicio real que exige el Artículo IX y el `docker-compose up` con el que empiezan los tres `quickstart.md` — [Art. IX]
- [ ] B03 [P] `.env.example` con placeholders (nunca valores reales) y `backend/app/core/config.py` con Pydantic Settings leyendo `DATABASE_URL`, `REDIS_URL` y las credenciales IAM/Bedrock — [Art. VI]
- [ ] B04 `backend/app/db/session.py`: engine async, `async_sessionmaker`, y la dependencia `get_session` que consumirán los routers — [Art. VIII]
- [ ] B05 Fixtures en `backend/tests/conftest.py`: cliente async vía `httpx.ASGITransport` y sesión de BD contra el **Postgres real** del compose, con rollback por test. Sin mocks (Art. IX) — [Art. IX]
- [ ] B06 Prueba de contrato `GET /health` en `backend/tests/contract/test_health.py` y **confirmar que falla** — [Art. III]
- [ ] B07 `backend/app/main.py`: app FastAPI mínima con `/health`, que hace pasar B06. Sin lógica de negocio — [Art. I]
- [ ] B08 `backend/alembic.ini` y `backend/alembic/env.py` apuntando al metadata declarativo, con una revisión inicial vacía que habilite `CREATE EXTENSION vector` — [Art. IX]
- [ ] B09 Verificar el arranque completo: `docker compose -f infra/docker-compose.yml up -d` levanta, `pytest` corre, `GET /health` responde 200, y `alembic upgrade head` aplica sin error — [Art. IX]

## Grupo 1 — Contratos y pruebas (test-first)
- [ ] T001 [P] Prueba de contrato GET `/api/leagues` en `backend/tests/contract/test_leagues.py` — [RF-008]
- [ ] T002 [P] Prueba de contrato GET `/api/matches/upcoming` (con filtro `league` y paginación) en `backend/tests/contract/test_matches_upcoming.py` — [RF-008]
- [ ] T003 [P] Prueba de contrato GET `/api/matches/{match_id}` (incluye caso 404) en `backend/tests/contract/test_match_detail.py` — [RF-006]
- [ ] T004 [P] Prueba de contrato GET `/api/matches/{match_id}/prediction` (incluye caso 404 sin predicción generada) en `backend/tests/contract/test_match_prediction.py` — [RF-001, RF-002, RF-003, RF-004, RF-005]
- [ ] T005 Confirmar que T001-T004 fallan (fase Red) antes de continuar — [Art. III]

## Grupo 2 — Modelo de datos
- [ ] T006 [P] Crear modelo SQLAlchemy `Partido` en `backend/app/models/partido.py` (enum `liga` con las 5 ligas, enum `estado`: programado/jugado/pospuesto/cancelado, `resultado_real` nullable) — [RF-008, RF-009]
- [ ] T007 [P] Crear modelo SQLAlchemy `Equipo` en `backend/app/models/equipo.py` (incluye `tiene_historial_suficiente`) — [RF-001, RF-010]
- [ ] T008 [P] Crear modelo SQLAlchemy `Predicción` en `backend/app/models/prediccion.py`: `top_shap_features` como campo interno JSON, `version_modelo`, y **solo** `prob_over_2_5` y `prob_btts_si` — los complementos se derivan en el schema, no se persisten — [RF-001, RF-002, RF-003, RF-004]
- [ ] T009 [P] Crear modelo SQLAlchemy `CalibraciónHistórica` en `backend/app/models/calibracion_historica.py` — [RF-005, RF-005b]
- [ ] T010 Migración Alembic inicial: las 4 tablas más los índices y restricciones de `data-model.md` — índice compuesto `(fecha_kickoff, estado)`, `unique(partido_id)` en `Predicción`, y los CHECK de que las probabilidades sumen 1.0 y estén en `[0,1]` (depende de T006-T009) — [RF-001, RF-005, RF-008]
- [ ] T011 [P] Crear schemas Pydantic (`MatchOut`, `PredictionOut`, `LeagueOut`) en `backend/app/schemas/matches.py`, siguiendo exactamente los contratos de `contracts/matches-api.md` (sin incluir `top_shap_features`, que es interno) — [RF-006, RF-008]

## Grupo 3 — Implementación (hace pasar las pruebas del Grupo 1)
- [ ] T012a Declarar las dependencias de ML en `backend/pyproject.toml` — `statsmodels`, `scipy`, `xgboost`, `scikit-learn`, `shap`, `mlflow`, `pandas`, `numpy` — listadas en `ml-design.md` §8. No estaban en el Grupo 0 porque no hacían falta hasta este punto (Art. VII) — [Art. IX]
- [ ] T012b Implementar `backend/ml/data/`: carga de Football-Data.co.uk, tabla de alias de equipo, y el mapeo de columnas de `ml-design.md` §1 (falla explícito ante un nombre de equipo sin alias, nunca crea un `Equipo` duplicado) — [RF-008]
- [ ] T012c Implementar `backend/ml/features/`: el feature set cerrado de `ml-design.md` §4 (forma, descanso, head-to-head, fuerza relativa de Dixon-Coles) — [RF-001, RF-002, RF-003]
- [ ] T012d Implementar `backend/ml/models/dixon_coles/train.py`, `predict.py` y `evaluate.py`: la formulación exacta (α/β/γ/ρ/ξ) y el default `ξ = 0.0018` de `ml-design.md` §3 — [RF-001, RF-002, RF-003, RF-004]
- [ ] T012e Implementar `backend/ml/models/xgboost/train.py`, `predict.py` y `evaluate.py` sobre el feature set de T012c — [RF-001, RF-002, RF-003]
- [ ] T012 Implementar `backend/ml/ensemble/predict.py`: combina Dixon-Coles + XGBoost por promedio ponderado, con el algoritmo de grid search de `w` y el peso mínimo `0.85` de `ml-design.md` §5 (sección 6.4 de project_spec.md) — [RF-001, RF-002, RF-003, RF-004]
- [ ] T013 Implementar `backend/ml/evaluation/calibration.py`: buckets, fórmula de `precision_empirica` y el default `n_observaciones = 30` de `ml-design.md` §6; lookup de `CalibraciónHistórica` por (mercado, rango de probabilidad) → nivel de confianza; "baja" si está bajo el umbral — [RF-005, RF-005b]
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
- [ ] T025 [P] Registrar en MLflow los pesos finales del ensamble siguiendo la convención de `ml-design.md` §7 (experimento por mercado, run nombrado por fecha+commit, params/métricas/artefactos) como evidencia para la defensa académica — [Art. II]

---
**Regla:** cada tarea debe ser lo bastante concreta para completarla sin
volver a abrir `spec.md`. Si una tarea requiere una decisión no tomada en el
plan, regresa a `/plan` (o pide clarificación) antes de marcarla lista.
