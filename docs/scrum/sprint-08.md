# Sprint 8 — Regresión, evidencia y entrega

**Semanas:** 15-16 · **Objetivo:** el proyecto está listo para la defensa académica. Nada
nuevo se construye este sprint — se verifica, se documenta la evidencia, y se ensaya.

## Por persona

Sin división por track — el equipo completo trabaja sobre el mismo objetivo esta quincena.

| Quién | Qué |
|---|---|
| **Los 5** | Ejecutar manualmente los 4 `quickstart.md` (uno por feature) de punta a punta y registrar el resultado |
| **Rodrigo** | Verificar que `docker compose up` + `alembic upgrade head` reproduce el entorno completo desde cero, sin pasos manuales no documentados |
| **Leandro** | Preparar la evidencia de MLflow (pesos del ensamble, métricas de backtesting) y el `docs/adr/` correspondiente como material de defensa académica |
| **Einar** | Muestra final de groundedness/faithfulness de RAG documentada y reproducible |
| **Carol** | Pulido final de UI encontrado durante la regresión; cierre del tablero de ClickUp con la evidencia de las 126 tareas |
| **Octavio** | Ensayo de la demo de defensa, Sprint Review final, y Retro de todo el proyecto (qué funcionó del reparto por tracks, qué se ajustaría en una próxima iteración) |

## Riesgos y dependencias

- Este sprint no tiene tareas nuevas de `tasks.md` — su riesgo es de otro tipo: descubrir en
  regresión un defecto que obliga a reabrir una tarea que se había dado por Done. Si pasa,
  se reporta y se resuelve con la misma prioridad que un bloqueo (protocolo de
  `docs/team-charter.md` §4), no se ignora por estar "fuera de sprint".

## Definition of Sprint Done

- Los 4 `quickstart.md` ejecutados manualmente sin fallos, con evidencia enlazada en ClickUp.
- `npm run audit:sdd` en 0 errores, 0 avisos.
- `cd backend && pytest -m "not pendiente_implementacion"` en verde.
- Evidencia de MLflow y ADRs listos para la defensa.
- Demo ensayada de punta a punta.
