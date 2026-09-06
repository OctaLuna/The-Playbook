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
| prob_local / prob_empate / prob_visitante | float (suman 1.0) | 1X2 |
| prob_over_2_5 / prob_under_2_5 | float | Única línea O/U soportada en el MVP |
| prob_btts_si / prob_btts_no | float | |
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
| n_observaciones | int | Si es menor a un umbral mínimo (a fijar junto al criterio de reentrenamiento, sección 6.5), el badge cae a "baja" por defecto |
| version_modelo | string | |

## Relaciones
```
Equipo (1) ──< Partido (N, como local o visitante)
Partido (1) ── (1) Predicción
Predicción (N) ──> Calibración histórica (lookup por mercado + rango, no FK estricta)
```
