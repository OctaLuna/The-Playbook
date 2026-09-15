# Sprint 5 — Integración de 001, cierre de 002, arranque de 003

**Semanas:** 9-10 · **Objetivo:** `001` y `002` quedan **Done** según la DoD del equipo
(`docs/team-charter.md` §6). El ensamble está probado contra los casos límite reales.

## Por persona

| Persona | Tareas |
|---|---|
| **Rodrigo** | `001` Grupo 4: `T017`-`T022` (pruebas de integración de las 4 historias y los casos límite). Grupo 5: `T023`, `T024` (404 documentados, `quickstart.md`). **`001` queda Done al cierre del sprint** |
| **Leandro** | `003` Grupo 1-2 completo si no arrancó en el Sprint 4: `T001`-`T003` (contratos, incl. la prueba negativa anti-cuotas) y `T004`-`T008` (modelos, migración, schemas) |
| **Einar** | `002` Grupo 4: `T019`-`T022` (evidencia real, fallback honesto, preguntas de seguimiento, no-contradicción con la predicción — la prueba `T021b` es constitucionalmente sensible, no se apura). Grupo 5: `T023`-`T025`. **`002` queda Done al cierre del sprint** |
| **Carol** | `004` resto de Grupo 4: `T020`-`T023` (aviso de datos insuficientes, bloque de explicación con evidencia enlazable —ahora sí con `002` disponible—, preguntas de seguimiento, estado del partido) |
| **Octavio** | Sprint Review con demo de `002`: una explicación real, citando evidencia real, con enlace verificable. Retro breve sobre cómo fue el sprint más pesado (Sprint 3-4) para ajustar el ritmo de lo que queda |

## Puede adelantarse sin esperar

Leandro puede escribir todo el Grupo 1-2 de `003` sin esperar a nadie — los contratos y el
esquema de `003` no dependen de que `001` esté "Done", solo de que `Predicción.version_modelo`
y `Partido.resultado_real` existan como columnas, que ya es el caso desde el Sprint 2.

## Riesgos y dependencias

- El bloque de explicación de Carol (`T020`-`T021`) depende de que el contrato de `002` responda
  de verdad, no de un mock — coordinar con Einar el momento exacto en que `T017` (routers de
  `002`) queda estable dentro del sprint.
- `T021b` de `002` (verificar que la explicación no contradice la predicción numérica) es de las
  pruebas más delicadas del proyecto — no comprimirla al final del sprint por falta de tiempo.

## Definition of Sprint Done

- `001` cumple la DoD completa de `docs/team-charter.md` §6, incluida la adicional de ML (split
  cronológico verificado).
- `002` cumple la misma DoD, incluida la adicional de RAG (filtro temporal respetado).
- La ficha del partido en `004` muestra las 4 señales **y** la explicación con evidencia
  enlazable, de punta a punta.
- El esquema de `003` migra sin error.
