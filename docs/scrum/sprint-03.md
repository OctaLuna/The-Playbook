# Sprint 3 — Núcleo matemático y de retrieval

**Semanas:** 5-6 · **Objetivo:** Dixon-Coles y XGBoost entrenan sobre datos reales; el
retrieval de `002` respeta el filtro temporal; el frontend tiene su capa de datos lista.

## Por persona

| Persona | Tareas |
|---|---|
| **Rodrigo** | Sin tareas nuevas de `tasks.md` este sprint — el resto de `001` (`T014`-`T016`) depende de que Leandro entregue `T012`/`T013`, que no llegan hasta el Sprint 4. Usa el sprint para dejar `T015` (routers) en borrador/esqueleto y para revisar el trabajo de Leandro como segundo par de ojos en `T012c`-`T012e` |
| **Leandro** | El sprint más denso del proyecto: `T012c` (`backend/ml/features/`), `T012d` (Dixon-Coles: train/predict/evaluate), `T012e` (XGBoost: train/predict/evaluate) |
| **Einar** | Cierra Grupo 2 si quedó pendiente (`T005`-`T009`). `T012`: `backend/rag/retrieval/query.py` — debe hacer pasar `T001` (el test crítico del filtro temporal) |
| **Carol** | `004` Grupo 2: `T010`-`T012` (cliente HTTP tipado, hooks de TanStack Query, componentes de carga/error/vacío). Grupo 3: `T013`-`T016` (vista de lista) — contra las respuestas de ejemplo de los contratos, ya que `001` real todavía no expone datos |
| **Octavio** | Chequeo de riesgo a mitad de sprint sobre `T012d`/`T012e` — es el camino más largo y matemáticamente denso del proyecto. Si Leandro reporta bloqueo, es el momento de decidir si Rodrigo se suma a pairing en vez de seguir en borrador de `T015` |

## Puede adelantarse sin esperar

Carol construye toda su Grupo 3 contra datos de ejemplo — no necesita que `001` sirva datos
reales todavía. Einar no depende de nadie más para `T012`.

## Riesgos y dependencias

- **Este es el sprint de mayor riesgo del proyecto.** `T012d`/`T012e` son los únicos dos tickets
  que exigen entender e implementar una fórmula matemática completa (Dixon-Coles) más un modelo
  de gradient boosting con selección de hiperparámetros. Si Leandro no los termina en las 2
  semanas, **no es una señal de alarma por sí sola** — es exactamente el tipo de tarea que
  `ml-design.md` documentó con tanto detalle para que no haga falta decidir nada sobre la marcha,
  pero la implementación en sí sigue tomando tiempo real.
- Si `T012d`/`T012e` se atrasan, el Sprint 4 de Rodrigo se corre en cascada — avisar temprano
  (protocolo de bloqueo de `docs/team-charter.md` §4), no esperar al Sprint Review.

## Definition of Sprint Done

- `backend/ml/models/dixon_coles/predict.py` devuelve `λ`/`μ` para un partido de prueba.
- `backend/ml/models/xgboost/predict.py` devuelve probabilidades para el mismo partido.
- El test de integración del filtro temporal de `002` (`T001`) pasa contra pgvector real.
- La vista de lista de `004` renderiza con datos de ejemplo, con sus 3 estados (carga/error/vacío)
  verificables manualmente.
