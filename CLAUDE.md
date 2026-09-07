# The Playbook — Guía para agentes

Sistema que **predice** resultados de fútbol (1X2, O/U 2.5, BTTS, xG), **explica** cada
predicción en lenguaje natural con evidencia verificable, y **publica** su propio track
record para que cualquiera lo audite. Proyecto académico del equipo The-Playbook (Taller de
Sistemas Inteligentes).

Los **3 pilares de valor** — todo feature debe trazarse a uno:

1. Predicción de resultados y mercados clave.
2. Explicación en lenguaje natural con evidencia verificable y temporalmente honesta.
3. Medición y transparencia del desempeño real del modelo.

---

## 1. Fuentes de verdad y precedencia

Léelo antes de escribir nada. Si dos documentos se contradicen, **gana el de arriba**.

| # | Fuente | Qué manda | Regla |
|---|---|---|---|
| 1 | `memory/constitution.md` | Los 9 artículos no negociables | Es ley. Si algo la contradice, la contradicción es el bug |
| 2 | `specs/00X-*/` | **CANÓNICO** para `spec`, `plan`, `data-model`, `contracts`, `quickstart`, `tasks` | Aquí se marcan los `[x]` |
| 3 | `docs/project_spec.md` | Decisiones de producto y stack | Cambiarlo exige fila en §12 + ADR si es arquitectónico |
| 4 | `docs/adr/` | Decisiones que se apartan de lo anterior | Un ADR aceptado no se edita: se supersede |
| 5 | `openspec/changes/00X/` | **Solo** `proposal.md` y `design.md` | Su `tasks.md` es un stub. **No lo edites** |

**spec-kit es canónico. OpenSpec es la capa de propuesta.** Hasta la auditoría SDD los
`tasks.md` estaban duplicados byte a byte entre ambos árboles; ahora hay uno solo y el
hook `.claude/hooks/sot-guard.mjs` bloquea las escrituras al stub.

### Los cuatro features del MVP

| ID | Capability | Depende de |
|---|---|---|
| `001-prediccion-partido` | 1X2, O/U 2.5, BTTS, xG, badge de confianza calibrado | — |
| `002-explicacion-lenguaje-natural` | Explicación RAG + SHAP, preguntas de seguimiento | `001` (`Predicción.top_shap_features`) |
| `003-track-record-publico` | Panel de desempeño de los 3 mercados vs. baseline de mercado | `001` (`version_modelo`, `resultado_real`) |
| `004-interfaz-web` | Las tres vistas: lista, ficha de partido y panel público | `001` (bloqueante); `002` y `003` son degradables |

Ninguno está implementado. `openspec/specs/` está vacío por eso, no por error.

**El primer trabajo es el Grupo 0 de `001/tasks.md`** (tareas `B01`-`B09`): sin app FastAPI,
docker-compose, Alembic ni fixtures, la primera prueba de contrato no se puede escribir.

---

## 2. Rutas canónicas

Definidas en `docs/project_spec.md` §10. **No inventes rutas alternativas.**

| Ruta | Contenido | Regla dura |
|---|---|---|
| `backend/app/api/` | Routers FastAPI por dominio | **Delgados.** Cero lógica de negocio |
| `backend/app/services/` | Lógica de negocio; orquesta `backend/ml/` y `backend/rag/` | Único puente entre el API y el ML |
| `backend/app/models/` | Modelos SQLAlchemy | — |
| `backend/app/schemas/` | Schemas Pydantic (contratos in/out) | Sin DTOs paralelos (Art. VIII) |
| `backend/app/core/` | Config, settings, credenciales IAM/Bedrock | — |
| `backend/app/db/` | Sesión async | — |
| `backend/ml/models/{dixon_coles,xgboost}/` | Modelos base | Cada uno expone `train.py`, `predict.py`, `evaluate.py` (Art. II) |
| `backend/ml/ensemble/` | Capa de combinación | Hermana de `models/`, **no hija**. Expone solo `predict.py` |
| `backend/ml/{data,features,evaluation}/` | Loaders, feature engineering, backtesting | — |
| `backend/rag/{ingestion,retrieval,generation}/` | Pipeline RAG | — |
| `backend/workers/` | Tareas Celery | Todo lo pesado vive aquí |
| `backend/tests/{contract,integration,unit}/` | Pruebas | — |
| `backend/alembic/` | Migraciones | — |
| `frontend/{app,components,lib}/` | Next.js 15 App Router | — |
| `infra/` | docker-compose, Dockerfiles, CI | — |

`backend/ml/` y `backend/rag/` **no importan nada de** `backend/app/api/`. Se comunican
con el backend únicamente vía `backend/app/services/` (Art. I).

---

## 3. Protocolo test-first (Artículo III, no negociable)

No se escribe código de implementación antes de:

1. Escribir la prueba.
2. Que el usuario la valide.
3. **Confirmar que falla** (fase Red).

En la práctica, en este repo:

- Ningún `Write` en `backend/app/`, `backend/ml/` o `backend/rag/` antes de que exista su
  test correspondiente y lo hayas visto fallar.
- El orden por feature está fijado en la sección *"Orden de creación de archivos"* de cada
  `plan.md`: contratos → pruebas de contrato → confirmar Red → modelos → schemas → ML →
  services → workers → routers.
- Pruebas de contrato **obligatorias** antes de implementar cualquier endpoint (Art. IX).
- Preferir Postgres/Redis/pgvector reales sobre mocks, vía docker-compose (Art. IX).

---

## 4. Los 9 artículos en 9 líneas

Detalle completo en `memory/constitution.md`. Cada uno con su guardián:

| Art. | Regla | Guardián |
|---|---|---|
| I | Library-First: `backend/ml/`, `backend/rag/`, `backend/app/services/` aislados; nada importa de `backend/app/api/` | Revisión de imports |
| II | Cada `backend/ml/models/*/` expone `train/predict/evaluate` | Pruebas de contrato ML |
| III | **Test-First**: Red antes de Green, sin excepciones | Revisión de PR |
| IV | **Integridad temporal**: split cronológico + `fecha_noticia < kickoff` en toda query RAG | `backend/ml/evaluation/test_split_cronologico.py` y test de integración pgvector |
| V | **Independencia del mercado**: las cuotas son baseline interno, jamás feature ni producto | `backend/ml/features/test_no_odds_en_feature_set.py` |
| VI | **Aislamiento**: nada pesado en el proceso API; contenido scrapeado = dato no confiable | Revisión + delimitación XML en prompts |
| VII | **Simplicidad**: ≤3 módulos, prohibido el future-proofing | Gate de Fase −1 en cada `plan.md` |
| VIII | **Anti-abstracción**: usar el framework directo, una sola representación de datos | Gate de Fase −1 |
| IX | **Integration-first**: servicios reales sobre mocks; contratos antes de implementar | Gate de Fase −1 |

---

## 5. Prohibiciones duras

Violarlas rompe el proyecto o su defensa académica. En orden de gravedad:

1. **Nunca** `train_test_split` sin orden temporal. El diferencial ético del proyecto es
   que ninguna parte usa información no disponible al momento real de la predicción.
2. **Nunca** una query de retrieval sin `WHERE fecha_publicacion_noticia < fecha_kickoff`.
   A nivel SQL, no como post-filtro en memoria.
3. **Nunca** una columna derivada de cuotas en el feature set de entrenamiento. Las cuotas
   solo calculan el baseline interno de log-loss.
4. **Nunca** exponer un comparador de casas de apuestas como funcionalidad al usuario.
5. **Nunca** un job de entrenamiento o reindexado en el proceso que atiende HTTP. Todo por
   Celery, incluso en local.
6. **Nunca** lógica de negocio en un router de `backend/app/api/`.
7. **Nunca** insertar contenido scrapeado en un prompt sin bloque delimitado explícito +
   instrucción de sistema que lo ignore como comando.
8. **Nunca** derivar el badge de confianza de la distancia a un reparto uniforme. Solo de
   calibración empírica. Ver [ADR 0001](docs/adr/0001-badge-confianza-calibrado.md).
9. **Nunca** editar `openspec/changes/*/tasks.md`. Es un stub.

---

## 6. Convenciones de documentación

- Todo requisito funcional es `RF-00X` y usa **sintaxis EARS**. Los cinco patrones:
  *ubiquitous* (`El sistema DEBE…`), *event-driven* (`CUANDO <disparador>, el sistema
  DEBE…`), *state-driven* (`MIENTRAS <estado>, …`), *unwanted behaviour* (`SI <condición>,
  ENTONCES el sistema DEBE…`) y *optional* (`DONDE <feature presente>, …`).
- **Toda tarea de `tasks.md` cita el RF que cubre**: sufijo `— [RF-00X]`. Las de proceso o
  infraestructura citan el artículo: `— [Art. III]`. Los IDs son `TXXX` por feature, y `BXX`
  para el Grupo 0 de arranque.
- **Todo `### Requirement:` de un delta de OpenSpec declara qué RF canónicos cubre**, con
  `<!-- rf: RF-00X, RF-00Y -->` bajo el encabezado. El validador comprueba que existan y que
  ningún RF quede sin cubrir.
- `spec.md` describe **qué** y **por qué**, nunca **cómo**. Nada de stack, endpoints ni
  esquemas: eso vive en `plan.md`, `data-model.md` y `contracts/`.
- Las referencias a `docs/project_spec.md` se escriben como `sección N.M` y deben resolver
  a un heading real. El validador las comprueba.
- Idioma: **español** en toda la documentación; identificadores de código en inglés.

---

## 7. Comandos

```bash
npm run audit:sdd                              # valida el grafo de referencias y la trazabilidad RF↔tarea
cd backend && pytest -q                        # pruebas (deben estar en ROJO hasta implementar)
cd backend && ruff check --fix . && ruff format .
cd frontend && npm run lint && npm run dev
docker compose -f infra/docker-compose.yml up  # Postgres + Redis + pgvector
```

`npm run audit:sdd` corre también como hook tras cada edición de `.md` y en CI. Si falla,
arregla la referencia — no la silencies.

---

## 8. Estado actual

**No hay código de implementación.** El repositorio es documentación SDD, el andamiaje de
carpetas, y los dos guardianes constitucionales.

`cd backend && pytest` está **en rojo a propósito**: los contratos de comportamiento de
`ml.evaluation.split` y `ml.features.build` fallan porque esos módulos aún no existen. Es
la fase Red del Artículo III y no debe "arreglarse" borrando o saltando los tests — se
arregla implementándolos. CI usa `-m "not pendiente_implementacion"` para gatear sobre los
guardianes estáticos, que sí están en verde.

El siguiente paso real es `specs/001-prediccion-partido/tasks.md` T001-T005: escribir las
cuatro pruebas de contrato y **verlas fallar**.

Antes de proponer una implementación, lee en este orden:
`memory/constitution.md` → `specs/00X/spec.md` → `specs/00X/plan.md` → `specs/00X/tasks.md`.
