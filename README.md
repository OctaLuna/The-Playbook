# The Playbook

Sistema inteligente que **predice** resultados de fútbol de las cinco grandes ligas,
**explica en lenguaje natural** qué datos reales respaldan cada predicción, y **publica su
propio historial de aciertos** para que cualquiera pueda auditarlo.

> Para aficionados y analistas amateur que quieren entender —no solo adivinar— qué puede
> pasar en un partido.

**Equipo:** The-Playbook · **Materia:** Taller de Sistemas Inteligentes

## Los 3 pilares

1. **Predicción** — 1X2, Over/Under 2.5, BTTS y xG por equipo, con un nivel de confianza
   *calibrado contra la precisión histórica real* del modelo, no contra la forma de la
   distribución.
2. **Explicación honesta** — un LLM justifica cada predicción citando noticias, forma y
   head-to-head, con una garantía dura: **nunca usa evidencia publicada después del
   kickoff** del partido que predice.
3. **Transparencia** — panel público con el desempeño real del modelo, comparado contra el
   baseline implícito del mercado, auditable partido a partido.

## Estado

🚧 **Fase de especificación.** No hay código todavía. Las tres features del MVP están
completamente especificadas y planificadas; el siguiente paso es escribir las pruebas de
contrato de `001-prediccion-partido` y verlas fallar.

| Feature | Estado |
|---|---|
| [001 — Predicción de partido](specs/001-prediccion-partido/spec.md) | Especificado |
| [002 — Explicación en lenguaje natural](specs/002-explicacion-lenguaje-natural/spec.md) | Especificado |
| [003 — Track record público](specs/003-track-record-publico/spec.md) | Especificado |
| [004 — Interfaz web](specs/004-interfaz-web/spec.md) | Especificado |

El primer trabajo es el **Grupo 0** de [`001/tasks.md`](specs/001-prediccion-partido/tasks.md):
levantar el stack (docker-compose, app FastAPI, Alembic, fixtures) para que las pruebas de
contrato se puedan escribir.

## Cómo está organizado

Este repositorio sigue **Spec-Driven Development**: nada se implementa sin una
especificación, un plan y una lista de tareas trazable.

| Ruta | Qué contiene |
|---|---|
| [`memory/constitution.md`](memory/constitution.md) | Los 9 principios no negociables. **Empieza aquí** |
| [`specs/00X-*/`](specs/) | Fuente canónica: spec, plan, modelo de datos, contratos, quickstart y tareas |
| [`docs/project_spec.md`](docs/project_spec.md) | Decisiones de producto, stack y arquitectura |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |
| [`openspec/`](openspec/) | Capa de propuesta (`proposal.md` + `design.md`) |
| [`CLAUDE.md`](CLAUDE.md) | Guía para agentes de IA: precedencia de fuentes, rutas canónicas, prohibiciones |
| [`docs/mapa-archivos-the-playbook.md`](docs/mapa-archivos-the-playbook.md) | Qué hace cada archivo del repo |

## Stack

**Backend** FastAPI (Python 3.12) · SQLAlchemy 2.0 async · PostgreSQL 16 + pgvector · Redis · Celery
**ML** statsmodels (Dixon-Coles) + XGBoost por ensamble ponderado · SHAP · MLflow
**RAG/LLM** LangChain + AWS Bedrock (Claude vía Converse API) · Titan Text Embeddings V2
**Frontend** Next.js 15 + TypeScript · Tailwind + shadcn/ui · TanStack Query · Recharts

Justificación de cada elección: [`docs/project_spec.md`](docs/project_spec.md) §5.

## Desarrollo

```bash
npm run audit:sdd    # valida referencias y trazabilidad RF↔tarea de la documentación
```

El resto de comandos y el protocolo test-first están en [`CLAUDE.md`](CLAUDE.md).
Antes de abrir un PR, revisa la [Definition of Done](docs/team-charter.md#6-definition-of-done-dod-inicial).
