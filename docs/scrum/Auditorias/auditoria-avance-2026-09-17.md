# Auditoría de avance real — 2026-09-17 (actualizada, 2ª pasada)

Auditoría puntual (no reemplaza a ClickUp como fuente de "hecho/en progreso", `docs/scrum/README.md`
§*Regla de fuente única*) hecha ejecutando el stack real: `docker compose up`, `alembic upgrade
head`, `pytest -q -v`, `ruff`, `mypy`, `npm run test/lint/typecheck`, `npm run audit:sdd` y
verificación de las rutas del frontend. Cruza lo que cada persona cree haber avanzado contra
`docs/scrum/sprint-0X.md`, `specs/00X-*/tasks.md` y el resultado real de esos comandos.

**Claims verificados en esta versión** (corregidos por el usuario tras la primera pasada):
Rodrigo, Leandro y Einar dicen haber llegado hasta el **sprint 3**; Carol dice haber completado
**los 8 sprints**.

> **⚠️ Esta es la 2ª ejecución del día.** Entre la primera pasada (mañana) y esta (tarde, tras
> `git fetch`) se mergearon a `develop` los PR #18, #19 y #20: Dixon-Coles y XGBoost (`T012d`,
> `T012e`), el ensamble (`T012`), la calibración (`T013`), MLflow tracking (`T025`), y los
> modelos/migración de `003` (`T004-T008`). **El hallazgo central de la primera pasada — "Dixon-
> Coles/XGBoost no existen" — ya no es cierto.** Esta versión refleja el código y los resultados
> de ejecución actuales de `develop` (commit `786fd3d`). Lo que sigue igual: el frontend no tuvo
> cambios nuevos, así que su sección no se volvió a ejecutar (solo se confirmó que no hay commits
> nuevos en `frontend/`).

## 1. Resumen ejecutivo

| Spec | Semáforo | Bloqueante actual |
|---|---|---|
| `001-prediccion-partido` | 🟡 ML completo (Dixon-Coles, XGBoost, ensamble, calibración, MLflow), cero API de negocio | **Rodrigo** — `T014` (servicio), `T015` (router), `T016` (worker Celery) sin una línea de código |
| `002-explicacion-lenguaje-natural` | 🟡 Ingestion+retrieval reales, generación ausente | **Einar** (`generation/`: sin cliente Bedrock, caché ni prompts) |
| `003-track-record-publico` | 🟡 Contratos + modelos/migración reales, cero servicio/router | **Leandro** — Grupo 2 (`T004-T008`) ya cerrado, pero Grupo 3 en adelante (`T009-T022`: servicio, router, worker) sin código |
| `004-interfaz-web` | 🟢 UI completa y testeada, pero **no integrable** | Bloqueada externamente por `001`/`002`/`003` — Carol no tiene qué arreglar de su lado |

**El cuello de botella se movió.** En la primera pasada (mañana), Dixon-Coles/XGBoost eran el
bloqueante que frenaba todo lo demás. Tras los merges de la tarde, ese ML ya existe y pasa sus
pruebas (ver sección Leandro) — **el nuevo cuello de botella es la capa de servicios/routers**
(`backend/app/services/`, `backend/app/api/`, `backend/workers/tasks/`), que sigue **completamente
vacía** en las tres specs de backend. Ningún endpoint de negocio existe hoy fuera de `/health`,
pero ya no es porque falte el modelo — es porque nadie escribió todavía el pegamento entre el
modelo/los datos y una respuesta HTTP.

**Con el claim corregido, el hallazgo de la primera pasada se invierte**: en la mañana, "Leandro
hasta sprint 3" contradecía la evidencia (Dixon-Coles/XGBoost no existían). En la tarde, con el
código ya mergeado, **el claim de Leandro queda confirmado por ejecución real** — ver el detalle
abajo. El resto de claims (Rodrigo y Einar hasta sprint 3, Carol los 8) sigue siendo consistente
con lo que muestra la ejecución.

## 2. Por persona: claim vs. evidencia vs. ejecución

### Rodrigo (`Rdrgrvram`) — Backend-core, `001` capa de aplicación
**Claim:** "hasta el sprint 3".

- Sprint 1 (Grupo 0, `B01-B09`) y Sprint 2 (Grupo 1-2, `T001-T011`): **completos, marcados `[x]`,
  y confirmados por ejecución** — `alembic upgrade head` corrió las 4 migraciones en una sola
  cadena (el fix de los 2 heads de Alembic quedó bien resuelto), y los modelos/schemas que creó
  pasan sus pruebas.
- Sprint 3 no le asigna tareas nuevas de `tasks.md` (`docs/scrum/sprint-03.md`: *"Rodrigo: sin
  tareas nuevas — deja T015 en borrador, revisa a Leandro"*) — su claim de "sprint 3" es
  consistente solo si se refiere a haber llegado *al* sprint 3 sin quedar atrás, no a tareas
  nuevas completadas en él.
- **Sprint 4 (`T014` servicio, `T015` router, `T016` worker Celery) sigue sin una sola línea de
  código**, confirmado en esta 2ª pasada — `backend/app/services/`, `backend/app/api/` y
  `backend/workers/tasks/` siguen vacíos. Los 4 tests de contrato de `matches`/`prediction`
  siguen fallando con 404 (Rojo correcto del Art. III mientras no exista el router). **Esto ya
  no tiene excusa de dependencia**: el ensamble de Leandro (`backend/ml/ensemble/predict.py`)
  y sus modelos (`backend/ml/models/{dixon_coles,xgboost}/`) están completos y probados desde
  esta tarde — Rodrigo tiene ahora todo lo que necesitaba para escribir `T014-T016`. Es, con
  esta actualización, **el nuevo bloqueante #1 del proyecto**.

### Leandro (`leandrobaldur`) — ML del modelo + `003` completo
**Claim (corregido):** "hasta el sprint 3", igual que Rodrigo y Einar.

> **Actualización de la tarde**: en la 1ª pasada (mañana) el claim "hasta sprint 3" contradecía
> la evidencia porque `T012d`/`T012e` no existían. Entre esa pasada y esta, se mergearon a
> `develop` los PR #18 (`T012d`/`T012e`) y #19 (`T012` ensamble, `T013` calibración, `T025`
> MLflow) y #20 (`003` `T004-T008`). Re-ejecuté `pytest`/`mypy`/`ruff` contra el `develop` actual
> (commit `786fd3d`) — esta sección refleja ese resultado, no el de la mañana.

- Sprint 3 (`docs/scrum/sprint-03.md`) le asigna a Leandro exactamente `T012c` (features),
  `T012d` (Dixon-Coles), `T012e` (XGBoost) — **"el sprint de mayor riesgo del proyecto"**.
  **Las tres están cerradas y confirmadas por ejecución real**: `backend/ml/models/dixon_coles/`
  (`train.py`/`predict.py`/`evaluate.py`, 26 tests, todos en verde),
  `backend/ml/models/xgboost/` (ídem, 11 tests en verde). También cerró de más, adelantando
  Sprint 4 (`T012` ensamble — `backend/ml/ensemble/predict.py`, 8 tests; `T013` calibración —
  `backend/ml/evaluation/calibration.py`, 15 tests; `T025` MLflow tracking —
  `backend/ml/evaluation/mlflow_tracking.py`, 8 tests) y Sprint 5 de `003` (Grupo 2 completo,
  `T004-T008`: modelos `EvaluaciónPredicción`/`TrackRecordAgregado`/`CuotaMercado` + migración
  `2e87cd87231a`, aplicada limpia con `alembic upgrade head`). **136 tests recolectados en total
  en el árbol `backend/ml/`+`backend/tests/`, 124 pasan** (los 12 que fallan son, otra vez, los contratos de
  routers que no existen — Rojo correcto, no un problema de Leandro).
- **Veredicto sobre el claim corregido**: con el código de esta tarde, **"hasta sprint 3" queda
  confirmado por ejecución real** — de hecho es conservador, porque también cerró piezas de los
  sprints 4 y 5. Esto invierte el hallazgo de la mañana: Leandro deja de ser el bloqueante #1 del
  proyecto (ver Resumen ejecutivo) — el cuello de botella pasa a Rodrigo (`T014-T016`) y al propio
  Leandro en `003` Grupo 3+ (servicio/router, ver tabla).
- **Gap real que sigue sin resolver, y que la rúbrica de la próxima defensa exige como
  evidencia**: el pipeline de ML **nunca se corrió contra los datos reales**. Verifiqué la
  carpeta `mlruns/` que generó la propia suite de tests — solo contiene artefactos sintéticos de
  las pruebas unitarias (`calibracion.json` con datos de prueba), no un experimento real de
  Dixon-Coles/XGBoost/ensamble entrenado sobre Football-Data.co.uk con un log-loss/Brier score
  real registrado. El código para hacerlo ya existe; falta ejecutarlo una vez de punta a punta
  y guardar el resultado (ver `docs/scrum/Auditorias/guia-defensa-ec1.md`, bloque 6).
- **Hallazgo de calidad, ahora más extendido**: `mypy` encontró **50 errores reales** (subió de
  10 a 50 porque hay mucho más código nuevo de Leandro para analizar), casi todos del mismo
  patrón que ya se había visto en `backend/ml/features/build.py:77`: comparar/operar sobre
  columnas tipadas `int | None` sin verificar `None` antes. Ahora aparece también en
  `backend/ml/models/dixon_coles/evaluate.py:37,65,70` y `backend/ml/models/dixon_coles/train.py:93`
  — es un patrón repetido, no un error puntual, y vale la pena que Leandro revise sus módulos con
  ese criterio antes de la defensa. El resto son mayormente `import-untyped` (faltan
  `pandas-stubs`, cosmético) y typing de `dict` opcional en `backend/ml/models/xgboost/train.py`.

### Einar (`pupi1000`) — RAG/LLM, `002` completo
**Claim:** "hasta el sprint 3".

- Coincide bien con la evidencia: ingestion (`T010` chunking, `T011` sanitización anti-prompt-
  injection) y retrieval (`T012`, con el filtro temporal `fecha_publicacion < fecha_kickoff`
  aplicado a nivel SQL, verificado con `tests/integration/test_temporal_filter.py` contra
  pgvector real) están completos y pasan. Los modelos/schemas/migración de `002` (Grupo 2)
  también existen y corren.
- **Sprint 4 (`generation/` — `T013-T018`) está vacío**: no hay cliente Bedrock, caché en Redis
  ni prompts versionados. Es exactamente donde su claim se detiene.
- `specs/002-*/tasks.md` sigue **100% sin marcar `[x]`** pese a que buena parte del trabajo ya
  está hecho y probado — desincronización de proceso, no de código.
- **Hallazgo de calidad**: `tests/contract/test_explanations_api.py` (suyo) hace
  `assert response.status_code == 404` contra una ruta que **no existe todavía**. Como FastAPI
  devuelve 404 genérico para cualquier ruta no registrada, este test **pasa igual cuando el
  router no existe que cuando existiera y funcionara bien** — nunca puede confirmar una fase Roja
  real ni detectar una implementación rota. Vale la pena reescribirlo contra un `match_id` real
  sin explicación generada (no un UUID al azar) para que sí distinga "ruta no existe" de
  "partido sin explicación".

### Carol (`CaroZeballos`) — Frontend, `004` completo
**Claim:** "en teoría los 8 sprints".

- Todo `frontend/app/`, `components/`, `lib/` y 20 archivos de test llegaron en **un solo commit**
  (PR #16, 2026-09-16), no incremental sprint a sprint — así que "en teoría" es la palabra clave
  correcta: el volumen de código cubre las 3 vistas (lista, ficha de partido, panel de track
  record) y en apariencia las 34 tareas de `004`, pero no hay forma de verificar que se construyó
  siguiendo el orden de sprints porque no hay commits intermedios.
- **Confirmado por ejecución** (no solo lectura): `npm run test` → **55 tests pasando en 21
  archivos**; `npm run lint` y `npm run typecheck` sin ningún error; las 3 rutas
  (`/`, `/partidos/{id}`, `/track-record`) responden `200` en `NEXT_PUBLIC_DEMO_MODE=true`. Mi
  hipótesis inicial de que Vitest fallaría por el alias `@/` sin `vite-tsconfig-paths` **era
  incorrecta** — Vitest 5 lo resuelve nativo, sin necesidad de ese plugin.
- **Limitación de esta auditoría**: no hay navegador headless disponible en este entorno para
  confirmar visualmente que los datos de `demo-data.ts` se pintan correctamente tras la
  hidratación del cliente (el HTML servido por SSR solo trae el esqueleto de carga; los datos se
  resuelven después, en el navegador, vía TanStack Query). La cobertura real de esa lógica de
  render viene de los 55 tests de Vitest, que sí montan los componentes con datos mockeados y
  aseveran el contenido — es evidencia sólida pero no reemplaza un vistazo real en Chrome.
- **El verdadero problema de Carol no es su código, es que no tiene contra qué integrar**: sin
  routers reales de `001`/`002`/`003`, el frontend solo puede probarse en `DEMO_MODE`. Nadie ha
  confirmado nunca que `useLeagues`, `useMatch`, `usePrediction`, etc. funcionen contra una API
  real — ese es un gap que persiste sea cual sea el estado de Carol.

## 3. Tabla de tareas por spec — checkbox / código / test

| Spec | Grupo | Checkbox `tasks.md` | Código existe | Test pasa (ejecutado) |
|---|---|---|---|---|
| 001 | Grupo 0 (`B01-B09`) | ✅ | ✅ | ✅ |
| 001 | Grupo 1-2 (`T001-T011`) | ✅ | ✅ | ✅ |
| 001 | `T012a-T012e`, `T012`(ensamble), `T013`(calibración), `T025`(MLflow) | ✅ | ✅ **(actualizado)** | ✅ (45 tests entre dixon_coles/xgboost/ensemble/calibration/mlflow_tracking) |
| 001 | `T014-T016` (servicio/router/worker) | ⬜ | ❌ | ❌ (404, Rojo esperado — **nuevo bloqueante #1**) |
| 001 | Grupo 5 (`T017-T024`) | ⬜ | ❌ | — |
| 002 | Todo (`T001-T025`) | ⬜ (**0% pese a código real**) | ✅ hasta `T012` (ingestion+retrieval), ❌ desde `T013` (generation) | ✅ ingestion/retrieval; `T013+` sin test posible (no hay código) |
| 003 | Grupo 1 (`T001-T003`) | ✅ | ✅ | ✅ |
| 003 | Grupo 2 (`T004-T008`, modelos+migración) | ✅ | ✅ **(actualizado)** | ✅ (migración `2e87cd87231a` aplicada limpia) |
| 003 | Grupo 3-5 (`T009-T022`, servicio/router/worker) | ⬜ | ❌ | ❌ (no aplica, no hay router) |
| 004 | Todo (`T001-T034`) | ⬜ (**0% pese a código completo**) | ✅ | ✅ (55/55 Vitest, lint, typecheck — sin cambios desde la 1ª pasada) |

## 4. Hallazgos de proceso (no atribuibles a una sola persona)

1. **Markers de fase Roja obsoletos**: `pytest -m pendiente_implementacion` confirma que los 3
   tests marcados así (2 en `backend/ml/evaluation/test_split_cronologico.py`, 1 en
   `backend/ml/features/test_no_odds_en_feature_set.py`) **pasan** — la función que debían esperar ya
   está implementada. Como CI corre con `-m 'not pendiente_implementacion'`, estos 3 tests
   **hoy no se ejecutan en CI en absoluto**, pese a que podrían correr en verde. Se recomienda
   quitarles el marker.
2. **`CLAUDE.md` §8 desactualizado**: dice que solo 2 tests están "en rojo a propósito" (split y
   features build) — ambos ya están implementados. El gap real es mucho mayor: `T012d/e` y
   `T012-T016` de `001`, `generation` completo de `002`, casi todo `003`. Conviene actualizar esa
   sección antes de que alguien la use como fuente de "próximo paso".
3. **Tests de contrato tautológicos**: al menos `test_explanations_api.py` (ver sección Einar)
   no puede distinguir "ruta no implementada" de "implementación correcta" porque ambas dan 404.
   Vale la pena revisar si `test_track_record_api.py`/`test_matches_upcoming.py` tienen el mismo
   problema en algún caso límite (no lo tienen: comprueban forma de payload, no solo status code).
4. **CI no corre `npm run test`** — el job `frontend` de `.github/workflows/ci.yml` solo hace
   `lint`+`typecheck`. Los 55 tests de Vitest de Carol nunca se ejecutaron automáticamente hasta
   esta auditoría.
4b. **Brecha entre autopercepción de sprint y código verificable (Leandro)**: el claim
   "hasta sprint 3" asume completo justo el contenido que `sprint-03.md` define como el más
   riesgoso (Dixon-Coles + XGBoost), y el código muestra lo contrario. Como el check-in de
   avance es async (`docs/scrum/README.md` — 3 franjas de 2h/semana, sin daily), es fácil que
   "avancé en el sprint" se lea como "toqué las tareas del sprint" en vez de "las cerré". Vale
   la pena que el Sprint Review use un criterio binario por tarea (código + test en verde) en
   vez de autopercepción, justo para esta clase de caso.
5. **Flujo de ramas apartado de `docs/team-charter.md` §3**: `qa` sigue congelada en el commit
   inicial (2026-08-16, nunca recibió nada de `develop` — 55 commits detrás); `main` está 41
   commits detrás de `develop` (última fusión: PR #3, 2026-09-15). El flujo documentado
   (`feature/* → develop → qa → main`) no se está siguiendo en la práctica.
6. **Contenedores Docker huérfanos**: al levantar `infra/docker-compose.yml` aparecieron
   contenedores de un compose anterior con más servicios (`infra-api-1`, `infra-frontend-1`,
   `infra-pgbouncer-1`, `infra-sin-mock-1`, `infra-minio-1`, de hace ~2 meses). No se tocaron;
   si ya no corresponden a la arquitectura actual (Art. VII, simplicidad), alguien debería
   limpiarlos con `docker compose down --remove-orphans` conscientemente.
7. **Gap de configuración en `mypy`**: el override `[[tool.mypy.overrides]] module =
   ["tests.*"]` (pensado para relajar tipado en tests) no cubre los tests bajo `backend/ml/`
   (`backend/ml/data/test_*.py`, `backend/ml/features/test_*.py`), porque su módulo no matchea el patrón
   `tests.*`. Son varios de los 50 errores de mypy reportados en la sección de Leandro.
8. **`mlruns/` solo tiene evidencia sintética, no un experimento real** (hallazgo de esta 2ª
   pasada): la carpeta que generan los propios tests unitarios de `mlflow_tracking.py` no debe
   confundirse con evidencia de línea base para la defensa — es un artefacto de prueba, se borró
   después de esta auditoría (`rm -rf mlruns`). Antes de la defensa hace falta correr el pipeline
   completo contra datos reales y guardar ese run — ver
   `docs/scrum/Auditorias/guia-defensa-ec1.md`, bloque 6.

## 5. Recomendaciones priorizadas (actualizadas tras la 2ª pasada)

1. **Rodrigo implementa `T014-T016` (servicio/router/worker) ya mismo** — es el nuevo
   bloqueante #1: todo lo que necesitaba (ensamble + modelos ML) ya existe y está probado.
2. **Leandro sigue con `003` Grupo 3+ (`T009-T022`: servicio/router/worker de track-record)** —
   los modelos y la migración (Grupo 2) ya están listos, falta el mismo tipo de capa que le
   falta a Rodrigo en `001`.
3. **Correr el pipeline de ML de punta a punta contra datos reales y guardar el resultado en
   MLflow** — es el gap más visible de cara a la próxima defensa (rúbrica EC1, "Línea Base y
   Evidencia"), y ya no hay ningún bloqueante técnico para hacerlo.
4. **Einar arranca `generation/` (`T013-T018`)** en paralelo — no depende de Rodrigo/Leandro.
5. Revisar el patrón repetido de `mypy` (Optional sin verificar) en `backend/ml/features/build.py`
   y ahora también en `backend/ml/models/dixon_coles/{evaluate,train}.py` — mismo tipo de fix en
   los tres archivos.
6. Corregir el test tautológico de `test_explanations_api.py` para que use un `match_id`
   sembrado sin explicación (no un UUID al azar), y quitar el marker `pendiente_implementacion`
   de los 3 tests que ya pasan.
7. Actualizar `specs/001-*/tasks.md` (ya marcado para T012d/e/T012/T013/T025, verificar que
   `specs/003-*/tasks.md` T004-T008 también esté marcado) y `specs/002-*/tasks.md`/
   `specs/004-*/tasks.md` (siguen sin marcar pese al código real).
8. Agregar `npm run test` al job `frontend` de CI, y revisar/actualizar `CLAUDE.md` §8 (sigue
   describiendo un estado de hace dos ciclos de merges).
