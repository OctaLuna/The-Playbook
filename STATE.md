# STATE — The Playbook (actualizado 2026-11-17)

Rol de quien lo lee: Rodrigo, Product Owner / Scrum Master. Verificado contra `specs/*/tasks.md`,
git, `gh pr` y CI; no contra ClickUp (fuente oficial de avance según `docs/team-charter.md` §2).

## Estado
Rama `develop`. Estamos en el **Sprint 6** (003 + panel de track record). Sprints 1-5 cumplidos.

| Feature | Dueño | `[x]` / pendientes | Situación |
|---|---|---|---|
| 001 predicción | Octavio + Leandro | 39 / 0 | Done |
| 002 explicación | Einar | 26 / 2 | Abiertas: T004 (Red, a propósito) y T022 (muestra real de groundedness: la primera ejecución fue 1 partido, el texto fue la plantilla de seguridad y el revisor figura como "Claude Code"; falta ampliar la muestra y revisión humana) |
| 003 track record | Leandro | 9 en `develop` / 25 de 25 en el PR #29 | **PR #29 abierto** (15-nov) con Grupos 3-5 (servicio, job Celery, router, tests, ADR 0002). CI Backend en rojo: T014 y T017 por `flush` faltante en `recalcular_track_record_agregado`. Diagnóstico y arreglo de 3 líneas comentados en el PR (verificado en local: 212 passed). Sin review aún. |
| 004 web | Carol | 4 / 30 | `frontend/` ya tiene scaffold y rutas (`partidos`, `track-record`), pero los checkboxes no reflejan eso |

## Qué supervisar (Sprints 6-8)
**Sprint 6**
- Leandro: Grupo 3 de 003 (T009-T012) **primero**; luego Grupo 4 (T013-T019, T013b, T017b) y Grupo 5. Si a mitad de sprint no cierra: recortar a Grupo 3-4 y mover el 5 al Sprint 7.
- Carol (T024-T028): depende del Grupo 3 de Leandro. Mientras, trabajar con datos de ejemplo del contrato.
- Octavio: activar el job `frontend` de `ci.yml` (hoy `if: false`), revisar PR de Leandro en <24 h, preparar `infra/` para las 5 ligas.
- Einar: libre. Apoyo a Carol con el bloque de explicación.

**Sprint 7**
- Carol: accesibilidad AA (T029-T034), **única fecha dura**. Leandro/Einar la apoyan.
- Octavio/Leandro/Einar: pagar deuda técnica; Octavio sustituye datos de prueba por datos reales.
- Tú: Sprint Review con demo lista → ficha → explicación → panel.

**Sprint 8**
- Los 5 ejecutan su quickstart y registran evidencia. Carol cierra ClickUp con las 126 tareas.
- Octavio: reproducir entorno desde cero. Leandro: evidencia MLflow + ADR. Einar: muestra de groundedness.
- Un defecto de regresión se trata como bloqueo, no como "fuera de sprint".

## Dependencias críticas
Leandro → Carol (Grupo 3 de 003 antes del panel) · Octavio → Carol (CI frontend) · Octavio → Leandro (revisión de PR) · todos → Carol (evidencia en ClickUp) · todos → tu demo.

## Problemas conocidos
- `npm test` del frontend: falla (`Cannot read properties of undefined (reading 'config')`) si se corre desde una terminal con la unidad en minúscula (`c:\...`, p. ej. Git Bash); **pasa desde PowerShell con `C:\...`** (21 archivos, 55 pruebas; lint y typecheck limpios). Causa: capitalización de la letra de unidad en Windows. OJO: las 4 pruebas "de componentes" de 004 T020-T023 (`explanation`, `follow-up`, `explanation-absence`, `match-status`) definen su propia función dentro del test y no ejercitan la UI real, así que no bastan para marcar esas tareas.
- Ramas remotas sin PR/mergear: `Octa-dev` (guion Sprint 8, ahora con PR), `pupi` (alternativa de 002 ya superada; rescatar solo `test_chunking.py`, `test_sanitizer.py`, `test_explanations_service.py`), `feature/pupi-sprint-3` (`docs/c4-diagrams.md`). Ramas `feature/001-*`/`T012*` parecen obsoletas: borrar solo con confirmación.
- Sprint 7: no hay PR de Carol para T029-T034 (accesibilidad AA, fecha dura). Sprint 8: falta muestra real de groundedness con Bedrock (T022 según Octavio; STATE decía solo T004: aclarar con Einar) y entorno Docker/Postgres reproducible.
- PR #29 bloqueado por CI rojo hasta que Leandro aplique el `flush`; bloquea a Carol (T024-T028). Sin review de Octavio pasadas >24 h.
- `tasks.md` de 004 desfasado frente al código de `frontend/`.
- `CLAUDE.md` §8 desactualizado: dice que lo siguiente es el Grupo 1 de 001.
- 25 archivos modificados sin commit en `develop` (docs/scrum, `explanations_service.py`, etc.) y varios `.png`, `dev.log`, `mlflow.log` sueltos.
- Grafo graphify con última corrida del 2026-10-26.

## Próximo objetivo
Destrabar PR #29: Leandro aplica el `flush`, CI en verde, review (Octavio) y merge a `develop`. Luego Carol sigue con T024-T028 sobre el contrato real.

## Decisiones
- `tasks.md` de `specs/` es lo único que se marca `[x]`; `docs/scrum/` solo dice quién y cuándo.
- Rodrigo sin track técnico, para tener capacidad de destrabar (ver `docs/scrum/equipo-y-tracks.md`).
