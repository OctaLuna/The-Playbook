# Scrum — The Playbook

Plan de ejecución del MVP en 8 sprints de 2 semanas (16 semanas), sobre las 126 tareas ya
trazables de `specs/00X-*/tasks.md`. El Sprint 0 (organización) ya ocurrió y no se planifica
aquí — este es el trabajo de construcción, del Sprint 1 al 8.

## Cómo leer esta carpeta

| Archivo | Qué contiene |
|---|---|
| [`equipo-y-tracks.md`](equipo-y-tracks.md) | Quién lleva qué track, por qué, y los límites de archivo entre personas — léelo primero |
| [`product-backlog.md`](product-backlog.md) | Las 126 tareas agrupadas por persona, con sus IDs de `specs/00X-*/tasks.md` |
| `sprint-01.md` … `sprint-08.md` | Un archivo por sprint: objetivo, tareas por persona, qué se puede adelantar, riesgos, Definition of Sprint Done |

**Regla de fuente única:** esta carpeta dice **quién** hace **qué** y **cuándo**. Nunca dice
**qué es** una tarea — eso vive solo en `specs/00X-*/tasks.md`, que sigue siendo lo único que
se marca `[x]`. Si un sprint necesita describir de nuevo una tarea en vez de referenciar su ID,
es una señal de que se está duplicando lo que ya existe — no lo hagas, enlaza el ID.

El estado real de avance ("hecho", "en progreso", "bloqueado") vive en **ClickUp**
(`docs/team-charter.md` §2: *"es la única fuente válida de qué se hizo y quién lo hizo"*), no en
estos archivos — el plan de sprints no cambia sprint a sprint salvo que el equipo replanifique.

## Metodología

**Sprints de 2 semanas.** `docs/priorizacion_casos.md` fija el taller en 18 semanas; con
Sprint 0 ya corrido, quedan 16 semanas ÷ 8 sprints = 2 semanas exactas cada uno.

**Roles:**
- **Product Owner / Scrum Master:** Octavio. Prioriza el backlog, facilita las ceremonias,
  resuelve bloqueos entre tracks. Sin sprint técnico fijo.
- **4 tracks técnicos, uno por persona:** Rodrigo (Backend-core), Leandro (ML + Track Record),
  Einar (RAG/LLM), Carol (Frontend). Ver el porqué de cada uno en `equipo-y-tracks.md`.

**Ceremonias, ajustadas a la disponibilidad real del equipo.** `docs/team-charter.md` §1
declara solo 3 franjas de 2h/semana en simultáneo (Dom/Mar/Mié) — no alcanza para una daily
tradicional de 15 minutos todos los días. En su lugar:

| Ceremonia | Cuándo | Duración |
|---|---|---|
| Sprint Planning | Primera franja sincrónica del sprint (día 1) | ~45 min |
| Check-in de avance | Segunda franja de la primera semana | ~15 min, async si no hace falta |
| Sprint Review + Retro | Última franja sincrónica del sprint (día 14) | ~45-60 min |

El resto de la coordinación es asíncrona: ClickUp para estado, WhatsApp/Teams para avisos
rápidos, GitHub Issues para bloqueos formales — exactamente el esquema que ya define
`docs/team-charter.md` §2.

## El mapa de sprints, de un vistazo

| Sprint | Objetivo | Cierra |
|---|---|---|
| 1 | Arrancar el stack y lo que no depende de él | — |
| 2 | Contratos, esquema y tipos | — |
| 3 | Núcleo matemático (Dixon-Coles, XGBoost) y de retrieval | — |
| 4 | Primera predicción real de punta a punta | — |
| 5 | Integración de 001, cierre de 002 | **001, 002** |
| 6 | Cierre de 003, panel de track record | **003** |
| 7 | Cierre del frontend, hardening cruzado | **004** |
| 8 | Regresión, evidencia, entrega | — |

**Esto es un plan de partida, no un contrato.** Scrum recalibra en cada Sprint Planning — si un
sprint se corre (el Sprint 3, el más denso técnicamente, es el candidato más probable), se
ajusta el resto en cascada y se documenta el cambio, no se fuerza la fecha original.

## Verificación de que el plan sigue vigente

```bash
npm run audit:sdd    # las tareas referenciadas aquí siguen existiendo en specs/00X-*/tasks.md
```

Si `specs/00X-*/tasks.md` cambia (una tarea se divide, se agrega una nueva), esta carpeta debe
actualizarse en el mismo PR — igual que cualquier otra documentación del repo.
