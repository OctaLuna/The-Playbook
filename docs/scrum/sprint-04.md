# Sprint 4 — Cerrar el núcleo de 001, avanzar 002 y 004

**Semanas:** 7-8 · **Objetivo:** los 4 endpoints de `matches-api.md` responden con datos
reales, calculados por el ensamble. Es la primera vez que el sistema predice de punta a punta.

## Por persona

| Persona | Tareas |
|---|---|
| **Rodrigo** | `T014` (`predictions_service.py`), `T015` (routers, ya sobre el esqueleto del Sprint 3), `T016` (worker Celery `generate_predictions.py`) — los tres desbloqueados ahora que Leandro entrega el ensamble |
| **Leandro** | `T012` (`backend/ml/ensemble/predict.py`, grid search de `w`), `T013` (`backend/ml/evaluation/calibration.py`), `T025` (registro en MLflow). Si sobra tiempo en el sprint: arranque de `003` Grupo 1 (`T001`, `T002`, `T002b`, `T003`) |
| **Einar** | `002` Grupo 3 completo: `T013`-`T018` (prompts versionados, cliente Bedrock, caché en Redis, `explanations_service.py`, routers, workers de ingesta/reindexado) |
| **Carol** | Verifica la vista de lista (`T013`-`T016`, construida en el Sprint 3 contra datos de ejemplo) contra el backend real de `001` — no es una tarea nueva, es apuntar `frontend/lib/api/config.ts` a la API real y confirmar que TanStack Query trae los mismos datos sin cambiar código. Grupo 4: `T017`-`T019` (las 4 señales y el badge en la ficha del partido — no depende de que `002` esté lista) |
| **Octavio** | Prepara el Sprint Review: primera demo end-to-end de `001` (partido → predicción real en pantalla) |

## Puede adelantarse sin esperar

Einar no depende de nada de este sprint que no tuviera ya desde el Sprint 3. Carol puede avanzar
`T017`-`T019` sin esperar a que `002` exista — el bloque de explicación (`T020`) sí espera.

## Riesgos y dependencias

- `T014` depende de `T012`/`T013` de Leandro. Si Leandro entra al sprint con eso aún en curso
  (arrastrado del Sprint 3), Rodrigo empieza la semana en pairing/soporte en vez de en `T014` —
  mejor eso que bloquearse esperando.
- El bloque de explicación de la ficha (`T020` de `004`, Sprint 5) necesita que `002` tenga al
  menos el servicio y los routers (`T016`/`T017`) — este sprint es cuando Einar los construye.

## Definition of Sprint Done

- `GET /api/matches/{id}/prediction` devuelve las 4 señales y un `confidence` calculado, no
  hardcodeado, para un partido con datos suficientes.
- Los pesos del ensamble están registrados en MLflow con la convención de `ml-design.md` §7.
- `backend/rag/generation/client.py` genera una explicación real vía Bedrock para un partido de
  prueba.
- La ficha del partido en `004` muestra las 4 señales reales, sin explicación todavía.
