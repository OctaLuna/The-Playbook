# Modelo de datos: Predicción de Partido

**Basado en:** `specs/001-prediccion-partido/spec.md` y `plan.md`

## Partido
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| liga | enum (premier_league, laliga, serie_a, bundesliga, ligue_1) | Alcance MVP fijo a 5 ligas (RF-008) |
| equipo_local_id | FK → Equipo | |
| equipo_visitante_id | FK → Equipo | |
| fecha_kickoff | datetime (UTC) | |
| estado | enum (programado, jugado, pospuesto, cancelado) | "pospuesto/cancelado" se marca visualmente, no se oculta (caso límite resuelto en Clarify) |
| resultado_real | struct opcional (goles_local, goles_visitante) | Solo se llena cuando estado = jugado; también lo consume 003-track-record-publico |

## Equipo
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| nombre | string | |
| liga | enum | |
| tiene_historial_suficiente | boolean (derivado) | Dispara el aviso de baja confiabilidad de la Historia 1 |

## Predicción
Relación 1:1 con `Partido` (una predicción vigente por partido; si el partido se reprograma, se conserva la predicción original — no se regenera).

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| partido_id | FK → Partido | único |
| prob_local / prob_empate / prob_visitante | float (suman 1.0) | 1X2. Se guardan las tres porque ninguna se deriva trivialmente de las otras dos sin arrastrar error de redondeo |
| prob_over_2_5 | float | Única línea O/U soportada en el MVP. `prob_under_2_5` **no se persiste**: es `1 - prob_over_2_5`, y guardar ambas permite que se desincronicen (Artículo VIII, una sola representación). El contrato sí devuelve las dos, calculadas en el schema Pydantic |
| prob_btts_si | float | `prob_btts_no` tampoco se persiste, por la misma razón |
| xg_local / xg_visitante | float | Calculado por el modelo, no histórico |
| nivel_confianza | enum (alta, media, baja) | Baja por defecto si no hay calibración suficiente (Historia 4) |
| head_to_head_disponible | boolean | Alimenta el aviso visual del caso límite de head-to-head |
| top_shap_features | JSON (campo interno) | Top-N features/valores SHAP de XGBoost — no se expone en la API pública por defecto; lo consume 002-explicacion-lenguaje-natural vía `backend/app/services/` |
| version_modelo | string | Referencia a la versión registrada en MLflow (sección 6.4); reutilizada por 003 para distinguir versiones en el track record |
| generado_en | datetime | |

## Calibración histórica
Tabla de lookup independiente, recalculada por el job de backtesting (sección 6.5), no asociada a un partido específico.

| Campo | Tipo | Notas |
|---|---|---|
| mercado | enum (1x2, over_under_2_5, btts) | |
| rango_probabilidad_min / max | float | Bucket de probabilidad, ej. [0.50, 0.60) |
| precision_empirica | float | % de aciertos observado en backtesting para ese bucket |
| n_observaciones | int | Si es menor al umbral mínimo, el badge cae a "baja" por defecto. Algoritmo del bucket, fórmula de `precision_empirica` y el default del umbral (`30`) están en `ml-design.md` §6 — aquí solo el campo |
| version_modelo | string | |

## Campos derivados (no se persisten)

Se calculan en `backend/app/services/predictions_service.py` y solo existen en la respuesta de
la API. Se documentan aquí porque aparecen en `contracts/matches-api.md` y buscarlos como
columna llevaría a añadirlos a una tabla donde no deben estar.

| Campo del contrato | Se deriva de | Regla |
|---|---|---|
| `low_data_warning` | `Equipo.tiene_historial_suficiente` de ambos equipos | `true` si cualquiera de los dos no tiene historial suficiente (RF-010) |
| `over_under_2_5.under` | `Predicción.prob_over_2_5` | `1 - prob_over_2_5` |
| `btts.no` | `Predicción.prob_btts_si` | `1 - prob_btts_si` |
| `has_prediction` | Existencia de la `Predicción` del partido | Usado en el listado de próximos partidos |

## Relaciones
```
Equipo (1) ──< Partido (N, como local o visitante)
Partido (1) ── (1) Predicción
Predicción (N) ──> Calibración histórica (lookup por mercado + rango, no FK estricta)
```

## Índices y restricciones

| Tabla | Restricción | Por qué |
|---|---|---|
| `Partido` | índice compuesto `(fecha_kickoff, estado)` | Es **la** query del sistema: los partidos que entran en la ventana de 24 h previas al kickoff y siguen programados (RF-007). Sin el índice, el job de Celery hace un recorrido completo en cada ejecución |
| `Partido` | índice sobre `liga` | Filtro del listado y del track record (RF-007 de 003) |
| `Predicción` | `unique(partido_id)` | La relación es 1:1 y el data-model ya lo declara. Sin la restricción, un job reejecutado generaría una segunda predicción y `GET /prediction` devolvería una arbitraria |
| `Predicción` | CHECK `prob_local + prob_empate + prob_visitante` ≈ 1.0 (tolerancia 1e-6) | RF-001 lo exige y el escenario 1 de la Historia 1 lo comprueba. Mejor que falle al insertar que al servir |
| `Predicción` | CHECK de que toda probabilidad esté en `[0, 1]` | Atrapa un error de la capa de ensamble en el borde de la base de datos |
| `Calibración histórica` | `unique(mercado, rango_probabilidad_min, version_modelo)` | Un solo bucket vigente por mercado y versión; el backtesting lo reemplaza, no lo acumula |
| `Equipo` | `unique(nombre, liga)` | Evita duplicar equipos al cargar varias fuentes de datos históricos (sección 6.3) |
