# Sprint 2 — Contratos, esquema y tipos

**Semanas:** 3-4 · **Objetivo:** el esquema de `001` existe y migra; los otros tres tracks
tienen su propia base de contratos/tipos lista, sin necesitar todavía datos reales.

## Por persona

| Persona | Tareas |
|---|---|
| **Rodrigo** | `001` Grupo 1: `T001`-`T005` (pruebas de contrato en rojo). Grupo 2: `T006`-`T011` (modelos SQLAlchemy, migración inicial, schemas). **Prioridad dentro del sprint: `T006`/`T007` (Partido/Equipo) primero** — son lo que desbloquea a Leandro |
| **Leandro** | `T012a` (dependencias de ML — ahora sí, con `B01` ya fusionado) en cuanto empieza el sprint. `T012b` (`backend/ml/data/`, carga histórica) en cuanto Rodrigo fusione `T006`/`T007` — probablemente mitad de sprint, no el día 1 |
| **Einar** | `002` Grupo 1: `T001`-`T004`, empezando por `T001` (filtro temporal contra pgvector real — **la prueba más crítica del feature**, Artículo IV). Grupo 2: `T004b` (deps RAG, después de `B01`), `T005`-`T009` (modelos, migración, schemas) |
| **Carol** | `004` Grupo 1: `T005`-`T009` (tipos derivados de los 3 contratos de backend + pruebas de que parsean los JSON de ejemplo). No depende de que el backend esté implementado — los contratos ya están congelados desde la ronda de auditoría anterior |
| **Octavio** | Sprint Review del Sprint 1, Sprint Planning de este. Seguimiento diario informal (no ceremonia formal) de cuándo Rodrigo fusiona `T006`/`T007`, para avisar a Leandro apenas pase |

## Puede adelantarse sin esperar

Carol sigue sin ninguna dependencia real este sprint. Einar puede completar todo `T001`-`T004`
sin esperar nada de Rodrigo (solo necesita el Grupo 0 ya fusionado desde Sprint 1).

## Riesgos y dependencias

- Leandro depende de una fecha intra-sprint, no del sprint completo: si Rodrigo deja `T006`/`T007`
  para el final de las 2 semanas, Leandro pierde casi todo el sprint. Rodrigo debería priorizar
  esos dos modelos sobre `T008`/`T009` si el tiempo aprieta.
- `T012a` y `T004b` tocan `backend/pyproject.toml` — coordinar el orden de los dos PRs (no en
  paralelo) para evitar un conflicto de merge trivial pero evitable.

## Definition of Sprint Done

- Las 4 pruebas de contrato de `001` existen y fallan (fase Red confirmada, `T005`).
- La migración inicial de `001` aplica sin error sobre el Postgres del compose.
- El test de integración del filtro temporal de `002` (`T001`) existe — puede seguir en rojo,
  pero debe existir y estar escrito contra pgvector real, no un mock.
- Los tipos de `004` parsean sin error los tres JSON de ejemplo de los contratos.
