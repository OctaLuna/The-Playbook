# Quickstart: Validación manual de Explicación en Lenguaje Natural (T024)

**Basado en:** `specs/002-explicacion-lenguaje-natural/spec.md`, `plan.md` y `contracts/explanations-api.md`

Este documento proporciona los pasos concretos y comandos HTTP definitivos para validar la feature de RAG y explicabilidad.

---

## Prerrequisitos
1. Levantar la infraestructura local:
   ```bash
   docker compose -f infra/docker-compose.yml up -d
   ```
2. Ejecutar las migraciones de Alembic:
   ```bash
   cd backend && alembic upgrade head
   ```
3. Levantar la API FastAPI:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## Escenario 1 — Explicación con evidencia real disponible (Historia 1 / RF-001)
1. Indexar noticias previas al partido mediante la tarea Celery o endpoint de prueba con `fecha_publicacion < fecha_kickoff`.
2. Consultar la explicación del partido:
   ```bash
   curl -X GET "http://localhost:8000/api/matches/{match_id}/explanation" \
        -H "Accept: application/json"
   ```
3. **Verificación:**
   - Código HTTP 200.
   - `text` cita la evidencia relevante y menciona al menos una variable SHAP.
   - `is_fallback_no_evidence` es `false`.
   - `evidence` contiene la lista de noticias con `title`, `url`, `source` y `published_at`.

---

## Escenario 2 — Aviso honesto de evidencia insuficiente (Historia 2 / RF-003)
1. Para un partido sin cobertura mediática indexada, llamar:
   ```bash
   curl -X GET "http://localhost:8000/api/matches/{match_id}/explanation"
   ```
2. **Verificación:**
   - Código HTTP 200.
   - `is_fallback_no_evidence` es `true`.
   - `evidence` es una lista vacía `[]`.
   - `text` declara explícitamente la ausencia de cobertura periodística, sin inventar hechos.

---

## Escenario 3 — Nunca citar evidencia posterior al kickoff (Artículo IV / RF-002)
1. Con una noticia indexada con `fecha_publicacion >= fecha_kickoff` (crónica posterior al partido):
2. Consultar el endpoint de explicación.
3. **Verificación:**
   - La noticia del futuro **NUNCA** aparece en el array `evidence` ni se menciona en `text`.
   - Verificado de manera automatizada mediante `pytest tests/integration/test_temporal_filter.py`.

---

## Escenario 4 — Pregunta de seguimiento (Historia 4 / RF-005)
1. Con una explicación base ya generada, realizar una pregunta de seguimiento:
   ```bash
   curl -X POST "http://localhost:8000/api/matches/{match_id}/explanation/follow-up" \
        -H "Content-Type: application/json" \
        -d '{"question": "¿Por qué pesa tanto la lesión del delantero?"}'
   ```
2. **Verificación:**
   - Código HTTP 200.
   - `answer` responde anclándose en la evidencia y SHAP de la explicación original.
   - No introduce predicciones nuevas ni contradice las probabilidades numéricas.
   - Devuelve 404 si se intenta hacer follow-up a un partido sin explicación previa.
