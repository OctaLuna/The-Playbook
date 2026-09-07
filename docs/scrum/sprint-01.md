# Sprint 1 — Arrancar el stack y lo que no depende de él

**Semanas:** 1-2 · **Objetivo:** el stack local levanta con un comando, y cada track adelantó
lo que no necesitaba esperar a nadie.

## Por persona

| Persona | Tareas (ver `specs/00X-*/tasks.md` para el detalle) |
|---|---|
| **Rodrigo** | `001` Grupo 0 completo: `B01`-`B09`. Es el bloqueante del sprint — todo lo demás del proyecto depende de que esto termine |
| **Leandro** | Sin tareas de `tasks.md` todavía (`T012a` necesita `B01` fusionado primero). Preparación: descargar y explorar el CSV de Football-Data.co.uk, construir la tabla de alias de equipo de `ml-design.md` §1, leer `ml-design.md` completo |
| **Einar** | `002` — `T010`, `T011`: chunking y sanitización. Son funciones puras, no tocan base de datos ni la app — se pueden escribir y testear sin esperar al Grupo 0 |
| **Carol** | `004` Grupo 0 completo: `T001`-`T004` (proyecto Next.js, lint/typecheck, shadcn+TanStack, config). No depende del backend. Además: **configurar el tablero de ClickUp** con las 126 tareas de las 4 features, mapeadas desde `specs/00X-*/tasks.md` |
| **Octavio** | Sprint Planning inicial, fijar la Definition of Ready del equipo, verificar a mitad de semana que `B01`-`B09` avanza — es la única dependencia real de todo el sprint 2 |

## Puede adelantarse sin esperar

Einar y Carol no dependen del Grupo 0 en absoluto este sprint — su trabajo de esta quincena es
100% independiente del de Rodrigo. Solo Leandro está genuinamente bloqueado para escribir
código (no para prepararse).

## Riesgos y dependencias

- **Riesgo único del sprint:** si `B01`-`B09` no cierra en las 2 semanas, el Sprint 2 completo
  de Rodrigo y Leandro se retrasa. Es la razón por la que Octavio lo vigila explícitamente.
- `T012a` (Leandro) y `T004b` (Einar) tocan `backend/pyproject.toml`, el mismo archivo que crea
  `B01`. Ninguno de los dos debe tocarlo este sprint — esperan a que `B01` esté fusionado.

## Definition of Sprint Done

- `docker compose -f infra/docker-compose.yml up -d` levanta Postgres+pgvector y Redis.
- `cd backend && pytest` corre (los guardianes constitucionales en verde, los contratos de `001`
  en rojo — es la fase Red esperada).
- `GET /health` responde 200.
- `cd frontend && npm run dev` levanta la app en blanco sin errores de consola.
- El tablero de ClickUp existe con las 126 tareas cargadas y asignadas por persona.
