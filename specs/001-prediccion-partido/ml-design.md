# Diseño de ML: Predicción de Partido

**Basado en:** `specs/001-prediccion-partido/plan.md` y `data-model.md`
**Propósito de este archivo:** `plan.md` fija la arquitectura (qué módulo llama a cuál,
qué corre en Celery); `data-model.md` fija el esquema de base de datos. Ninguno de los dos fija
el **algoritmo**. Este archivo sí — es el que debe bastar para escribir
`backend/ml/models/dixon_coles/train.py`, `backend/ml/models/xgboost/train.py`,
`backend/ml/ensemble/predict.py` y `backend/ml/evaluation/calibration.py` sin decidir nada por
el camino.

Todo hiperparámetro de esta página tiene un valor por defecto documentado y vive en
configuración (`backend/app/core/config.py` o un YAML propio de `backend/ml/`), **nunca hardcodeado en
el código** — mismo principio que ya aplica el repo al umbral de groundedness de
`002-explicacion-lenguaje-natural` (T025).

---

## 1. Fuente de datos → esquema

**Fuente:** Football-Data.co.uk (sección 6.2 de `docs/project_spec.md`), un CSV por
temporada/liga, sin autenticación. Columnas relevantes del CSV y su mapeo:

| Columna CSV | Significado | Mapea a |
|---|---|---|
| `Date` | Fecha del partido (`dd/mm/yy` o `dd/mm/yyyy` según temporada) | `Partido.fecha_kickoff` — normalizar a UTC; el CSV no trae hora, usar 15:00 hora local de la liga como convención hasta tener el dato operativo real |
| `HomeTeam` / `AwayTeam` | Nombre del equipo tal como lo escribe Football-Data.co.uk | `Partido.equipo_local_id` / `equipo_visitante_id`, vía tabla de alias (ver abajo) |
| `FTHG` / `FTAG` | Goles finales del local / visitante (*Full Time Home/Away Goals*) | `Partido.resultado_real.goles_local` / `goles_visitante` |
| `FTR` | Resultado final: `H`/`D`/`A` | Derivado, no se persiste — se recalcula de `FTHG`/`FTAG` para no guardar dos fuentes de la misma verdad |
| `B365H`, `B365D`, `B365A` | Cuotas 1X2 de Bet365 al cierre | **Nunca** a `Predicción` ni a ninguna tabla de `backend/ml/features/` (Artículo V). Van a `CuotaMercado` de `003-track-record-publico`, documentado en `specs/003-track-record-publico/data-model.md` §"Fuente de las cuotas" |

**Tabla de alias de equipo.** Football-Data.co.uk, la API operativa (API-Football) y Kaggle no
escriben el mismo nombre igual (`"Man United"` vs. `"Manchester United"`). `backend/ml/data/`
mantiene un CSV propio `equipo_alias.csv` (`alias`, `equipo_id`) cargado antes que cualquier
otro loader; un nombre sin alias conocido **falla la carga con un error explícito**, nunca crea
un `Equipo` duplicado en silencio — es lo que protege el `unique(nombre, liga)` de
`data-model.md`.

**Kaggle European Soccer Database** aporta features de evento (posesión, tiros, córners) para
enriquecer XGBoost, pero **no** resultado ni cuota — esas ya vienen de Football-Data.co.uk y
usar dos fuentes para el mismo hecho es la clase de duplicación que el Artículo VIII prohíbe. Su
uso es opcional a partir de la Fase 3 de `tasks.md` (T012); el MVP puede entrenar solo con
Football-Data.co.uk.

## 2. Pipeline de entrenamiento (orden de ejecución)

```
backend/ml/data/       → carga los CSV, resuelve alias, escribe Partido/Equipo históricos
backend/ml/features/   → construye el feature set de XGBoost (§4) a partir de Partido/Equipo
backend/ml/models/*/   → train.py de Dixon-Coles y de XGBoost, cada uno independiente
backend/ml/ensemble/   → combina las dos salidas (§5)
backend/ml/evaluation/ → backtesting cronológico, calibración (§6), registro en MLflow (§7)
```

Cada etapa lee la salida persistida de la anterior — no hay estado compartido en memoria entre
etapas, así que cada una es re-ejecutable y testeable sola (Artículo IX).

## 3. Dixon-Coles

Referencia académica: Dixon, M.J. y Coles, S.G. (1997), *"Modelling Association Football Scores
and Inefficiencies in the Betting Market"*. Es el modelo estándar que `docs/project_spec.md`
ya nombra como "el *prior* estadístico clásico" (sección 6.4); esta sección fija su formulación.

**Parámetros del modelo**, uno por equipo `i`:
- `α_i` — fuerza de ataque
- `β_i` — fuerza de defensa
- `γ` — ventaja de jugar de local (un único parámetro global, no por equipo)
- `ρ` — corrección de dependencia entre marcadores bajos (el hallazgo central del paper: en la
  realidad, los resultados 0-0, 1-0, 0-1 y 1-1 son ligeramente más o menos probables que lo que
  predice la independencia de Poisson pura)
- `ξ` (xi) — decaimiento temporal: pesa más los partidos recientes en el ajuste, `peso = exp(-ξ·días_desde_el_partido)`

**Tasas de gol esperadas** para un partido local `i` vs. visitante `j`:
```
λ (goles esperados del local)    = exp(α_i + β_j + γ)
μ (goles esperados del visitante) = exp(α_j + β_i)
```

**Probabilidad del marcador exacto** `(x, y)` goles: Poisson bivariada con la corrección `ρ`
del paper original (matriz de corrección aplicada solo cuando `x ≤ 1` y `y ≤ 1`). El 1X2, el
Over/Under 2.5 y el BTTS se obtienen sumando la matriz de probabilidades de marcador sobre los
rangos correspondientes — **no** hay una fórmula cerrada separada para cada mercado, todos salen
de la misma matriz.

**Implementación:** `statsmodels` no trae Dixon-Coles como función lista — se ajusta como una
optimización del log-likelihood negativo sobre `α`, `β`, `γ`, `ρ` con `scipy.optimize.minimize`,
que es el enfoque estándar en la literatura y en las implementaciones de referencia públicas.
`ξ` se fija como hiperparámetro de configuración, no se ajusta por optimización.

**Hiperparámetros y default:**

| Parámetro | Default | Por qué |
|---|---|---|
| `ξ` (decaimiento temporal) | `0.0018` por día (≈ media vida de un año) | Valor típico reportado en la literatura de aplicación de Dixon-Coles a ligas europeas; sin decaimiento el modelo pesa igual un partido de hace 8 temporadas que uno de la semana pasada |
| Restricción de identificabilidad | `Σα_i = 0` sobre los equipos de la liga en la ventana de entrenamiento | Sin una restricción así el sistema `α`/`β` no tiene solución única (se puede sumar una constante a todos los `α` y restarla a todos los `β` sin cambiar `λ`/`μ`) |

`xg_local`/`xg_visitante` de `Predicción` son exactamente `λ` y `μ` de este modelo — **no** un
xG a nivel de tiro (eso exigiría datos de eventos que el MVP no tiene, sección 6.1).

## 4. Features de XGBoost

XGBoost se entrena sobre el mismo objetivo (1X2, O/U 2.5, BTTS) pero con features adicionales
que Dixon-Coles no usa. Lista cerrada — añadir una columna nueva exige actualizar esta tabla
primero, no solo el código:

| Feature | Cálculo | Ventana |
|---|---|---|
| `forma_local` / `forma_visitante` | Puntos obtenidos (3/1/0) sobre los partidos jugados, normalizado a `[0,1]` | Últimos 5 partidos de cada equipo, cualquier rival |
| `goles_favor_reciente` / `goles_contra_reciente` | Promedio de goles marcados/recibidos | Últimos 5 partidos |
| `descanso_dias` | Días desde el partido anterior de cada equipo hasta este kickoff | — |
| `h2h_forma` | Puntos obtenidos por el local en los enfrentamientos directos previos contra este rival | Últimos 5 enfrentamientos directos, o los que existan si hay menos (ver `head_to_head_disponible`) |
| `fuerza_relativa_ataque` / `fuerza_relativa_defensa` | `α_i`/`β_i` de Dixon-Coles del equipo, ya entrenado — XGBoost usa la salida de Dixon-Coles como feature, no al revés | Del modelo Dixon-Coles vigente |

**Ninguna columna de este feature set referencia cuotas.** El test
`backend/ml/features/test_no_odds_en_feature_set.py` (Artículo V) falla el build si aparece una;
esta tabla es la lista que ese test valida en la práctica.

**Hiperparámetros de XGBoost** (objetivo `multi:softprob` para 1X2, `binary:logistic` para O/U y
BTTS): se ajustan por búsqueda en grilla sobre el log-loss de validación cronológica dentro de
`train.py`, sin valores fijados aquí — a diferencia de Dixon-Coles, XGBoost no tiene un
hiperparámetro con interpretación de dominio que deba decidirse por adelantado.

## 5. Algoritmo de ensamble

`backend/ml/ensemble/predict.py` combina las probabilidades de Dixon-Coles (`p_dc`) y XGBoost
(`p_xgb`) para el mismo mercado por promedio ponderado:

```
p_final = w · p_xgb + (1 - w) · p_dc
```

**Cómo se fija `w`:** búsqueda en grilla, `w ∈ {0.0, 0.05, 0.10, …, 1.0}`, evaluada sobre el
log-loss del conjunto de validación cronológica (el split posterior a la fecha de corte,
Artículo IV) — se elige el `w` que minimiza el log-loss agregado de los tres mercados. Se ajusta
**una vez por reentrenamiento**, no por partido: es el mismo `w` para todas las predicciones de
una `version_modelo`.

**Peso mínimo garantizado para Dixon-Coles:** `w ≤ 0.85`. `docs/project_spec.md` §6.4 ya exige
que Dixon-Coles se mantenga como "ancla interpretable" incluso si XGBoost domina en validación;
`0.85` es ese límite hecho número — deja a Dixon-Coles con al menos 15% de peso siempre.

`xg_local`/`xg_visitante` de la `Predicción` **no** se ensamblan: se toman directamente de
Dixon-Coles (§3), porque son su salida natural y XGBoost no produce una tasa de gol comparable.

## 6. Calibración

`backend/ml/evaluation/calibration.py` construye la tabla `Calibración histórica` de
`data-model.md` a partir del backtesting cronológico:

1. Para cada mercado, ordenar las predicciones de validación por probabilidad predicha del
   resultado más probable.
2. Agrupar en **buckets de ancho 0.1** sobre `[0.33, 1.0]` para 1X2 (`[0.33, 0.43)`, `[0.43,
   0.53)`, … — el mínimo posible en 1X2 es 1/3) y sobre `[0.5, 1.0]` para O/U y BTTS (mercados
   binarios, el mínimo posible es 0.5).
3. Por bucket: `precision_empirica = aciertos_del_bucket / n_observaciones_del_bucket`.
4. Mapeo de `precision_empirica` a badge:

| `precision_empirica` | Badge |
|---|---|
| `≥ 0.60` | Alta |
| `[0.45, 0.60)` | Media |
| `< 0.45` | Baja |

**Umbral `n_observaciones`:** el data-model.md dejaba esto como "a fijar". Se fija en **30**
como default de Sprint 0 — la regla clásica del límite central para que un promedio muestral
empiece a comportarse como normal, usada aquí como una elección conservadora de "cuántas
observaciones necesito antes de confiar en un porcentaje". **No** es la última palabra: se
revisa con datos reales de backtesting en Sprint 1, junto con el criterio de reentrenamiento que
`docs/project_spec.md` §6.5 también deja pendiente para entonces. Si `n_observaciones < 30`, el
badge cae a Baja sin mirar `precision_empirica` — la regla que ya fija RF-005b.

## 7. Convención de MLflow

Registrado por `backend/ml/evaluation/` al final de cada backtesting (sección 6.4).

| Elemento | Convención |
|---|---|
| Experimento | `the-playbook/{mercado}` — un experimento por mercado (`1x2`, `over_under_2_5`, `btts`), para poder comparar runs del mismo mercado entre sí sin filtrar |
| Nombre de run | `{fecha_iso}-{hash_corto_del_commit}` — trazable a un commit exacto del pipeline de entrenamiento, no solo a una fecha |
| Parámetros registrados | `xi`, `w` (peso del ensamble), rango de fechas del split de entrenamiento/validación, versión de los datos de origen |
| Métricas registradas | log-loss y Brier score de Dixon-Coles solo, de XGBoost solo, y del ensamble — las tres, para poder justificar en la defensa académica que el ensamble mejora sobre cada modelo por separado |
| Artefactos | los parámetros `α`/`β`/`γ`/`ρ` ajustados de Dixon-Coles, el modelo XGBoost serializado, y la tabla de calibración resultante |
| `version_modelo` (persistido en `Predicción`) | el `run_id` que MLflow asigna al run del ensamble — así `version_modelo` siempre resuelve a un run real y auditable, nunca a una cadena inventada a mano |

## 8. Dependencias adicionales

No están en `backend/pyproject.toml` hoy (que solo declara lo del arranque genérico, Grupo 0).
Se añaden en **T012** de `tasks.md`, cuando el pipeline de ML se empieza a implementar — no antes
(Artículo VII, no declarar dependencias antes de que la tarea que las usa exista):

```
statsmodels    # ajuste de Dixon-Coles
scipy          # optimización del log-likelihood
xgboost        # modelo de gradient boosting
scikit-learn   # utilidades de evaluación (log-loss, Brier score)
shap           # TreeExplainer para 002
mlflow         # tracking de experimentos
pandas, numpy  # manipulación de datos tabulares
```
