# The Playbook — Contexto del Proyecto

> Este archivo es el equivalente en OpenSpec de las convenciones técnicas y principios no negociables del proyecto. La versión extendida, con el razonamiento completo de cada artículo y el proceso de enmienda, vive en `memory/constitution.md` (formato spec-kit) — este documento es un resumen orientado a que el asistente de IA tenga contexto rápido antes de proponer o implementar un cambio.

## Stack tecnológico
- **Frontend:** Next.js 15 (App Router) + TypeScript, Tailwind CSS + shadcn/ui, Recharts, TanStack Query.
- **Backend:** FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0 async + Alembic, PostgreSQL 16, pgvector (índice HNSW), Redis.
- **Tareas en background:** Celery + Redis — ningún job de entrenamiento/reindexado corre en el proceso del API (ver convención no negociable #3 abajo).
- **ML:** statsmodels (Dixon-Coles) + XGBoost, combinados por ensamble de promedio ponderado; SHAP (TreeExplainer) solo sobre XGBoost.
- **RAG/LLM:** LangChain + AWS Bedrock (Claude) vía Converse API (`boto3`/`bedrock-runtime`), Amazon Titan Text Embeddings V2.
- **Contenerización/CI:** Docker + docker-compose, GitHub Actions.

Detalle completo y justificación de cada elección: `docs/project_spec.md`, sección 5.

## Convenciones no negociables (derivadas de `memory/constitution.md`)
1. **Integridad temporal:** split cronológico obligatorio en entrenamiento (nunca aleatorio); todo retrieval RAG filtra `fecha_publicacion_noticia < fecha_kickoff_del_partido` a nivel de query SQL, nunca como post-filtro en memoria.
2. **Independencia del mercado:** las cuotas de casas de apuestas se usan únicamente como baseline interno (log-loss); ninguna columna de odds puede llegar al feature set de entrenamiento; nunca se expone un comparador de casas de apuestas como funcionalidad independiente.
3. **Aislamiento de procesos:** ningún job de entrenamiento ML ni de reindexado RAG corre en el mismo proceso que atiende requests HTTP — todo vía Celery, incluso en desarrollo local con docker-compose.
4. **Seguridad de la ingesta:** contenido scrapeado (News API/RSS) se trata como dato no confiable — se delimita explícitamente en el prompt (bloque XML) y se sanitiza antes de indexar; el LLM nunca ejecuta acciones ni código a partir de contenido indexado.
5. **Simplicidad:** máximo 3 módulos/proyectos por implementación inicial; prohibido el future-proofing (no se construye para requisitos hipotéticos — ej. líneas O/U o idiomas no confirmados en el MVP).
6. **Test-first:** ningún código de implementación antes de escribir la prueba correspondiente y confirmar que falla (fase Red).

## Estructura del repositorio
- `openspec/` — este árbol: propuestas de cambio (`changes/`) y especificaciones vigentes (`specs/`, vacío hasta el primer `archive`).
- `memory/` + `specs/00X-.../` — **fuente canónica** de la documentación spec-kit (historias de usuario, planes técnicos, modelo de datos, contratos, quickstarts, **y tareas**). Cada `design.md` de OpenSpec referencia estos archivos en vez de duplicarlos.

> **Precedencia (resuelto en la auditoría SDD).** spec-kit es canónico. OpenSpec aporta
> únicamente `proposal.md` y `design.md`. Los `changes/*/tasks.md` son **stubs que apuntan
> a `specs/00X-.../tasks.md`** y no deben editarse: hasta la auditoría eran copias byte a
> byte, es decir, dos fuentes de verdad sin regla de desempate. El hook
> `.claude/hooks/sot-guard.mjs` bloquea las escrituras a esos stubs.
- `backend/`, `frontend/`, `infra/`, `docs/` — según la sección 10 de `docs/project_spec.md`.

## Cómo usar este proyecto con OpenSpec
- Los cuatro changes actuales (`001-prediccion-partido`, `002-explicacion-lenguaje-natural`, `003-track-record-publico`, `004-interfaz-web`) están en estado de **propuesta**, no implementados — por eso `openspec/specs/` todavía está vacío. Al completar e implementar cada uno, se archiva (`openspec archive <id>`) y sus specs delta se fusionan a `openspec/specs/<capability>/spec.md`.
- Cada `### Requirement:` de un spec delta declara qué requisitos del árbol canónico cubre, con `<!-- rf: RF-00X, RF-00Y -->` bajo el encabezado. `npm run audit:sdd` verifica que esos RF existan y que ninguno del spec canónico quede sin cubrir, de modo que los dos árboles no puedan volver a desincronizarse en silencio.
- El detalle de modelo de datos y contratos de API de cada change vive en `specs/00X-.../data-model.md` y `specs/00X-.../contracts/` (spec-kit) — el `design.md` de cada change de OpenSpec apunta ahí en vez de repetirlo.
- **Las tareas se marcan `[x]` solo en `specs/00X-.../tasks.md`.** El archivo homónimo bajo `changes/` es un stub.
- `002-explicacion-lenguaje-natural` depende de `001-prediccion-partido` (usa `Predicción.top_shap_features`); `003-track-record-publico` depende de `001` (usa `Predicción.version_modelo` y `Partido.resultado_real`).
