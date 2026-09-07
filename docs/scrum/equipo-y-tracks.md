# Equipo y tracks técnicos

**Basado en:** `docs/team-charter.md` §1 (integrantes, roles iniciales, disponibilidad)
**Propósito de este archivo:** el charter dice quién es cada quien y cuándo está disponible;
este archivo dice **qué construye cada quien** durante los 8 sprints — el desglose técnico que
el charter no tenía porque se escribió antes de que existieran las 126 tareas de
`specs/00X-*/tasks.md`.

## Los 5 y su track

| Persona | Rol declarado (charter) | Track técnico | Feature(s) |
|---|---|---|---|
| **Octavio Luna** | Valor/Producto — líder de equipo | Product Owner / Scrum Master | Ninguna fija — coordina las 4 |
| **Rodrigo Rivera** | Proceso | Backend-core | `001` — capa de aplicación |
| **Leandro Colque** | Modelo/IA | ML del modelo | `001` — capa de ML, **+ `003` completo** |
| **Einar Guillen** | Datos | RAG/LLM | `002` completo |
| **Carol Zevallos** | Ingeniería | Frontend | `004` completo |

## Por qué este reparto

**Octavio sin track fijo.** Es el líder de equipo declarado en el charter; en Scrum eso es
Product Owner (prioriza el backlog, decide qué entra en cada sprint) y, dado el tamaño del
equipo, también Scrum Master (facilita ceremonias, destraba bloqueos entre tracks). Un PO/SM
con tareas técnicas fijas tiende a priorizar su propio código sobre destrabar a los demás —
mejor que su capacidad quede libre para eso.

**Rodrigo lleva el Backend-core.** Es el track más transversal: el Grupo 0 de `001/tasks.md`
(`B01`-`B09`) que arranca el stack vive aquí, y bloquea a los otros tres tracks hasta que esté
listo. Conviene que lo posea alguien cuyo rol ya es "Proceso" — no es un dato menor que quien
más impacto tiene en destrabar a los demás sea, precisamente, el rol orientado a eso.

**Leandro lleva ML + `003` completo, no solo ML.** `003-track-record-publico` reutiliza
`backend/ml/evaluation/` (log-loss, Brier) que Leandro mismo construye para `001` — la tarea T009
de `003/tasks.md` lo dice explícitamente: *"reutiliza `backend/ml/evaluation/` ya existente para
001 — no reimplementar las métricas"*. Si `003` fuera de otra persona, cada sprint dependería de
una coordinación cruzada que no hace falta si el mismo dueño de la evaluación es quien construye
el track record sobre ella.

**Einar lleva RAG/LLM.** El trabajo más temprano de `002` (`backend/rag/ingestion/`: chunking,
sanitización) es ingeniería de datos pura, aunque el track deriva hacia LLM en la capa de
generación (`backend/rag/generation/`, cliente Bedrock). Es el track que mejor conserva la
etiqueta "Datos" del charter sin forzarla.

**Carol lleva Frontend, con carga técnica reducida a propósito.** Pedido explícito del equipo:
Carol administra ClickUp para todo el grupo (tablero, asignación de tareas, evidencia — la
única fuente válida de "qué se hizo y quién lo hizo" según `docs/team-charter.md` §2), así que
necesita el track de menor riesgo técnico. Frontend lo es por tres razones concretas, no solo
por intuición:
1. **No bloquea a nadie.** Por el Artículo I (Library-First), `frontend/` no comparte ni un
   archivo con `backend/`. Nadie en los otros tres tracks espera a Carol para nada.
2. **Consume contratos ya congelados**, no los inventa. Los tres contratos de `specs/00X/contracts/`
   están fijados desde la ronda de auditoría anterior — Carol no depende de decisiones que
   todavía no se tomaron.
3. **Sin superficie constitucional crítica.** No toca el filtro temporal del Artículo IV, no
   toca cuotas de mercado (Artículo V), no entrena nada. El riesgo de romper una regla no
   negociable del proyecto es, en este track, el más bajo de los cuatro.

## Recuento de tareas (de las 126 totales)

| Persona | Tareas | Detalle |
|---|---|---|
| Rodrigo | 31 | Grupo 0 (9) + Grupo 1-2 de 001 (11) + T014-T016 (3) + Grupo 4-5 de 001 (8) |
| Leandro | 33 | T012a-T012e, T012, T013, T025 de 001 (8) + `003` completo (25) |
| Einar | 28 | `002` completo |
| Carol | 34 | `004` completo |

Quedó parejo en cantidad pese a repartirse por afinidad, no por balanceo forzado. La diferencia
real entre tracks no está en el número de tickets sino en su densidad: un `T012d` (Dixon-Coles)
es semanas de trabajo matemático; un `T032` de accesibilidad de `004` es una tarde. Eso es
intencional — es justamente lo que hace que el track de Carol sea "el más sencillo" sin que la
tabla de arriba lo muestre como más corto.

## Límites de archivo por persona

Consecuencia directa del Artículo I (Library-First): cada track vive en su propio árbol de
directorios y no necesita tocar el de otro para avanzar.

| Persona | Escribe en | Nunca escribe en |
|---|---|---|
| Rodrigo | `backend/app/{api,services,schemas,db,core}/`, `backend/app/models/{partido,equipo,prediccion,calibracion_historica}.py`, `backend/workers/tasks/generate_predictions.py`, `backend/alembic/`, `infra/`, `backend/tests/{contract,integration}/test_leagues.py`, `test_matches_*.py` | `backend/ml/`, `backend/rag/`, `frontend/` |
| Leandro | `backend/ml/`, `backend/app/models/{evaluacion_prediccion,track_record_agregado,cuota_mercado}.py`, `backend/app/services/track_record_service.py`, `backend/app/api/track_record.py`, `backend/workers/tasks/update_track_record.py` | `backend/app/api/matches.py`, `backend/rag/`, `frontend/` |
| Einar | `backend/rag/`, `backend/app/models/{explicacion,evidencia,pregunta_seguimiento,explicacion_evidencia}.py`, `backend/app/services/explanations_service.py`, `backend/app/api/explanations.py`, `backend/workers/tasks/{ingest_news,reindex_rag}.py` | `backend/ml/`, `backend/app/api/matches.py`, `frontend/` |
| Carol | `frontend/` completo | Cualquier cosa bajo `backend/` |

## Las 3 zonas de cruce (coordinar antes de tocar)

No hay archivos compartidos entre tracks salvo estos tres puntos, cada uno con su regla:

1. **`backend/pyproject.toml`.** Rodrigo lo crea en `B01` (Grupo 0). Leandro añade sus
   dependencias de ML en `T012a` y Einar las de RAG en `T004b` — **cada uno en su propio commit,
   después** de que `B01` esté fusionado a `develop`, nunca en paralelo con él. Es el único
   archivo que los tres tracks tocan.
2. **`backend/ml/evaluation/`.** Leandro lo construye para `001` y lo reutiliza él mismo en
   `003` (T009 de `003/tasks.md`) — no es una zona de cruce entre personas, es la razón por la
   que `003` es de Leandro y no de otra persona (ver arriba).
3. **`specs/001-prediccion-partido/data-model.md` y `contracts/matches-api.md`.** Son de
   lectura obligatoria para Leandro (define qué campos persiste `Predicción`) y para Rodrigo
   (define qué expone la API) al mismo tiempo. Ninguno de los dos los edita sin avisar al otro
   — cualquier cambio de contrato en mitad de un sprint es el tipo de bloqueo que
   `docs/team-charter.md` §4 pide reportar como Issue, no resolver en silencio.

## Cómo usar esto

Cada sprint (`docs/scrum/sprint-0X.md`) asigna IDs concretos de `specs/00X-*/tasks.md` dentro de
estos tracks. Este archivo no cambia sprint a sprint — solo si el equipo decide replanificar
quién lleva qué, en cuyo caso se actualiza aquí primero y después se ajustan los sprints
afectados.
