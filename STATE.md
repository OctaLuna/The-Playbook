# STATE — The Playbook (actualizado 2026-11-17)

Para Rodrigo (Product Owner / Scrum Master). Verificado contra git, `gh pr` y CI; no contra ClickUp
(fuente oficial de avance según `docs/team-charter.md` §2). Repo público: aquí no va nada sensible.

## Estado
Rama `develop`, **Sprint 6** en curso (003 + panel de track record). Sprints 7 y 8 pendientes.

| Feature | Dueño | Situación |
|---|---|---|
| 001 predicción | Octavio + Leandro | Done. Abiertos: #32 (línea base solo con partidos jugados) y #37 (tabla de alias de 20 clubes) |
| 002 explicación | Einar | 26 hechas / 2 abiertas: T004 (Red, a propósito) y **T022** (ver abajo). Abiertos: #31 (commit de la explicación) y #38 (log de la guarda, apilado sobre #31) |
| 003 track record | Leandro | **#29** con Grupos 3-5 (25/25). CI Backend rojo: falta `flush` en `recalcular_track_record_agregado` (arreglo de 3 líneas y diagnóstico comentados en el PR; Leandro sin responder). Bloquea a Carol (T024-T028) |
| 004 web | Carol | 4/30 marcadas. 55 pruebas pasan, pero las de T020-T023 definen su propia función y no ejercitan la UI real: no marcar sin verificar en el navegador. Falta accesibilidad AA (T029-T034), única fecha dura del Sprint 7; sin PR visible |

## PRs abiertos (esperan review de Octavio, ya avisado)
#29 Leandro · #30 guion Sprint 8 · #31, #32 fixes · #33 roles + STATE · #34 hook `isolation-guard` que `develop` ya
referenciaba pero no existía, + revisor temporal + skills · #35 guion/láminas EC2 · #36 PRODUCT.md · #37 alias · #38.
Orden sugerido: #31, #32, #34, #37. #31/#38 tocan archivos de Einar; #32/#37 están en `backend/ml/`.

## T022 (002): dueño Einar · N=10 y firma de la revisión: Rodrigo
- Primera ejecución (26/10): 1 partido, texto = plantilla de seguridad, revisor "Claude Code" → insuficiente. Sigue `[ ]`.
- La guarda `_contains_prediction_contradiction` descarta **cualquier** frase de resultado (aunque esté negada) y **cualquier**
  porcentaje ajeno al modelo (aunque venga de una noticia), y no dejaba rastro. #38 registra motivo y texto original
  (WARNING); la lógica no cambió. Afinarla es decisión del equipo/Einar.
- Muestra = 10 partidos de **demostración** (emparejamientos sintéticos de equipos reales). El calendario real no sirve: el
  loader exige goles y solo se predice a <24 h. El registro debe decirlo.
- **BLOQUEADO:** AWS rechaza las credenciales de `backend/.env` (`UnrecognizedClientException: security token invalid`);
  embeddings (Titan) y generación (`us.anthropic.claude-sonnet-4-6`) usan Bedrock. Salidas: renovar claves (más
  `AWS_SESSION_TOKEN` si empiezan con `ASIA`; probar con `aws sts get-caller-identity`) o autorizar explícitamente el perfil de `~/.aws`.
- Hecho en local (worktree `..\pb-t022` = rama del #38 + `equipo_alias.csv` del #37): compose del proyecto arriba (volumen
  `postgres_data`), `E0.csv` cargado (100 partidos), 10 partidos creados con `C:\Users\Lenovo\Downloads\crear_muestra_t022.py`
  (equipos por orden alfabético en parejas, Brighton de visitante, uuid5), 10 predicciones generadas.
- **Kickoff de la muestra: 18/11 11:34-12:19 UTC.** Si se retoma después, recrear los partidos y regenerar predicciones
  (la ventana de ingesta y predicción es de 24 h).
- Falta: ingesta con `NEWS_RSS_FEEDS` (19 feeds `theguardian.com/football/<slug>/rss`: arsenal, aston-villa, bournemouth,
  brentford, chelsea, everton, fulham, liverpool, manchester-united, sunderland, tottenham-hotspur, coventry, manchestercity,
  newcastleunited, nottinghamforest, crystalpalace, leedsunited, hullcity, ipswichtown; Brighton no tiene) → `reindex_rag()` →
  10 × `GET /api/matches/{id}/explanation` → paquete (JSON, evidencia, SHAP, WARNING de la guarda) → revisión humana con la tabla de
  `groundedness-review.md`. Marcar `[x]` solo después.

## Problemas conocidos
- `Equipo.nombre` guarda el slug (`manchester-united`) y la API lo devuelve como nombre: verificar si la UI lo formatea.
- Al generar predicciones salen avisos de `sklearn` ("y_prob values do not sum to one"): no investigado (`backend/ml/`, Leandro).
- Pruebas del frontend: solo pasan desde PowerShell con `C:\` en mayúscula (en `c:` fallan por la unidad en minúscula).
- Limpieza local pendiente: 5 volúmenes Docker anónimos (`docker volume prune`), contenedores del compose y worktree `pb-t022` activos.
- Informes `arquitectura-y-seguridad` y `estado-backlog` quedan locales a propósito (riesgos sin resolver; repo público).
  graphify y `caveman-mode` no se versionan. `CLAUDE.md` §8 sigue desactualizado.

## Próximo objetivo
Destrabar #29 y mergear los PR. Reanudar T022 cuando haya credenciales AWS válidas. Seguimiento a Carol por Sprint 7.

## Decisiones
- Solo `specs/*/tasks.md` se marca `[x]`. T022 y 004 T020-T023 siguen abiertas hasta tener evidencia.
- Reparto vigente (26/10): Rodrigo PO/SM sin track técnico; Octavio Backend-core. El charter aún dice otra cosa.
- T022 con N=10, fixtures por script local (no en el repo, para no sumar código sin tarea; si se repite cada sprint, crear
  tarea en 002 Grupo 4) y firma humana de Rodrigo.
- La tabla de alias de demo conserva "Manchester Utd" sin alias a propósito (el notebook lo usa para mostrar la inconsistencia).
