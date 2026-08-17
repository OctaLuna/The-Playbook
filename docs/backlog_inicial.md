# Backlog Inicial — The Playbook

**Proyecto:** The Playbook
**Equipo:** Sqleadores
**Versión:** 2.0 (alineado a `docs/project_spec.md` v2.0)
**Última actualización:** 16 de agosto de 2026
**Ubicación en repositorio:** `docs/backlog_inicial.md`
**Deriva de:** `docs/product_goal.md` (todo ítem debe trazarse a uno de los 3 pilares del Product Goal: predicción, explicación con evidencia temporalmente honesta, o medición/transparencia del desempeño)

> Regla de oro: si una decisión o avance no está registrado en GitHub, no es parte del avance del equipo. ClickUp enlaza a la evidencia, no la duplica.

---

## Cómo leer este backlog

Cada tarea sigue la fórmula: **Verbo + Objeto + Criterio + Evidencia**. Las tareas vagas tipo "investigar X" o "ver Y" no se aceptan como ítems de backlog — deben reescribirse hasta tener un resultado verificable.

Campos obligatorios por tarea (los mismos que exige ClickUp):
`Sprint` · `Dueño` · `Criterio de Aceptación` · `Enlace a Evidencia` · `Riesgo Asociado` · `Estado de Bloqueo`

---

## 📋 Lista: Discovery

### D1 — Validar y versionar el Product Goal con la fórmula usuario/valor/resultado medible
- **Sprint:** Sprint 0
- **Dueño:** Octavio Luna
- **Criterio de Aceptación:** El documento responde "sí" a la pregunta de control, incluye el pilar de evidencia "temporalmente honesta" (corrección de la auditoría v2.0), y está aprobado por al menos 2 integrantes.
- **Enlace a Evidencia:** `docs/product_goal.md`
- **Riesgo Asociado:** Definir un usuario demasiado amplio ("todo aficionado al fútbol") diluye la priorización del backlog.
- **Estado de Bloqueo:** No bloqueado.

### D2 — Priorizar 3 mercados de predicción para el MVP y documentar el criterio de selección
- **Sprint:** Sprint 0
- **Dueño:** Octavio Luna
- **Criterio de Aceptación:** Se identifican exactamente 3 mercados (1X2, over/under 2.5, BTTS), cada uno con justificación de por qué entra al MVP; se documenta explícitamente que LSTM y sentimiento pasan a stretch goal (no por falta de datos, sino por riesgo de cronograma).
- **Enlace a Evidencia:** `docs/mvp_scope.md`
- **Riesgo Asociado:** Sobre-alcance (scope creep) si el equipo intenta reincorporar los stretch goals antes de cerrar el MVP.
- **Estado de Bloqueo:** No bloqueado.

### D3 — Definir y versionar el Team Charter con roles, canales y Definition of Done
- **Sprint:** Sprint 0
- **Dueño:** Octavio Luna
- **Criterio de Aceptación:** Los 5 integrantes tienen rol, disponibilidad y riesgo personal declarado registrado; el DoD incluye los 3 criterios adicionales de `ml/`/`rag/` introducidos por v2.0 (split cronológico, filtro temporal, aislamiento de Celery).
- **Enlace a Evidencia:** `docs/team-charter.md`
- **Riesgo Asociado:** Riesgos personales no declarados por integrantes generan sobrecarga de trabajo mal distribuida en sprints futuros.
- **Estado de Bloqueo:** Bloqueado parcialmente — falta que cada integrante complete su "riesgo personal declarado" en la tabla.

---

## 📋 Lista: Data

### DA1 — Identificar fuentes multi-temporada (Football-Data.co.uk y Kaggle European Soccer Database) y registrar cobertura/licencia en el inventario de datos
- **Sprint:** Sprint 0
- **Dueño:** Einar Guillen
- **Criterio de Aceptación:** El inventario documenta, por cada fuente: cobertura histórica (ligas y temporadas), formato de acceso, licencia de uso, y qué datasets aportan cuotas históricas para el baseline interno de log-loss.
- **Enlace a Evidencia:** `docs/data_inventory.md`
- **Riesgo Asociado:** Diferencias de formato/nomenclatura de equipos entre Football-Data.co.uk y Kaggle pueden generar duplicados o desalineación al combinar ambas fuentes.
- **Estado de Bloqueo:** No bloqueado.

### DA2 — Cargar el histórico multi-temporada a PostgreSQL vía un job de Celery (carga única, no re-scraping por request)
- **Sprint:** Sprint 0–1
- **Dueño:** Einar Guillen
- **Criterio de Aceptación:** El job corre como tarea de Celery (nunca síncrono dentro del proceso API, según la regla arquitectónica de la sección 4 del spec), carga al menos las ligas top de ambas fuentes, y queda documentado cuántos partidos se cargaron por liga.
- **Enlace a Evidencia:** Link al PR del job de carga + `docs/data_inventory.md` (sección "Carga histórica")
- **Riesgo Asociado:** Volumen de datos mayor al esperado puede alargar el tiempo de carga inicial más de lo planificado en Sprint 0.
- **Estado de Bloqueo:** Bloqueado por DA1 (necesita el inventario para saber qué campos y cobertura tiene cada fuente).

### DA3 — Diseñar el esquema de base de datos (partidos, equipos, estadísticas, predicciones, track record, evidencia RAG) y versionarlo como diagrama
- **Sprint:** Sprint 0
- **Dueño:** Einar Guillen
- **Criterio de Aceptación:** El diagrama incluye entidades equipo, partido, estadística_partido, predicción, track_record y noticia_indexada (con campo `fecha_publicacion` para soportar el filtro temporal del RAG), con relaciones y tipos de dato definidos.
- **Enlace a Evidencia:** `docs/db_schema.md`
- **Riesgo Asociado:** Un esquema mal normalizado obliga a migraciones costosas una vez el modelo de ML y el pipeline RAG ya dependen de la estructura.
- **Estado de Bloqueo:** Bloqueado por DA1.

### DA4 — Registrar en el inventario las fuentes operativas (API-Football, football-data.org) distinguidas de las fuentes históricas de entrenamiento
- **Sprint:** Sprint 0
- **Dueño:** Einar Guillen
- **Criterio de Aceptación:** El inventario deja explícito que API-Football/football-data.org alimentan solo datos operativos (temporada en curso, lesiones), nunca el entrenamiento histórico — evita repetir la ambigüedad señalada en la auditoría v1.0.
- **Enlace a Evidencia:** `docs/data_inventory.md` (sección "Fuentes operativas")
- **Riesgo Asociado:** Límite de requests gratuito de API-Football puede ser insuficiente en temporada alta con varios partidos por jornada.
- **Estado de Bloqueo:** No bloqueado.

---

## 📋 Lista: Architecture

### AR1 — Redactar ADR-001: elección de FastAPI como backend único
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El ADR documenta el contexto, al menos 2 alternativas descartadas (Node.js/Express, Django), y la justificación de la decisión final.
- **Enlace a Evidencia:** `docs/adr/ADR-001-backend-fastapi.md`
- **Riesgo Asociado:** Ninguna decisión registrada obliga a re-discutir la misma elección en sprints futuros, perdiendo tiempo.
- **Estado de Bloqueo:** No bloqueado.

### AR2 — Redactar ADR-002: elección de pgvector sobre un vector DB dedicado
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El ADR justifica la elección en función del volumen de noticias indexadas esperado del proyecto.
- **Enlace a Evidencia:** `docs/adr/ADR-002-vector-storage.md`
- **Riesgo Asociado:** Si el volumen de noticias indexadas crece más de lo previsto, pgvector puede no escalar igual que un vector DB dedicado.
- **Estado de Bloqueo:** No bloqueado.

### AR3 — Redactar ADR-003: adopción de AWS Bedrock (Claude + Titan Embeddings) sobre APIs directas
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El ADR documenta el motivo del cambio (autenticación IAM, facturación unificada, eliminación de la ambigüedad de embeddings de v1.0), y deja explícito que se usa el Converse API para no acoplar el backend a un formato específico de proveedor.
- **Enlace a Evidencia:** `docs/adr/ADR-003-aws-bedrock.md`
- **Riesgo Asociado:** Dependencia de un solo proveedor gestionado (Bedrock) para todo el pipeline generativo — si hay problemas de disponibilidad regional, afecta tanto LLM como embeddings a la vez.
- **Estado de Bloqueo:** No bloqueado.

### AR4 — Redactar ADR-004: capa de ensamble entre Dixon-Coles y XGBoost
- **Sprint:** Sprint 0
- **Dueño:** Leandro Colque
- **Criterio de Aceptación:** El ADR documenta el esquema de promedio ponderado, el criterio de ajuste de pesos por backtesting cronológico, y cómo entra el LSTM como generador de features (no como modelo independiente) si se activa el stretch goal.
- **Enlace a Evidencia:** `docs/adr/ADR-004-ensemble-layer.md`
- **Riesgo Asociado:** Un ensamble mal calibrado puede terminar dándole más peso al modelo equivocado si el backtesting no cubre suficientes jornadas.
- **Estado de Bloqueo:** No bloqueado.

### AR5 — Diagramar la arquitectura general del sistema, incluyendo la separación obligatoria de Celery y el flujo del ensemble
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El diagrama muestra el flujo end-to-end (APIs/datasets → ML/ensemble → RAG con filtro temporal → frontend) y refleja explícitamente que ningún job pesado corre en el proceso API.
- **Enlace a Evidencia:** `docs/architecture.md`
- **Riesgo Asociado:** Un diagrama desactualizado respecto al código real genera confusión en la incorporación de nuevas tareas.
- **Estado de Bloqueo:** Bloqueado por AR1, AR2, AR3 y AR4.

### AR6 — Evaluar y documentar los riesgos técnicos principales del proyecto (incluye los hallazgos de la auditoría v2.0)
- **Sprint:** Sprint 0
- **Dueño:** Leandro Colque
- **Criterio de Aceptación:** Se documentan al menos 6 riesgos técnicos (techo de predictibilidad, límite de requests, dependencia de scraping, fuga temporal en RAG, costo/latencia de Bedrock, riesgo de cronograma por stretch goals), cada uno con probabilidad, impacto y mitigación.
- **Enlace a Evidencia:** `docs/risks.md`
- **Riesgo Asociado:** — (esta tarea *es* el registro de riesgos; ver Lista Risk para el detalle operativo)
- **Estado de Bloqueo:** No bloqueado.

---

## 📋 Lista: Build / QA / Deploy

### BQ1 — Configurar el repositorio con la estructura de monorepo del spec v2.0 y protección de rama main
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El repo replica la estructura de `docs/project_spec.md` sección 10 (`frontend/`, `backend/app/`, `backend/ml/`, `backend/rag/`, `backend/workers/`, `infra/`, `docs/`); `main` tiene protección activada; existe un PR de prueba validando el flujo.
- **Enlace a Evidencia:** Link al PR de configuración inicial en GitHub
- **Riesgo Asociado:** Sin protección de rama, un push accidental a `main` puede romper la demo.
- **Estado de Bloqueo:** No bloqueado.

### BQ2 — Habilitar acceso a modelos de AWS Bedrock (Claude + Titan Embeddings) y crear el rol IAM con permisos mínimos
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El "model access" está habilitado por región/cuenta para ambos modelos, existe un rol IAM dedicado con permiso `bedrock:InvokeModel` acotado a los ARNs usados, y se documenta el procedimiento (sin exponer credenciales) para que el equipo no dependa de una sola persona.
- **Enlace a Evidencia:** `docs/adr/ADR-003-aws-bedrock.md` (sección de configuración) + captura del "model access" habilitado
- **Riesgo Asociado:** Dejar esto para cuando el equipo ya esté implementando el RAG bloquearía todo el pipeline en un sprint avanzado — por eso se resuelve en Sprint 0.
- **Estado de Bloqueo:** No bloqueado.

### BQ3 — Implementar el modelo baseline de Dixon-Coles con split cronológico y prueba automatizada que lo verifique
- **Sprint:** Sprint 1
- **Dueño:** Leandro Colque
- **Criterio de Aceptación:** El modelo entrena sobre el histórico combinado (Football-Data.co.uk + Kaggle), usa split cronológico (nunca `train_test_split` aleatorio), y existe un test que falla el build si algún pipeline de `ml/` no respeta el orden temporal.
- **Enlace a Evidencia:** Link al PR con el código del modelo + resultados de pruebas
- **Riesgo Asociado:** Equipos con pocos partidos históricos (recién ascendidos) producen predicciones poco confiables — necesita manejo explícito.
- **Estado de Bloqueo:** Bloqueado por DA2 (requiere el histórico ya cargado en PostgreSQL).

### BQ4 — Implementar el modelo XGBoost y la capa de ensamble (promedio ponderado con Dixon-Coles), registrando pesos en MLflow
- **Sprint:** Sprint 1
- **Dueño:** Leandro Colque
- **Criterio de Aceptación:** XGBoost entrena sobre las mismas features + forma/head-to-head/descanso; el ensamble combina ambos modelos por promedio ponderado ajustado por backtesting; los pesos finales y el proceso quedan registrados en MLflow.
- **Enlace a Evidencia:** Link al PR + experimento de MLflow enlazado
- **Riesgo Asociado:** Un ensamble mal calibrado puede terminar dándole más peso al modelo equivocado si el backtesting no cubre suficientes jornadas.
- **Estado de Bloqueo:** Bloqueado por BQ3 y AR4.

### BQ5 — Implementar el filtro temporal obligatorio en el retrieval del RAG (`fecha_publicacion_noticia < fecha_kickoff`)
- **Sprint:** Sprint 1
- **Dueño:** Rodrigo Rivera
- **Criterio de Aceptación:** Toda query de retrieval contra pgvector incluye la restricción a nivel de SQL, no como convención de equipo; existe una prueba que confirma que noticias posteriores al kickoff nunca se recuperan para ese partido.
- **Enlace a Evidencia:** Link al PR + resultado de la prueba de filtro temporal
- **Riesgo Asociado:** Sin este filtro, el sistema podría explicar predicciones con evidencia que en la realidad no existía antes del partido, invalidando el pilar 2 del Product Goal.
- **Estado de Bloqueo:** Bloqueado por DA3 (requiere el esquema con campo `fecha_publicacion`).

### BQ6 — Configurar pipeline de CI en GitHub Actions para pruebas automáticas en cada PR
- **Sprint:** Sprint 1
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** Cada PR hacia `develop` o `qa` ejecuta automáticamente las pruebas existentes (incluye el test de split cronológico y el de filtro temporal) y bloquea el merge si fallan.
- **Enlace a Evidencia:** `.github/workflows/ci.yml` + link a una ejecución exitosa
- **Riesgo Asociado:** Sin CI, un PR con pruebas rotas puede fusionarse "a simple vista" sin que nadie corra las pruebas localmente.
- **Estado de Bloqueo:** Bloqueado por BQ1.

---

## 📋 Lista: Risk

### R1 — Registrar el riesgo del "techo de predictibilidad" del fútbol y su plan de mitigación
- **Sprint:** Sprint 0
- **Dueño:** Leandro Colque
- **Criterio de Aceptación:** El registro documenta que ningún modelo supera cierto nivel de precisión, y define log-loss/Brier score vs. baseline de mercado como métrica honesta de éxito, no accuracy cruda.
- **Enlace a Evidencia:** `docs/risks.md` (entrada R1)
- **Riesgo Asociado:** Comunicar mal este límite ante el tribunal puede leerse como que el proyecto "no funciona", cuando es honestidad científica esperable en el dominio.
- **Estado de Bloqueo:** No bloqueado.

### R2 — Registrar el riesgo de límite de requests gratuito en APIs operativas y su plan de mitigación
- **Sprint:** Sprint 0
- **Dueño:** Einar Guillen
- **Criterio de Aceptación:** El registro define el límite exacto de API-Football, la estrategia de cache en Redis, y football-data.org como fuente de respaldo — distinguiendo claramente que el histórico ya no depende de estas APIs (ver DA1/DA2).
- **Enlace a Evidencia:** `docs/risks.md` (entrada R2)
- **Riesgo Asociado:** Si se agota el límite diario durante una demo en vivo, el sistema puede mostrar datos operativos desactualizados.
- **Estado de Bloqueo:** No bloqueado.

### R3 — Registrar el riesgo de dependencia del scraping de Understat y su plan de mitigación
- **Sprint:** Sprint 0
- **Dueño:** Rodrigo Rivera
- **Criterio de Aceptación:** El registro define qué pasa si Understat cambia su estructura HTML, y establece una prueba de scraping que se ejecuta periódicamente para detectar rupturas.
- **Enlace a Evidencia:** `docs/risks.md` (entrada R3)
- **Riesgo Asociado:** El scraping es la fuente menos estable del proyecto por no depender de una API oficial.
- **Estado de Bloqueo:** No bloqueado.

### R4 — Registrar el riesgo de fuga temporal en el RAG (evidencia posterior al partido) y su plan de mitigación
- **Sprint:** Sprint 0
- **Dueño:** Rodrigo Rivera
- **Criterio de Aceptación:** El registro documenta el hallazgo crítico de la auditoría v1.0→v2.0 y confirma que la mitigación (filtro SQL obligatorio, tarea BQ5) es una restricción de query, no una convención de equipo.
- **Enlace a Evidencia:** `docs/risks.md` (entrada R4)
- **Riesgo Asociado:** Es el riesgo de mayor impacto reputacional/académico del proyecto: invalida la honestidad del track record si no se controla.
- **Estado de Bloqueo:** No bloqueado.

### R5 — Registrar el riesgo de costo/latencia por invocaciones a Bedrock y su plan de mitigación
- **Sprint:** Sprint 0
- **Dueño:** Carol Zevallos
- **Criterio de Aceptación:** El registro documenta la mitigación vía caché de explicaciones en Redis (solo se regenera si cambió la evidencia subyacente) y define un umbral de latencia aceptable para la demo.
- **Enlace a Evidencia:** `docs/risks.md` (entrada R5)
- **Riesgo Asociado:** Invocar Bedrock en cada request sin cache puede volver el sistema lento o costoso durante la demo con jurado.
- **Estado de Bloqueo:** No bloqueado.

### R6 — Registrar el riesgo de cronograma por incluir LSTM/sentimiento en el núcleo del MVP y su mitigación
- **Sprint:** Sprint 0
- **Dueño:** Octavio Luna
- **Criterio de Aceptación:** El registro documenta la decisión de mover ambos componentes a stretch goal (sección 2.3 del spec) y el criterio para reincorporarlos solo si el MVP (Dixon-Coles + XGBoost + RAG) está sólido antes de la fecha límite.
- **Enlace a Evidencia:** `docs/risks.md` (entrada R6)
- **Riesgo Asociado:** Intentar entregar los 5 componentes de IA a la vez sin priorización clara es la causa más común de que un taller no llegue a una demo funcional.
- **Estado de Bloqueo:** No bloqueado.

---

## Trazabilidad

- Todas las tareas listadas deben crearse como ítems individuales en **ClickUp**, cada una en la lista correspondiente (Discovery, Data, Architecture, Build/QA/Deploy, Risk), replicando exactamente estos 6 campos.
- ClickUp **enlaza** a la evidencia en GitHub — no reescribe ni duplica el contenido de los archivos `.md`.
- Cualquier tarea nueva que se agregue al backlog después del Sprint 0 debe seguir la misma fórmula (Verbo + Objeto + Criterio + Evidencia) y debe trazarse a alguno de los 3 pilares del Product Goal (`docs/product_goal.md`).
- Este archivo se actualiza vía Pull Request, siguiendo el flujo de ramas definido en `docs/team-charter.md`.