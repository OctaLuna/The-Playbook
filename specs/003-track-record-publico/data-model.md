# Modelo de datos: Track Record Público

**Basado en:** `specs/003-track-record-publico/spec.md` y `plan.md`

## EvaluaciónPredicción
Relación 1:1 con `Predicción` (001); solo existe para partidos con `estado = jugado`.

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| partido_id | FK → Partido (001) | |
| prediccion_id | FK → Predicción (001) | |
| acierto_1x2 | boolean | Si el resultado más probable predicho coincidió con el real |
| brier_contribution | float | Aporte de este partido al Brier score agregado |
| log_loss_contribution | float | Aporte de este partido al log-loss agregado del modelo |
| tiene_cuota_mercado | boolean | false si no había `CuotaMercado` para este partido (caso límite resuelto) |
| log_loss_mercado_contribution | float, nullable | Solo si `tiene_cuota_mercado = true` |
| version_modelo | string | Copiado de `Predicción.version_modelo` al momento de evaluar (caso límite de reentrenamiento) |
| evaluado_en | datetime | |

## TrackRecordAgregado
Tabla cacheada, recalculada por el job diario de Celery (Historia 1, escenario 2).

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| liga | enum, nullable | `null` = agregado global; valor = agregado filtrado por liga (RF-007) |
| ventana_n | int | 50 por defecto (RF-006) |
| porcentaje_aciertos | float | |
| brier_promedio | float | |
| log_loss_promedio | float | |
| log_loss_mercado_promedio | float, nullable | Solo considera partidos con `tiene_cuota_mercado = true` |
| n_partidos_incluidos | int | |
| calculado_en | datetime | |

## CuotaMercado
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| partido_id | FK → Partido (001) | |
| prob_implicita_local / empate / visitante | float | Derivada de la cuota, no la cuota cruda |
| fuente | enum (football_data, kaggle, operativa) | |

## Relaciones
```
Predicción (001) (1) ── (1) EvaluaciónPredicción (solo si Partido.estado = jugado)
Partido (001) (1) ── (0..1) CuotaMercado
EvaluaciónPredicción (N) ──> TrackRecordAgregado (agregado, no FK estricta — se recalcula, no se referencia fila a fila)
```
