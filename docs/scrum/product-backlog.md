# Product Backlog

**Fuente canónica de cada tarea:** `specs/00X-*/tasks.md`. Este archivo **no repite** la
descripción de ninguna tarea — solo las agrupa por persona con su ID, para tener una vista de
conjunto antes de entrar al detalle sprint a sprint. Si necesitas saber qué hace `T012d`, ábrelo
en `specs/001-prediccion-partido/tasks.md`, no aquí.

126 tareas totales. El reparto por persona y su porqué están en
[`equipo-y-tracks.md`](equipo-y-tracks.md).

## Rodrigo — Backend-core de `001` (31 tareas)

Fuente: [`specs/001-prediccion-partido/tasks.md`](../../specs/001-prediccion-partido/tasks.md)

| Grupo | IDs | Qué es |
|---|---|---|
| Grupo 0 — Arranque | `B01`-`B09` | Stack completo: dependencias, docker-compose, config, sesión de BD, fixtures, `/health`, Alembic |
| Grupo 1 — Contratos | `T001`-`T005` | Pruebas de contrato de los 4 endpoints, confirmadas en rojo |
| Grupo 2 — Modelo de datos | `T006`-`T011` | Modelos SQLAlchemy de `Partido`/`Equipo`/`Predicción`/`CalibraciónHistórica`, migración inicial, schemas Pydantic |
| Grupo 3 (parte) | `T014`, `T015`, `T016` | `predictions_service.py`, routers de `matches.py`, worker `generate_predictions.py` — depende de que Leandro entregue `T012`/`T013` |
| Grupo 4 — Integración | `T017`-`T022` | Pruebas de integración de las 4 historias y los casos límite |
| Grupo 5 — Pulido | `T023`, `T024` | 404 documentados, `quickstart.md` actualizado |

## Leandro — ML de `001` + `003` completo (33 tareas)

**ML de `001`** — fuente: [`specs/001-prediccion-partido/tasks.md`](../../specs/001-prediccion-partido/tasks.md)

| IDs | Qué es |
|---|---|
| `T012a` | Dependencias de ML en `pyproject.toml` |
| `T012b` | `backend/ml/data/` — carga de Football-Data.co.uk, alias de equipo |
| `T012c` | `backend/ml/features/` — feature set de XGBoost |
| `T012d` | `backend/ml/models/dixon_coles/` — train/predict/evaluate |
| `T012e` | `backend/ml/models/xgboost/` — train/predict/evaluate |
| `T012` | `backend/ml/ensemble/predict.py` — grid search del peso `w` |
| `T013` | `backend/ml/evaluation/calibration.py` — buckets y badge |
| `T025` | Registro en MLflow con la convención de `ml-design.md` §7 |

**`003-track-record-publico` completo** — fuente: [`specs/003-track-record-publico/tasks.md`](../../specs/003-track-record-publico/tasks.md)

| Grupo | IDs | Qué es |
|---|---|---|
| Grupo 1 — Contratos | `T001`, `T002`, `T002b`, `T003` | Pruebas de contrato de los 2 endpoints + la prueba negativa de no-exposición de cuotas |
| Grupo 2 — Modelo de datos | `T004`-`T008` | `EvaluaciónPredicción`, `TrackRecordAgregado`, `CuotaMercado`, migración, schemas |
| Grupo 3 — Implementación | `T009`-`T012` | Servicio (reutiliza `backend/ml/evaluation/`), baseline de mercado, worker diario, routers |
| Grupo 4 — Integración | `T013`-`T019` | Los tres mercados, reentrenamiento a mitad de ventana, guardián anti-odds |
| Grupo 5 — Pulido | `T020`-`T022` | Muestra insuficiente, `quickstart.md`, ADR de exclusión de partidos sin cuota |

## Einar — `002-explicacion-lenguaje-natural` completo (28 tareas)

Fuente: [`specs/002-explicacion-lenguaje-natural/tasks.md`](../../specs/002-explicacion-lenguaje-natural/tasks.md)

| Grupo | IDs | Qué es |
|---|---|---|
| Grupo 1 — Contratos | `T001`-`T004` | Filtro temporal (la prueba más crítica del feature), contratos de los 2 endpoints |
| Grupo 2 — Modelo de datos | `T004b`-`T009` | Dependencias RAG, `Explicación`, `Evidencia`, `ExplicacionEvidencia`, `PreguntaSeguimiento`, migración, schemas |
| Grupo 3 — Implementación | `T010`-`T018` | Chunking, sanitización, retrieval con filtro SQL, prompts, cliente Bedrock, caché, servicio, routers, workers de ingesta |
| Grupo 4 — Integración | `T019`-`T022` | Evidencia real, fallback honesto, preguntas de seguimiento, no-contradicción con la predicción numérica |
| Grupo 5 — Pulido | `T023`-`T025` | 404, `quickstart.md`, umbral de groundedness configurable |

## Carol — `004-interfaz-web` completo (34 tareas)

Fuente: [`specs/004-interfaz-web/tasks.md`](../../specs/004-interfaz-web/tasks.md)

| Grupo | IDs | Qué es |
|---|---|---|
| Grupo 0 — Andamiaje | `T001`-`T004` | Proyecto Next.js, lint/typecheck en CI, shadcn+TanStack, config |
| Grupo 1 — Tipos | `T005`-`T009` | Tipos derivados de los 3 contratos de backend, pruebas de parseo |
| Grupo 2 — Cliente y estado | `T010`-`T012` | Cliente HTTP tipado, hooks de TanStack Query, componentes de carga/error/vacío |
| Grupo 3 — Lista | `T013`-`T016` | Vista de partidos próximos, filtro por liga |
| Grupo 4 — Ficha | `T017`-`T023` | Las 4 señales, aviso de datos insuficientes, explicación con evidencia, preguntas de seguimiento |
| Grupo 5 — Track record | `T024`-`T028` | Panel de los 3 mercados, detalle partido a partido |
| Grupo 6 — Accesibilidad | `T029`-`T034` | Teclado, lectores de pantalla, contraste, responsive, verificación de que nada se calcula en el cliente |

## Octavio — Product Owner / Scrum Master

Sin tareas de `specs/` asignadas. Su trabajo por sprint está en cada `sprint-0X.md`: prioriza
qué entra, facilita Planning/Review/Retro, y resuelve los bloqueos que crucen tracks (protocolo
de `docs/team-charter.md` §4).
