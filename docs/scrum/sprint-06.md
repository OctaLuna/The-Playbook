# Sprint 6 — Cerrar 003, avanzar el panel de track record

**Semanas:** 11-12 · **Objetivo:** `003` queda **Done**. El panel público de `004` muestra
datos reales de desempeño. Rodrigo y Einar, libres de sus features, refuerzan al resto.

## Por persona

| Persona | Tareas |
|---|---|
| **Leandro** | El sprint más cargado de `003`: Grupo 3 (`T009`-`T012`, servicio + baseline de mercado + worker diario + routers), Grupo 4 (`T013`-`T019`, incluido el caso de reentrenamiento a mitad de ventana), Grupo 5 (`T020`-`T022`). **`003` queda Done al cierre del sprint** |
| **Rodrigo** | Libre de `001` desde el Sprint 5. Este sprint: revisor de PR de Leandro en `003` (segundo par de ojos, especialmente en el worker diario y el baseline de mercado), activa el job `frontend` de `.github/workflows/ci.yml` (hoy desactivado con `if: false`), prepara `infra/` para datos reales de las 5 ligas |
| **Einar** | Libre de `002` desde el Sprint 5. QA de RAG: la prueba manual de groundedness (`T022` de `002`, si no se completó), y soporte a Carol en la integración del bloque de explicación si aparece fricción |
| **Carol** | `004` Grupo 5 completo: `T024`-`T028` (panel de track record con los 3 mercados por separado). **Depende de que Leandro tenga al menos el Grupo 3 de `003` listo** — coordinar el momento exacto a inicio de sprint |
| **Octavio** | Es el sprint más cargado para una sola persona (Leandro) del proyecto — vigilar de cerca, y decidir temprano si Rodrigo pasa de "revisor" a "pairing activo" si hace falta |

## Puede adelantarse sin esperar

Rodrigo y Einar no tienen tareas propias de `tasks.md` este sprint — su trabajo es de soporte,
explícitamente para no dejar a Leandro solo en el sprint más pesado de `003`.

## Riesgos y dependencias

- **Concentración de riesgo en una persona.** `003` completo (17 tareas: Grupo 3-5) en un solo
  sprint es ambicioso incluso habiendo arrancado Grupo 1-2 en el Sprint 5. Si a mitad de sprint
  se ve que no cierra, mejor recortar a "Grupo 3-4 completo, Grupo 5 se corre al Sprint 7" que
  forzar el cierre y sacrificar las pruebas de integración.
- El panel de Carol no puede empezar en serio hasta que el Grupo 3 de `003` (servicio + routers)
  esté estable — si Leandro prioriza Grupo 4-5 primero por error, Carol se queda sin nada que
  consumir. El orden dentro del sprint importa: Grupo 3 primero.

## Definition of Sprint Done

- `003` cumple la DoD completa de `docs/team-charter.md` §6.
- `GET /api/track-record` devuelve los 3 mercados con datos reales de partidos ya jugados.
- El panel de `004` muestra el desempeño real, no datos de ejemplo.
- El job `frontend` de CI ya no está desactivado.
