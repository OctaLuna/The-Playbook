# Tareas: Explicación en Lenguaje Natural de la Predicción

**Fuente:** `plan.md` (+ `data-model.md`, `contracts/explanations-api.md`, `quickstart.md`)
**Convención:** `[P]` = se puede ejecutar en paralelo con otras tareas `[P]`
del mismo grupo (no comparten archivos ni dependen entre sí).

## Grupo 1 — Contratos y pruebas (test-first)
- [ ] T001 Prueba de integración del filtro temporal obligatorio (Artículo IV / sección 7.3) contra pgvector real, con caso construido a propósito, en `backend/tests/integration/test_temporal_filter.py` — la más crítica del feature, se escribe primero — [RF-002]
- [ ] T002 [P] Prueba de contrato GET `/api/matches/{match_id}/explanation` (incluye caso 404) en `backend/tests/contract/test_explanations_api.py` — [RF-001]
- [ ] T003 [P] Prueba de contrato POST `/api/matches/{match_id}/explanation/follow-up` (incluye caso 404 sin explicación previa) en `backend/tests/contract/test_explanations_api.py` — [RF-005]
- [ ] T004 Confirmar que T001-T003 fallan (fase Red) antes de continuar — [Art. III]

## Grupo 2 — Modelo de datos
- [ ] T005 [P] Crear modelo SQLAlchemy `Explicación` en `backend/app/models/explicacion.py` (incluye `es_fallback_sin_evidencia`, `shap_features_usadas`) — [RF-001, RF-003]
- [ ] T006 [P] Crear modelo SQLAlchemy `Evidencia` en `backend/app/models/evidencia.py`: `embedding` como `Vector(1024)` (Titan V2), `fecha_publicacion` NOT NULL, y `url` único + `titulo` — [RF-001, RF-002]
- [ ] T006b [P] Crear la tabla puente `ExplicacionEvidencia` en `backend/app/models/explicacion_evidencia.py` con PK compuesta `(explicacion_id, evidencia_id)` y columna `orden` — sustituye al array de identificadores, que no permitiría integridad referencial — [RF-001]
- [ ] T007 [P] Crear modelo SQLAlchemy `PreguntaSeguimiento` en `backend/app/models/pregunta_seguimiento.py` — [RF-005]
- [ ] T008 Migración Alembic: habilitar la extensión `vector`, crear las 4 tablas nuevas, el índice HNSW sobre `Evidencia.embedding`, el índice sobre `Evidencia.fecha_publicacion` y el `unique` sobre `Evidencia.url` (depende de T005-T007) — [RF-002]
- [ ] T009 [P] Crear schemas Pydantic (`ExplanationOut`, `FollowUpRequest`, `FollowUpOut`) en `backend/app/schemas/explanations.py`, siguiendo `contracts/explanations-api.md` — [RF-001, RF-005]

## Grupo 3 — Implementación (hace pasar las pruebas del Grupo 1)
- [ ] T010 [P] Implementar `backend/rag/ingestion/chunking.py`: chunkeo por artículo completo, overlap 15-20% si excede ~500 tokens (sección 7.1) — [RF-001]
- [ ] T011 [P] Implementar `backend/rag/ingestion/sanitizer.py`: sanitización anti-prompt-injection — límite de longitud, remoción de patrones de instrucción evidentes (Artículo VI de la constitución)
- [ ] T012 Implementar `backend/rag/retrieval/query.py`: query a pgvector con `WHERE fecha_publicacion_noticia < fecha_kickoff_del_partido` a nivel SQL — debe hacer pasar T001 — [RF-002]
- [ ] T013 [P] Crear prompts versionados en `backend/rag/generation/prompts/explanation.md` y `backend/rag/generation/prompts/follow_up.md` (archivos propios, no strings embebidos) — [RF-001, RF-004]
- [ ] T014 Implementar `backend/rag/generation/client.py`: cliente Bedrock vía Converse API, incluye el bloque XML delimitado para contenido no confiable + instrucción de sistema que lo ignora como comando — [RF-001]
- [ ] T015 Implementar `backend/rag/generation/cache.py`: caché en Redis, invalidado solo si cambió la evidencia relevante (sección 7.5) — [RF-001, RF-006]
- [ ] T016 Implementar `backend/app/services/explanations_service.py`: orquesta retrieval + generación + fallback de evidencia insuficiente (Historia 2) + inyección de `top_shap_features` leído de la `Predicción` de 001 — [RF-001, RF-003]
- [ ] T017 Implementar routers de `backend/app/api/explanations.py` — delgados, delegan al servicio — debe hacer pasar T002-T003 — [RF-001, RF-005]
- [ ] T018 Implementar `backend/workers/tasks/ingest_news.py` (Celery, scraping periódico) y `backend/workers/tasks/reindex_rag.py` (reindexado más frecuente en horas previas al kickoff) — [RF-001]

## Grupo 4 — Integración
- [ ] T019 Prueba de integración: Historia 1, escenario 1 — explicación cita evidencia real y menciona al menos una variable SHAP
- [ ] T020 Prueba de integración: Historia 2 — equipo/liga sin cobertura mediática devuelve `is_fallback_no_evidence: true`
- [ ] T021 Prueba de integración: Historia 4 — pregunta de seguimiento se ancla a la misma evidencia/SHAP, sin introducir predicción nueva
- [ ] T021b Prueba de integración: RF-004 — para un partido de prueba, comparar el texto generado contra `probabilities_1x2`/`over_under_2_5`/`btts` de la Predicción (001) y verificar que la explicación no afirma un resultado, mercado ganador o número distinto al ya calculado (hallazgo #2 de Analyze) — ver `plan.md` para el criterio exacto de "contradicción" a implementar (comparación de aserciones de resultado, no de texto libre)
- [ ] T022 Prueba manual documentada de groundedness/faithfulness sobre una muestra de explicaciones (sección 7.6) — no bloqueante para el MVP, pero debe quedar reproducible — [RF-001]

## Grupo 5 — Pulido
- [ ] T023 [P] Manejo de error 404 (partido sin predicción, explicación sin generar) documentado en `backend/app/api/explanations.py` — [RF-001]
- [ ] T024 [P] Actualizar `quickstart.md` con comandos definitivos una vez implementado — [Art. IX]
- [ ] T025 [P] Documentar como configuración (no hardcodeado) el umbral de groundedness/faithfulness que dispara alerta (sección 7.6) — [RF-001]

---
**Regla:** cada tarea debe ser lo bastante concreta para completarla sin
volver a abrir `spec.md`. Si una tarea requiere una decisión no tomada en el
plan, regresa a `/plan` (o pide clarificación) antes de marcarla lista.
