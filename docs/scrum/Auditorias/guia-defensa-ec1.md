# Guía de preparación — Defensa Grupal EC1 (SIS-352)

Esta guía traduce la rúbrica de "Elemento de Competencia 1 — Defensa Grupal y Revisión del
Repositorio" (20 puntos, presencial) a **qué ya tenemos en el repo (con ruta exacta) y qué falta
crear antes del día de la defensa**. Está ordenada igual que la "Secuencia Obligatoria de la
Presentación" para poder usarla como guión de ensayo.

> **Nota importante sobre el estado del repo**: esta guía se escribió el 2026-09-17, poco
> después de que se mergeara a `develop` el trabajo de Dixon-Coles, XGBoost, el ensamble, la
> calibración y el tracking de MLflow (`T012d`, `T012e`, `T012`, `T013`, `T025` — commits
> `82923ef`…`21aed96`, merge `a0b36a8`) y los modelos de `003` (`T004-T008`). Esto ocurrió
> **después** de `docs/scrum/Auditorias/auditoria-avance-2026-09-17.md`, así que esa auditoría
> ya está desactualizada en el punto de "Leandro no tiene Dixon-Coles/XGBoost" — el código ya
> existe. Lo que **no** se verificó todavía es si esos módulos ya se corrieron y produjeron un
> resultado real (ver bloque 6, Línea Base). Antes de la defensa conviene re-correr `pytest` y
> actualizar esa auditoría — no está hecho en este documento.

## Mapa de la rúbrica (20 pts)

| Criterio | Puntos | Qué exige el estándar de excelencia |
|---|---|---|
| Problema y Métricas | 3 | Problema formulado, usuarios identificados, alcance viable, métricas verificables |
| Datos y Gobierno | 3 | Fuentes viables; calidad, privacidad, licencias y riesgos documentados |
| Arquitectura | 4 | Diagramas C4 coherentes; decisiones justificadas con ADR; seguridad desde el diseño |
| Riesgos y Línea Base | 4 | 2 riesgos priorizados y mitigados; baseline reproducible con métrica analizada |
| Repo y Trazabilidad | 4 | README, backlog, commits, PRs muestran evolución real y contribución de todos |
| Defensa Técnica | 2 | Presentación ordenada con evidencia; respuestas precisas y justificadas |

Los dos criterios con **gap total hoy** son Arquitectura (sin C4) y Riesgos y Línea Base (sin
risk register ni resultado de experimento documentado) — 8 de los 20 puntos. Priorizar ahí.

---

## 1. Problema y Contexto

**Pide la rúbrica:** qué se resuelve, por qué es relevante, para quién.

**Ya existe:**
- `README.md` (raíz) — los 3 pilares de valor del proyecto y a quién sirve.
- `docs/product_goal.md` — declara la necesidad y el usuario de forma formal.
- `memory/constitution.md` — el "porqué" ético/técnico del proyecto (predicción explicable y
  auditable, nunca un comparador de casas de apuestas).

**Falta:** nada estructural — es el bloque mejor cubierto. Sí conviene que quien presente esta
parte pueda decir en una frase quién es el usuario (no solo "cualquiera que quiera predicciones")
y por qué el enfoque de *explicación verificable* es la diferencia frente a una app de apuestas
cualquiera.

## 2. Product Goal y Valor

**Pide la rúbrica** — este bloque en realidad junta 3 cosas distintas que la rúbrica pide por
separado en "Fundamentos" y hay que mostrar las 3, no solo el Product Goal:

1. **Product Goal**: el objetivo del producto en una frase.
2. **Alcance**: qué incluye el proyecto y **qué excluye explícitamente** (con el porqué de cada
   exclusión — no alcanza con decir "no lo hicimos", hay que decir "decidimos no hacerlo y por
   qué"). Es el criterio "Delimitación estricta del proyecto" de la rúbrica.
3. **Métricas de valor**: cómo se mide si el proyecto funciona.

**Ya existe (los 3, con material fuerte):**
- **Product Goal**: `docs/product_goal.md` — formato "Para [usuario] que [necesidad],
  construiremos [producto] que [valor], [resultado medible]", con ejemplos de control
  bueno/malo para poder defenderlo si preguntan "¿por qué está redactado así?".
- **Alcance (qué incluye)**: `docs/project_spec.md` §2 (los 4 features del MVP: `001`-`004`) y
  §3 (tabla comparativa contra competidores reales — Forebet, xGscore, NerdyTips, Scores24 —
  mostrando en qué igualan y en qué se diferencian: baseline de mercado honesto + track record
  auditable, algo que ningún competidor expone).
- **Alcance (qué excluye, con justificación)** — este es el material más fuerte para defender
  "delimitación estricta", tiene su propia sección dedicada:
  - `docs/project_spec.md` §2.3 "Stretch goals": LSTM y modelo de sentimiento se movieron de
    "núcleo" a *post-MVP* — **no por falta de datos, sino por gestión de riesgo de cronograma**
    (son los componentes de mayor costo de tuning y los que menos mueven los 3 pilares de valor).
  - `docs/project_spec.md` §2.4 "Explícitamente fuera de alcance (no se hará)": *live scores*
    minuto a minuto (no aporta al objetivo académico) y **comparador de cuotas como producto
    visible** (zona gris legal/ética — las cuotas solo son baseline interno, nunca se muestran
    al usuario; esto además es el Artículo V de la constitución, no una opinión suelta).
- **Métricas de valor**: log-loss y Brier score por mercado vs. baseline de mercado —
  `specs/001-prediccion-partido/ml-design.md` §7, expuestas al usuario en el panel de
  `003-track-record-publico` (`specs/003-track-record-publico/spec.md`).

**Falta:** nada que crear — el material ya cubre las 3 partes. Lo que falta es **decisión de
guión**: quien presente este bloque debe mostrar explícitamente la tabla de §2.4 (qué NO se
hizo y por qué) — es la parte que más impresiona en una defensa, porque demuestra que la
exclusión fue una decisión de diseño y no un olvido. No la salten por ir directo a lo que sí
se construyó.

## 3. Datos

**Pide la rúbrica:** ecosistema de fuentes, calidad, privacidad/licencias.

**Ya existe:**
- `docs/project_spec.md` §6 — tabla completa de fuentes evaluadas: Football-Data.co.uk
  (histórico multi-década/multi-liga, fuente principal de entrenamiento), Kaggle European
  Soccer Database, StatsBomb Open Data, API-Football (RapidAPI, datos operativos en vivo),
  football-data.org (respaldo), Understat (xG de referencia).
- `specs/001-prediccion-partido/ml-design.md` — mapeo exacto de columnas de Football-Data.co.uk
  (`FTHG`/`FTAG`, etc.) al modelo de datos interno.
- Código real de carga/calidad: `backend/ml/data/loader.py`, `backend/ml/data/alias.py`, con
  tests (`backend/ml/data/test_loader.py`, `test_alias.py`) que sí corren contra Postgres real.
- **Perfilado estadístico (EDA) — `backend/ml/data/eda.py`, ya implementado (2026-09-17,
  test-first: `test_eda.py`, 7 tests en verde, `ruff`/`mypy` limpios).** Responde en vivo las 3
  preguntas de calidad que pide la rúbrica sin necesitar Postgres ni Docker — solo el CSV crudo:
  - `perfilar_columnas(ruta_csv)`: total de filas y % de vacíos/nulos por columna requerida
    (`Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`).
  - `perfilar_alias(nombres_crudos, liga, tabla)`: qué % de nombres de equipo del CSV ya
    resuelve `equipo_alias.csv`, y lista exactamente cuáles faltan — la inconsistencia de
    nombres que pide la rúbrica ("Man United" vs. "Manchester Utd").
  - `main()`/CLI: corre ambos y además imprime `df[["FTHG","FTAG"]].describe()` con pandas —
    literalmente el `describe()` que pide la rúbrica.
  - **Cómo correrlo en vivo**, desde `backend/`:
    ```bash
    python -m ml.data.eda ml/data/raw/premier_league_2024.csv premier_league
    ```
  - **Prerrequisito para el día de la defensa**: hace falta (1) un CSV real de
    Football-Data.co.uk en `backend/ml/data/raw/` (carpeta gitignorada, se descarga
    localmente — no está en el repo) y (2) `backend/ml/data/equipo_alias.csv` con al menos los
    equipos de esa liga/temporada (tampoco existe todavía en el repo — hay que crearlo con las
    columnas `alias,equipo_id,liga`, como en el ejemplo de `test_alias.py`). Sin esos dos
    archivos locales el comando no tiene nada que leer.

**Falta (gap real, 3 pts en juego):**
- **Privacidad/licencias**: no hay ninguna sección que documente si Football-Data.co.uk/Kaggle
  permiten uso académico o redistribución. Agregar un párrafo corto a `project_spec.md` §6 antes
  de la defensa — es una pregunta obvia del docente ("¿pueden usar legalmente estos datos?").

## 4. Arquitectura

**Pide la rúbrica:** componentes, interfaces, flujo de datos (C4 o equivalente), ADR de cada
decisión técnica frente a alternativas descartadas, seguridad desde el diseño.

**Ya existe:**
- Arquitectura descrita en **texto y tablas**, no en diagrama: `docs/project_spec.md` §10
  (rutas canónicas, capas), `specs/00X-*/plan.md` (Fase -1, gates de simplicidad).
- **1 ADR real**: `docs/adr/0001-badge-confianza-calibrado.md` — decide que el badge de
  confianza se deriva de calibración empírica, no de distancia a un reparto uniforme, con 3
  alternativas descartadas en tabla (mantener distancia a uniforme, badge provisional por
  fases, ocultar el badge). Es un ejemplo perfecto de "ADR bien hecho" — mostrar este primero.
- Seguridad desde el diseño: Artículo VI de `memory/constitution.md` (aislamiento de procesos,
  contenido scrapeado como no confiable, sanitización anti-prompt-injection en
  `backend/rag/ingestion/sanitizer.py`, con tests reales).

**Falta (gap total, 4 pts en juego — el más urgente):**
- **Ningún diagrama C4 existe en el repo** (se confirmó con búsqueda exhaustiva). Mínimo viable
  antes de la defensa: 1 diagrama de **Contexto** (usuario ↔ The Playbook ↔ fuentes de datos
  externas) + 1 de **Contenedores** (FastAPI, Postgres+pgvector, Redis, Celery workers, RAG,
  Next.js) — con eso se cubre "Diagramas C4 coherentes" sin sobre-invertir tiempo.
- **Solo 1 ADR de 20+ decisiones técnicas reales del proyecto.** Candidatas obvias para 1-2 ADRs
  adicionales antes de la defensa (ya están decididas y justificadas en `project_spec.md`, solo
  falta el formato ADR): por qué Dixon-Coles **+** XGBoost en ensamble en vez de solo uno de los
  dos; por qué Postgres+pgvector en vez de un vector store separado (Art. VII, simplicidad); por
  qué Celery para todo lo pesado en vez de correrlo en el proceso de FastAPI (Art. VI).

## 5. Riesgos y Seguridad

**Pide la rúbrica:** amenazas técnicas y de IA desde el diseño, con controles/mitigaciones.

**Ya existe (mitigaciones puntuales, sin encuadrarlas como "riesgo"):**
- Fuga temporal de datos → Artículo IV de la constitución + filtro SQL obligatorio
  `fecha_publicacion < fecha_kickoff` en `backend/rag/retrieval/query.py` (con test de
  integración real contra pgvector).
- Prompt injection vía contenido scrapeado → `backend/rag/ingestion/sanitizer.py` + regla de
  bloque delimitado explícito en los prompts (Art. VI).
- Badge de confianza engañoso → ADR 0001 (ver bloque 4).
- Comparador de apuestas expuesto como funcionalidad → prohibición explícita, Art. V.

**Falta (gap total, comparte los 4 pts con Línea Base):**
No existe un **Risk Register** dedicado — lo que hay es riesgo de *cronograma del equipo*
(`docs/team-charter.md` §1), no riesgo técnico/de IA. Antes de la defensa, crear
`docs/risk-register.md` con al menos 2-3 filas priorizadas, por ejemplo:
1. **Sesgo/degradación del modelo sin detectar** → mitigación: baseline de mercado + alerta si
   log-loss se degrada más de un umbral (ya mencionado en `project_spec.md` línea ~191, falta
   formalizarlo como riesgo).
2. **Alucinación del LLM en la explicación** → mitigación: RAG con evidencia citada + Art. VI
   (el LLM nunca ejecuta acciones ni afirma sin fuente).
3. **Fuga temporal de datos** (ya mitigada, ver arriba) → formalizarla como riesgo #3 igual,
   demuestra que el diseño la tuvo en cuenta desde el inicio, no que se descubrió tarde.

## 6. Línea Base y Evidencia

**Pide la rúbrica:** estado de datos antes de procesar, pipeline reproducible, referencia mínima
(baseline) contra la cual comparar futuras mejoras. Regla explícita: si no hay resultados,
presentar la justificación técnica de cómo se establecerá; un experimento fallido documentado
también es evidencia válida.

**Ya existe:**
- Diseño completo: `specs/001-prediccion-partido/ml-design.md` §7 — un experimento MLflow por
  mercado (`the-playbook/{1x2, over_under_2_5, btts}`), qué métricas registrar (log-loss y
  Brier de Dixon-Coles solo, XGBoost solo, y ensamble), baseline = cuotas históricas de mercado.
- Código ya mergeado (recién, ver nota al inicio): `backend/ml/models/dixon_coles/`,
  `backend/ml/models/xgboost/` (con `train.py`/`predict.py`/`evaluate.py` cada uno),
  `backend/ml/ensemble/predict.py`, `backend/ml/evaluation/{calibration,mlflow_tracking}.py`.

**Falta (gap real, comparte 4 pts con Riesgos — el segundo más urgente):**
- **No hay evidencia de que el pipeline se haya corrido de punta a punta.** No existe carpeta
  `mlruns/` ni un `.md` con un log-loss/Brier score real obtenido. Antes de la defensa: **correr
  el entrenamiento contra los datos reales** (`backend/ml/data/loader.py` → features → Dixon-
  Coles/XGBoost → ensamble → `mlflow_tracking.py`) y guardar el resultado (aunque sea parcial o
  peor que el baseline — un resultado documentado y analizado vale más que ningún resultado).
  Si no alcanza el tiempo, la rúbrica permite explícitamente llevar solo "la justificación
  técnica de cómo se establecerá" — pero eso es un piso más bajo, mejor evitarlo si se puede.

## 7. Gestión y Cierre

**Pide la rúbrica:** backlog, bloqueos, viabilidad, próximos pasos.

**Ya existe:**
- `docs/scrum/product-backlog.md`, `docs/scrum/sprint-01.md`…`sprint-08.md`,
  `docs/scrum/equipo-y-tracks.md` — backlog completo y trazable a `specs/00X-*/tasks.md`.
- `docs/scrum/Auditorias/auditoria-avance-2026-09-17.md` — bloqueos reales identificados con
  evidencia de ejecución (aunque parcialmente desactualizada, ver nota inicial).
- `docs/team-charter.md` §4 — protocolo de manejo de bloqueos.

**Falta:** actualizar el resumen de "próximos pasos" con el estado post-merge de hoy (Dixon-
Coles/XGBoost/ensamble ya no son el bloqueante; el nuevo cuello de botella pasa a ser
`backend/app/services/` y `backend/app/api/`, que siguen vacíos — sin eso ningún endpoint de
negocio existe más allá de `/health`).

---

## Checklist "qué revisará el docente en vivo" (estado real, no aspiracional)

**Documentación y Datos**
- [x] README existe — [ ] pero está desactualizado ("no hay código todavía" es falso hoy)
- [x] Definiciones (problema, métricas, exclusiones) — `docs/product_goal.md`, `project_spec.md`
- [x] Datos: inventario de fuentes — [x] perfilado/EDA (`backend/ml/data/eda.py`, ver bloque 3) — [ ] sigue faltando privacidad/licencias
- [ ] Arquitectura y Riesgos: C4 y Risk Register — **no existen, crear antes de la defensa**

**Scrum y Ejecución**
- [x] Product Goal, Backlog priorizado, evidencia de sprint — completo en `docs/scrum/`
- [ ] Línea base: pipeline existe pero **no hay evidencia de un run real documentado**
- [x] Uso de IA declarado — `docs/team-charter.md` §5, con disclosure en PRs

## Antipatrones — cuáles son un riesgo real hoy en este repo

| Antipatrón | Riesgo hoy | Por qué |
|---|---|---|
| Afirmaciones sin evidencia | 🟡 Medio | Si se presenta Dixon-Coles/XGBoost como "listo" sin mostrar un run de MLflow real |
| Arquitectura "porque sí" | 🔴 Alto | 0 diagramas C4, solo 1 ADR — hay que armar los mínimos antes de la defensa |
| Evidencia "en foto" | 🟢 Bajo | El repo permite ejecución real en vivo (`docker compose up`, `pytest`, `npm test`, ya verificado que corren) |
| Repositorio fantasma | 🟢 Bajo | Historial real de PRs por tarea — **excepto** el frontend, que llegó en un solo commit (ver abajo) |
| Efecto "solo él sabe" | 🟡 Medio | El frontend completo (34 tareas de `004`) es un solo commit de Carol — si el docente pregunta a Rodrigo/Einar/Leandro sobre el frontend, deben poder explicarlo igual aunque no lo hayan escrito |
| Ocultar el fracaso | 🟢 Bajo | La auditoría ya documenta honestamente lo que no funciona (T012d/e cuando aún no existían) — mantener esa transparencia en la presentación |
| Uso opaco de IA | 🟢 Bajo | Ya declarado y con proceso de disclosure — `docs/team-charter.md` §5 |

## Las 4 preguntas de cierre — borrador de respuesta honesta

1. **¿El problema está bien formulado, delimitado, con métricas claras?** Sí — `product_goal.md`
   y las métricas de log-loss/Brier vs. baseline de mercado están bien definidas y verificables.
2. **¿Los datos y la arquitectura hacen viable la solución?** Los datos sí (fuentes reales,
   loader probado). La arquitectura está bien diseñada pero **no está documentada visualmente**
   todavía — hay que resolver eso antes de poder decir "sí" sin reservas.
3. **¿El repositorio demuestra de forma verificable cómo evolucionó el trabajo y quién lo hizo?**
   Sí en general (PRs por tarea, ramas nombradas por ID) — con la salvedad del frontend en un
   solo commit, que hay que poder explicar si preguntan por qué no tiene historial incremental.
4. **¿Todos pueden justificar las decisiones frente al docente?** Depende de practicar las
   partes de compañeros — es el punto de mayor riesgo dado el reparto por track fijo
   (`docs/scrum/equipo-y-tracks.md`): cada uno conoce a fondo solo su spec.

## Tareas pre-defensa, priorizadas por impacto en puntaje

1. **Correr el pipeline de ML y documentar un resultado real** (afecta 4 pts de Línea Base) —
   aunque el resultado sea preliminar o peor que el baseline, es mejor que nada.
2. **Crear `docs/risk-register.md`** con 2-3 riesgos técnicos/IA priorizados y mitigados (afecta
   los mismos 4 pts, junto con el punto 1).
3. **Crear 2 diagramas C4 (Contexto + Contenedores) y 1-2 ADRs adicionales** (afecta 4 pts de
   Arquitectura) — usar `docs/adr/0001-badge-confianza-calibrado.md` como plantilla de formato.
4. **Actualizar `README.md`** para que refleje el estado real (ya no "sin código") — bajo riesgo
   de puntaje directo, pero alto riesgo de antipatrón "repositorio fantasma" si el docente lo lee
   primero.
5. **Agregar privacidad/licencias de fuentes de datos** a `docs/project_spec.md` §6 (afecta 3
   pts de Datos y Gobierno) — es lo único que le falta al bloque de Datos.
6. **Sesión de repaso cruzado**: cada integrante explica en voz alta la spec de otro compañero,
   al menos una vez antes del día de la defensa (mitiga "efecto solo él sabe").
7. ~~Re-correr la auditoría~~ — **hecho** (`docs/scrum/Auditorias/auditoria-avance-2026-09-17.md`,
   2ª pasada): confirmó que Dixon-Coles/XGBoost/ensamble ya existen; el bloqueante pasó a ser
   `T014-T016` (servicio/router/worker de Rodrigo).
8. ~~Crear el EDA en vivo~~ — **hecho** (`backend/ml/data/eda.py`, ver bloque 3): falta solo
   conseguir el CSV real + `equipo_alias.csv` antes del día de la defensa para poder correrlo.
