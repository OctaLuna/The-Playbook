# Modelo de datos: Track Record Público

**Basado en:** `specs/003-track-record-publico/spec.md` y `plan.md`

## EvaluaciónPredicción
Relación 1:1 con `Predicción` (001); solo existe para partidos con `estado = jugado`.

Se evalúan los **tres mercados probabilísticos** que el modelo predice, no solo 1X2: los tres
se verifican contra el mismo `Partido.resultado_real` y medir uno de tres mientras el producto
promete transparencia sobre su desempeño dejaba abierto el pilar 3.

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| partido_id | FK → Partido (001) | |
| prediccion_id | FK → Predicción (001) | único |
| acierto_1x2 | boolean | El resultado más probable predicho coincidió con el real |
| acierto_over_under_2_5 | boolean | El lado más probable (over/under) coincidió con los goles totales reales |
| acierto_btts | boolean | El lado más probable (sí/no) coincidió con si ambos equipos anotaron |
| brier_1x2 / brier_over_under_2_5 / brier_btts | float | Aporte de este partido al Brier de cada mercado |
| log_loss_1x2 / log_loss_over_under_2_5 / log_loss_btts | float | Aporte al log-loss de cada mercado |
| tiene_cuota_mercado | boolean | false si no había `CuotaMercado` para este partido (caso límite resuelto) |
| log_loss_mercado_1x2 | float, nullable | Solo si `tiene_cuota_mercado = true`. El baseline de mercado se compara únicamente en 1X2: es el único mercado con cuota implícita disponible en las fuentes históricas (sección 6.2) |
| version_modelo | string | Copiado de `Predicción.version_modelo` al evaluar. Congelarlo aquí es lo que permite distinguir versiones cuando hay un reentrenamiento a mitad de ventana |
| evaluado_en | datetime | |

## TrackRecordAgregado
Tabla cacheada, recalculada por el job diario de Celery (RF-008).

Una fila por combinación de **(liga, mercado)**: el panel muestra el desempeño de cada mercado
por separado, y un agregado que mezclara los tres no sería interpretable.

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| liga | enum, nullable | `null` = agregado global; valor = agregado filtrado por liga (RF-007) |
| mercado | enum (1x2, over_under_2_5, btts) | Mercado al que corresponde esta fila |
| ventana_n | int | 50 por defecto (RF-006) |
| porcentaje_aciertos | float | |
| brier_promedio | float | |
| log_loss_promedio | float | |
| log_loss_mercado_promedio | float, nullable | Solo en la fila `mercado = 1x2`, y solo sobre partidos con `tiene_cuota_mercado = true` |
| n_partidos_incluidos | int | Tamaño real de la muestra; puede ser menor que `ventana_n` (RF-009) |
| versiones_modelo | array de string | Versiones presentes en la ventana. Si tiene más de un elemento, el panel lo indica en vez de presentar la serie como continua |
| calculado_en | datetime | |

## CuotaMercado
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| partido_id | FK → Partido (001) | |
| prob_implicita_local / empate / visitante | float | Derivada de la cuota, **nunca la cuota cruda** — así el modelo de datos no puede alimentar un comparador de casas de apuestas (Artículo V) |
| fuente | enum (football_data, kaggle, operativa) | |

Un partido puede tener una fila **por fuente**, no una sola: las fuentes históricas y la
operativa se solapan. Para el baseline se usa una y solo una, con esta precedencia:
`football_data` → `kaggle` → `operativa`. Las históricas van primero porque son las que se
usaron para entrenar y validar, y mezclar proveedores dentro de una misma ventana haría el
baseline incomparable consigo mismo.

### Fuente de las cuotas y fórmula de normalización

Football-Data.co.uk trae las columnas de cuotas de Bet365 al cierre: `B365H`, `B365D`, `B365A`
(local, empate, visitante). Son las **únicas** columnas de ese CSV con las que trabaja esta
tabla — `specs/001-prediccion-partido/ml-design.md` §1 documenta el resto del mapeo del mismo
CSV, y ahí se marca explícitamente que estas tres columnas nunca llegan al feature set de
entrenamiento (Artículo V).

**Normalización de cuota a probabilidad implícita**, con descuento del margen de la casa
(*overround*):

```
p_local_bruta    = 1 / B365H
p_empate_bruta   = 1 / B365D
p_visitante_bruta = 1 / B365A

margen = p_local_bruta + p_empate_bruta + p_visitante_bruta   # > 1.0, es el margen de la casa

prob_implicita_local     = p_local_bruta / margen
prob_implicita_empate    = p_empate_bruta / margen
prob_implicita_visitante = p_visitante_bruta / margen
```

Sin este descuento las tres probabilidades sumarían más de 1.0 (esa es la fuente del margen de
la casa) y no serían comparables por log-loss contra las probabilidades del modelo, que sí
suman 1.0 por construcción (CHECK de `Predicción` en `specs/001-prediccion-partido/data-model.md`).

Cuando `fuente = operativa`, la cuota viene de API-Football en vez del CSV; el campo que expone
esa fuente para 1X2 tiene el mismo significado (cuota decimal) y se normaliza con la misma
fórmula.

## Relaciones
```
Predicción (001) (1) ── (1) EvaluaciónPredicción (solo si Partido.estado = jugado)
Partido (001)    (1) ──< CuotaMercado (0..N, una por fuente)
EvaluaciónPredicción (N) ──> TrackRecordAgregado (agregado, no FK estricta — se recalcula, no se referencia fila a fila)
```

## Índices y restricciones

| Tabla | Restricción | Por qué |
|---|---|---|
| `EvaluaciónPredicción` | `unique(prediccion_id)` | La relación es 1:1. Sin esto, un job diario que se ejecute dos veces duplicaría la evaluación y sesgaría el agregado |
| `EvaluaciónPredicción` | índice sobre `(version_modelo, evaluado_en)` | Consulta de la ventana distinguiendo versiones |
| `TrackRecordAgregado` | `unique(liga, mercado, ventana_n)` | Una sola fila vigente por combinación; el job la reemplaza, no la acumula |
| `CuotaMercado` | `unique(partido_id, fuente)` | Impide dos cuotas de la misma fuente para el mismo partido |
| `CuotaMercado` | índice sobre `partido_id` | Lookup al construir el baseline |
