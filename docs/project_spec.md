# Especificación Oficial del Proyecto — The Playbook

**Equipo:** The-Playbook
**Materia:** Taller de Sistemas Inteligentes
**Versión:** 2.0 (reemplaza a v1.0 tras auditoría técnica)
**Fecha:** 16 de agosto de 2026
**Ubicación en repositorio:** `docs/project_spec.md`
**Registro de cambios respecto a v1.0:** ver sección 12.

---

## 1. Product Goal

> Para aficionados y analistas amateur de fútbol que quieren entender —no solo adivinar— qué puede pasar en un partido, construiremos un sistema inteligente que predice resultados, goles y mercados clave (1X2, over/under, BTTS) y explica en lenguaje natural qué datos reales respaldan cada predicción (forma del equipo, lesiones, historial de enfrentamientos), permitiendo comparar la precisión del modelo contra las cuotas públicas del mercado y verificar su desempeño real partido a partido, utilizando datos históricos multi-temporada y de contexto disponibles públicamente, con despliegue operativo en una plataforma web accesible.

**Los 3 pilares de valor** (todo feature del proyecto debe trazarse a uno de estos):

1. Predicción de resultados y mercados clave.
2. Explicación en lenguaje natural con evidencia verificable y temporalmente honesta.
3. Medición y transparencia del desempeño real del modelo.

---

## 2. Funcionalidades del producto

### 2.1 Núcleo del MVP (imprescindible)

| Funcionalidad | Descripción |
|---|---|
| Predicción 1X2 | Probabilidad de victoria local, empate o visitante por partido. |
| Predicción Over/Under de goles | Probabilidad de más/menos de 2.5 goles totales (ampliable a otras líneas). |
| Predicción BTTS (ambos marcan) | Probabilidad de que ambos equipos anoten. |
| xG (expected goals) por equipo | Goles esperados calculados por el modelo, no solo goles reales históricos. |
| Explicación en lenguaje natural | El LLM (vía AWS Bedrock) explica el "por qué" de cada predicción citando datos reales (forma, lesiones, head-to-head) — nunca predice por sí mismo, y nunca usa evidencia posterior al partido (ver sección 7.3). |
| Nivel de confianza de la predicción | Badge visual (Alta/Media/Baja) derivado de la **precisión histórica calibrada** del modelo para ese rango de probabilidad (backtesting cronológico, sección 6.5) — **nunca** de la distancia a un reparto uniforme (33/33/33). Ver ADR [0001](adr/0001-badge-confianza-calibrado.md). |
| Track record del modelo | Panel público con el porcentaje de aciertos de los últimos N partidos predichos — auditable por cualquier usuario. |

### 2.2 Funcionalidades adicionales

| Funcionalidad | Prioridad | Origen |
|---|---|---|
| Heatmap de tiros por equipo (zona de peligro ofensivo) | Alta | Visto en xGscore / literatura académica de xG |
| Nivel de dificultad del próximo rival (fuerza ofensiva/defensiva) | Media | Visto en Forebet |
| Favoritos — seguir equipos o ligas (requiere auth simple) | Media | Visto en Forebet |
| Actualización dinámica de predicciones ante noticias de último momento | Alta | Visto en Scores24 |
| Radar chart comparando estilo de juego entre equipos | Media | Estándar en scouting deportivo |

### 2.3 Stretch goals (post-MVP, explícitamente fuera del MVP)

> **Cambio respecto a v1.0:** LSTM y el modelo de sentimiento pasan de "núcleo" a *stretch goal*. La razón ya **no** es falta de volumen de datos (ver sección 6, resuelto con datasets multi-temporada), sino gestión de riesgo de cronograma: son los componentes de mayor costo de implementación/tuning y los que menos mueven la aguja sobre los tres pilares de valor si el MVP ya cubre Dixon-Coles + XGBoost + RAG con buena calidad.

| Funcionalidad | Por qué se pospone / descarta |
|---|---|
| Modelo LSTM (series temporales de forma/fatiga) | Alto costo de tuning para el beneficio marginal esperado sobre XGBoost en el horizonte del taller. Se reincorpora en segunda iteración, ya con la capa de ensamble (sección 6.4) lista. |
| Modelo de sentimiento sobre noticias (Transformer) | Depende de que el pipeline de RAG esté maduro y probado primero (evita construir sobre una base de ingestión inestable). |
| Predicción de tarjetas/córners | Datos más ruidosos y dependientes del árbitro asignado, a veces confirmado muy poco antes del partido. |
| Reentrenamiento automático / detección de drift | Fuera del ciclo de un taller; se documenta el criterio manual de reentrenamiento en su lugar (sección 6.5). |

### 2.4 Explícitamente fuera de alcance (no se hará)

| Funcionalidad | Por qué se descarta |
|---|---|
| Live scores minuto a minuto | Alto consumo de presupuesto de API sin aportar al objetivo académico (el proyecto predice, no retransmite). |
| Comparador de cuotas de casas de apuestas como producto visible | Zona gris legal/ética para un proyecto académico. Las cuotas se usan **solo como baseline interno** de comparación (log-loss vs. mercado), nunca se muestran como funcionalidad al usuario. |

---

## 3. Comparación con la competencia

| Funcionalidad | Forebet / xGscore / NerdyTips / Scores24 | The Playbook (nosotros) |
|---|---|---|
| Predicción 1X2 + probabilidades | ✅ | ✅ |
| Over/Under, BTTS | ✅ | ✅ |
| xG por equipo | ✅ | ✅ |
| Heatmap de tiros | ✅ (nivel académico) | ✅ |
| Explicación en lenguaje natural con evidencia | ✅ (NerdyTips, Scores24) | ✅ — diferencial: RAG con filtro temporal estricto, no solo texto genérico |
| Actualización dinámica por noticias de último momento | ✅ (Scores24) | ✅ (vía cron de reindexado) |
| Track record público del modelo | Implícito, poco explícito | ✅ — diferencial: explícito y auditable |
| Comparación honesta contra baseline de mercado (log-loss) | ❌ (nadie lo expone como feature) | ✅ — diferencial fuerte para la defensa académica |
| Live scores | ✅ | ❌ (fuera de alcance, justificado) |
| Comparador de casas de apuestas | ✅ | ❌ (fuera de alcance, justificado por ética/legal) |

**Conclusión:** el proyecto iguala las funcionalidades núcleo del mercado y se diferencia en dos puntos que ningún competidor expone de forma explícita: (1) comparación honesta contra un baseline de mercado, y (2) trazabilidad completa y **temporalmente honesta** entre predicción → evidencia (RAG) → track record verificable.

---

## 4. Arquitectura general

```
Frontend (Next.js + TS) ──REST──▶ Backend (FastAPI) ──▶ PostgreSQL + pgvector + Redis
                                        │
                                        ├──▶ ML: statsmodels (Dixon-Coles), XGBoost
                                        ├──▶ DL (stretch goal): PyTorch (LSTM), sentimiento
                                        ├──▶ Ensemble layer (combina Dixon-Coles + XGBoost)
                                        └──▶ RAG/LLM: LangChain + AWS Bedrock (Claude)
                                                        │
                                                        └──▶ Amazon Titan Embeddings (Bedrock)

Workers (Celery + Redis): scraping, reindexado RAG, entrenamiento — SIEMPRE separados del proceso API.
```

**Regla arquitectónica explícita (corrige hallazgo A1 de la auditoría):** ningún job de entrenamiento de modelos ni de reindexado RAG corre en el mismo proceso/contenedor que atiende requests HTTP del API, ni siquiera en desarrollo local con docker-compose. Todo pasa por Celery.

Monorepo, un solo backend en Python sirviendo endpoints web y lógica de ML/DL/RAG — evita microservicios innecesarios para el alcance del taller, siempre que se respete la separación de procesos anterior.

---

## 5. Stack tecnológico por capa

| Capa | Tecnología elegida | Justificación |
|---|---|---|
| **Frontend** | Next.js 15 (App Router) + TypeScript | SSR, deploy directo en Vercel, tipado fuerte alineado con Pydantic del backend |
| **UI / estilos** | Tailwind CSS + shadcn/ui | Velocidad de desarrollo, componentes accesibles y consistentes |
| **Gráficos** | Recharts | Integración nativa con React para probabilidades, xG, radar charts |
| **Estado del servidor** | TanStack Query | Cache y revalidación de datos sin lógica manual repetida |
| **Backend** | FastAPI (Python 3.12) | Un solo lenguaje con el stack de ML/DL, evita latencia de microservicios separados |
| **Validación de datos** | Pydantic v2 | Contratos de entrada/salida estrictos entre frontend y backend |
| **ORM / migraciones** | SQLAlchemy 2.0 (async) + Alembic | Control versionado del esquema de base de datos |
| **Tareas en background** | Celery + Redis | Reentrenamiento, scraping y reindexado sin bloquear requests HTTP |
| **Base de datos** | PostgreSQL 16 | Datos estructurados de partidos, equipos, estadísticas, predicciones |
| **Vector store** | pgvector (extensión de Postgres) | Suficiente para el volumen del proyecto, evita un servicio externo adicional |
| **Cache / rate-limiting** | Redis | Cache de predicciones recientes, cache de explicaciones LLM, control de límites de APIs externas |
| **ML — modelo base** | statsmodels (regresión de Poisson / Dixon-Coles) | Estándar académico validado para predicción de resultados de fútbol |
| **ML — modelo comparativo** | XGBoost | Mejor manejo de features no lineales; se combina con Dixon-Coles vía capa de ensamble (sección 6.4) |
| **ML — clasificación de tarjetas** | scikit-learn (Random Forest / Logistic Regression) | Stretch goal — feature de árbitro + historial de rivalidad |
| **DL — series temporales (stretch goal)** | PyTorch (LSTM) | Captura tendencias de forma/fatiga; ahora viable gracias a datasets multi-temporada (sección 6) |
| **DL — sentimiento de noticias (stretch goal)** | Hugging Face Transformers (modelo en español, ej. RoBERTuito) | Feature adicional derivado de noticias pre-partido |
| **RAG — orquestación** | LangChain | Pipeline de chunking, retrieval y prompting sobre noticias indexadas, con filtro temporal obligatorio |
| **RAG / LLM — proveedor** | **AWS Bedrock (Anthropic Claude)** | Acceso gestionado a Claude sin manejar claves de API directamente; IAM + límites de consumo integrados con el resto de la infraestructura si se despliega en AWS; facturación unificada |
| **Embeddings** | **Amazon Titan Text Embeddings V2 (Bedrock)** | Soporta español de forma nativa, se invoca con el mismo cliente/credenciales que el LLM (`boto3` + `bedrock-runtime`), sin depender de una cuenta ni facturación separada de OpenAI |
| **Explicabilidad del modelo ML** | SHAP, limitado al modelo XGBoost (TreeExplainer) | Evidencia matemática de qué features pesaron más; los componentes de deep learning se explican solo vía LLM/RAG (ver sección 8) |
| **Heatmaps / visualización deportiva** | mplsoccer (Python) o D3.js (frontend) | Librería especializada en visualización de datos de fútbol |
| **Auth (favoritos)** | NextAuth.js (Auth.js) | Integración nativa con Next.js, soporte OAuth sin backend propio de sesiones |
| **Tracking de experimentos** | MLflow | Registro de qué modelos se probaron y por qué ganó el elegido — evidencia directa para la defensa |
| **Contenerización** | Docker + docker-compose | Backend + Postgres + Redis levantados con un solo comando |
| **CI/CD** | GitHub Actions | Pruebas automáticas y bloqueo de merge si fallan |
| **Deploy frontend** | Vercel | Tier gratuito, integración nativa con Next.js |
| **Deploy backend** | Railway o Render (alternativa: AWS App Runner / ECS Fargate si el equipo ya está en el ecosistema AWS por Bedrock) | Tier gratuito suficiente para el taller; AWS es una opción natural para reducir la superficie de proveedores dado que Bedrock ya vive ahí |

### 5.1 Nota sobre el cambio a AWS Bedrock

El uso de AWS Bedrock en lugar de la API directa de Anthropic implica:

- **Autenticación vía IAM**, no una API key suelta en variables de entorno — se recomienda un rol IAM dedicado con permisos mínimos (`bedrock:InvokeModel` sobre el/los ARNs de modelo específicos que se usen).
- El acceso a modelos de Bedrock debe habilitarse explícitamente por región y por cuenta ("model access") antes del primer llamado; esto debe hacerse en Sprint 0, no dejarse para cuando el equipo ya esté implementando el pipeline de RAG.
- Bedrock expone tanto la API nativa de invocación por modelo como el **Converse API**, que normaliza el formato de mensajes entre proveedores — se recomienda usar Converse API para no acoplar el código del backend a un formato específico de Anthropic, en caso de que el equipo quiera comparar con otro modelo de Bedrock más adelante.
- El SDK a usar en el backend Python es `boto3` (cliente `bedrock-runtime`), que ya es compatible con el stack FastAPI + Pydantic sin dependencias adicionales.
- Dado que tanto el LLM como los embeddings ahora viven en Bedrock, se elimina la ambigüedad que tenía v1.0 entre `text-embedding-3-small` (OpenAI) y `sentence-transformers`: **se estandariza todo el pipeline de IA generativa en un solo proveedor gestionado**, lo cual simplifica facturación, límites de tasa y manejo de credenciales.

---

## 6. Datos: fuentes históricas y solución al problema de volumen insuficiente

### 6.1 Problema identificado en v1.0

La versión anterior del spec no especificaba de dónde saldrían datos de temporadas *anteriores* a la actual, y una sola temporada de liga son solo ~380 partidos — insuficiente para entrenar modelos de deep learning (LSTM, Transformer) sin sobreajuste severo.

### 6.2 Fuentes de datos multi-temporada evaluadas

| Fuente | Cobertura histórica | Formato / acceso | Uso recomendado |
|---|---|---|---|
| **Football-Data.co.uk** | <cite index="8-1">Historial de resultados, goles y forma organizados por temporada para ligas como Premier League, LaLiga, Serie A, Bundesliga y Ligue 1</cite>, con varias décadas de cobertura en las ligas top | CSV descargable directamente, sin API key ni límite de requests | **Fuente principal de entrenamiento histórico** para Dixon-Coles, XGBoost y (en la fase stretch) LSTM. Incluye cuotas de casas de apuestas históricas, útiles para el baseline interno de log-loss (nunca expuesto como producto, según sección 2.4). |
| **Kaggle — European Soccer Database** | <cite index="9-1">Más de 25,000 partidos y 10,000 jugadores de 11 países europeos, temporadas 2008 a 2016</cite>, con <cite index="9-1">cuotas de hasta 10 casas de apuestas y eventos detallados de partido (tipos de gol, posesión, córners, faltas, tarjetas) para más de 10,000 partidos</cite> | Descarga única (SQLite/CSV) desde Kaggle | Complemento con eventos a nivel de partido (no solo resultado) para feature engineering más rico — útil para el LSTM en la fase stretch. |
| **StatsBomb Open Data** | Datos abiertos de eventos a nivel de jugada (pases, tiros, duelos) para competiciones y temporadas seleccionadas, actualizado regularmente | JSON vía repositorio público | Fuente de referencia para heatmaps de tiros con mayor granularidad que xG agregado; uso opcional si el tiempo lo permite. |
| **API-Football (RapidAPI)** | Temporada actual + fixtures, alineaciones y estadísticas en tiempo casi real; cobertura histórica de temporadas pasadas variable según plan | REST API, requiere API key | Fuente **operativa** (temporada en curso, próximos partidos, lesiones) — no fuente principal de entrenamiento histórico por su límite de requests en el tier gratuito. |
| **football-data.org** | Resultados y fixtures de competiciones principales | REST API, tier gratuito limitado | Respaldo/complemento cuando el límite de API-Football se agota. |
| **Understat** | xG histórico por partido (scraping ético, datos públicos) | Scraping | Referencia de xG para validar/calibrar el xG calculado por el modelo propio. |
| **News API / RSS de medios deportivos** | Cobertura pre-partido (lesiones, forma, contexto) | REST / RSS | Alimenta exclusivamente el pipeline RAG — nunca el entrenamiento de los modelos de predicción. |

### 6.3 Decisión adoptada

- **Entrenamiento de Dixon-Coles y XGBoost:** combinar **Football-Data.co.uk** (multi-década, multi-liga, incluye cuotas para el baseline) con el dataset de **Kaggle European Soccer Database** (eventos de partido más ricos para feature engineering). Esto da varios miles de partidos por liga cubierta, resolviendo el problema de volumen de v1.0 sin depender de una sola fuente.
- **Entrenamiento del LSTM (stretch goal):** usar el mismo corpus combinado, pero **agrupando varias ligas** en un solo conjunto de entrenamiento con la liga como feature categórica, en vez de entrenar un LSTM por liga — así se multiplica el volumen efectivo de secuencias disponibles.
- **Datos operativos (temporada en curso, próximos partidos, lesiones confirmadas):** API-Football como fuente principal, football-data.org como respaldo.
- **Todas las fuentes históricas se cargan una sola vez** (batch, vía un job de Celery) a PostgreSQL en Sprint 0-1; no se re-scrapea en cada request.

### 6.4 Capa de ensamble entre modelos (corrige hallazgo M1 de la auditoría)

v1.0 no definía cómo se combinaban los tres modelos de predicción. Se adopta el siguiente esquema, explícito y simple de defender académicamente:

1. **Dixon-Coles** produce una distribución de probabilidad base (1X2, O/U, BTTS) a partir de la tasa de goles esperada de cada equipo — es el *prior* estadístico clásico.
2. **XGBoost** se entrena sobre features adicionales (forma reciente, head-to-head, descanso entre partidos, fuerza del rival, y en la fase stretch, salida del LSTM como feature adicional) para predecir el mismo conjunto de mercados.
3. **Combinación por promedio ponderado (weighted averaging)**, con el peso de cada modelo ajustado por validación cronológica (backtesting) sobre log-loss: si XGBoost supera consistentemente a Dixon-Coles en el conjunto de validación, su peso aumenta; si no, se mantiene un peso mínimo garantizado para Dixon-Coles como ancla interpretable.
4. Los pesos finales, y el proceso para llegar a ellos, se registran en **MLflow** como parte de la evidencia de la defensa académica.
5. Si en la fase stretch se incorpora el LSTM, entra como **generador de features** para XGBoost (no como modelo independiente en el ensamble), evitando la ambigüedad de "cuatro modelos compitiendo" que tenía v1.0.

### 6.5 Split de entrenamiento (corrige hallazgo M2 de la auditoría)

**Obligatorio: split cronológico, nunca aleatorio.** Se entrena con partidos anteriores a una fecha de corte y se valida/testea con partidos posteriores a esa fecha, replicando cómo el sistema se usaría en producción (nunca "ver" resultados futuros al momento de predecir un partido pasado). Este criterio se documenta en `backend/ml/evaluation/` y se verifica con un test automatizado que falla el build si algún pipeline usa `train_test_split` sin el parámetro de orden temporal.

Criterio de reentrenamiento (sustituye al vacío señalado como hallazgo M5): reentrenar manualmente al cierre de cada jornada/fecha FIFA, o antes si el log-loss del track record público se degrada más de un umbral definido por el equipo (a fijar en Sprint 1). El disparador automático de drift queda fuera de alcance del MVP (sección 2.3).

---

## 7. Pipeline de RAG (corregido)

### 7.1 Chunking

Chunkeo por **artículo de noticia completo**, no por párrafo suelto — las noticias deportivas pre-partido son cortas y fragmentar pierde el contexto de quién se lesionó, en qué equipo y con qué gravedad. Si un artículo excede ~500 tokens, se aplica overlap de 15-20% entre sub-chunks.

### 7.2 Embeddings

Amazon Titan Text Embeddings V2 vía Bedrock (ver sección 5.1) — resuelve la ambigüedad de v1.0 y da soporte nativo a español.

### 7.3 Filtro temporal obligatorio (corrige el hallazgo crítico de la auditoría)

Toda query de retrieval contra pgvector debe incluir la restricción:

```sql
WHERE fecha_publicacion_noticia < fecha_kickoff_del_partido
```

Esto es una restricción a nivel de query, no una convención de equipo. Sin este filtro, el sistema podría recuperar crónicas o análisis posteriores al partido que revelan el resultado, contaminando la "explicación" con información que en la realidad no existía antes del kickoff — lo cual invalidaría la honestidad del track record frente al tribunal.

### 7.4 Fallback ante ausencia de evidencia

Si el retrieval no encuentra evidencia suficiente (equipos o ligas con poca cobertura mediática), el LLM debe declarar explícitamente la ausencia de datos en la explicación, en vez de generar una justificación genérica no verificable. Esto protege el pilar 2 del product goal.

### 7.5 Caché de explicaciones

Las explicaciones generadas se cachean en Redis, y solo se regeneran si la evidencia subyacente (noticias indexadas relevantes a ese partido) cambió desde la última generación — controla el costo de invocaciones a Bedrock.

### 7.6 Métrica de calidad de RAG

Se incorpora una revisión de *groundedness* (¿la explicación se sostiene solo con la evidencia citada?) sobre una muestra de explicaciones por sprint, ya sea manual o mediante un framework tipo RAGAS si el tiempo del equipo lo permite.

---

## 8. Explicabilidad

- **SHAP** se aplica únicamente sobre el modelo **XGBoost** (vía `TreeExplainer`), que es donde es estable y computacionalmente barato.
- Los componentes de deep learning (LSTM, sentimiento), si se incorporan en la fase stretch, se explican **solo** a través del LLM/RAG, no vía SHAP — se documenta esta decisión explícitamente para que se lea como decisión de diseño y no como omisión frente al tribunal.

---

## 9. Métricas de evaluación del modelo

- **Log-loss** y **Brier score** como métricas principales — no accuracy cruda, dado que en fútbol el empate es el resultado más difícil de predecir y una métrica ingenua puede ser engañosa.
- **Baseline obligatorio de comparación:** cuotas históricas del mercado (de Football-Data.co.uk y Kaggle) para el histórico, y de la fuente operativa disponible para partidos en curso — uso interno, nunca expuesto como producto (sección 2.4).
- **Backtesting cronológico** (sección 6.5) como método de validación, registrado en MLflow.
- **Track record público:** porcentaje de aciertos sobre los últimos N partidos predichos, actualizado automáticamente.

---

## 10. Estructura del monorepo

```
the-playbook/
├── frontend/                      # Next.js 15 + TypeScript
│   ├── app/                        # App Router: páginas y layouts
│   ├── components/                  # UI compartida (shadcn/ui + Tailwind)
│   ├── lib/                          # cliente API, utilidades, TanStack Query hooks
│   └── public/
│
├── backend/                        # FastAPI (Python 3.12)
│   ├── app/
│   │   ├── api/                     # routers por dominio: matches, predictions, teams, track_record
│   │   ├── core/                     # config, seguridad, settings (Pydantic Settings), credenciales IAM/Bedrock
│   │   ├── models/                    # SQLAlchemy models
│   │   ├── schemas/                    # Pydantic schemas (contratos in/out)
│   │   ├── services/                    # lógica de negocio — orquesta ml/ y rag/, nunca vive en routers
│   │   └── db/                         # sesión async, migraciones (Alembic)
│   │
│   ├── ml/
│   │   ├── data/                        # loaders de Football-Data.co.uk, Kaggle, API-Football
│   │   ├── features/                     # feature engineering compartido entre modelos
│   │   ├── models/
│   │   │   ├── dixon_coles/               # train.py, predict.py, evaluate.py
│   │   │   ├── xgboost/                    # train.py, predict.py, evaluate.py
│   │   │   └── lstm/                        # stretch goal — mismo contrato que los anteriores
│   │   ├── ensemble/                     # capa de combinación (sección 6.4)
│   │   └── evaluation/                    # log-loss, Brier, backtesting cronológico (sección 6.5)
│   │
│   ├── rag/
│   │   ├── ingestion/                     # scraping / News API + chunking (sección 7.1)
│   │   ├── retrieval/                      # queries a pgvector con filtro temporal obligatorio (sección 7.3)
│   │   └── generation/                      # prompts, cliente Bedrock (Converse API), caché de explicaciones
│   │
│   ├── workers/                        # tareas Celery: scraping, reindexado, reentrenamiento
│   ├── tests/
│   └── alembic/                        # migraciones de base de datos
│
├── infra/
│   ├── docker-compose.yml              # backend + Postgres + Redis, un solo comando
│   ├── Dockerfile.backend
│   └── github-actions/                  # workflows de CI/CD
│
├── docs/
│   ├── project_spec.md                  # este documento
│   ├── team-charter.md
│   ├── product_goal.md
│   ├── backlog_inicial.md
│   └── adr/                              # Architecture Decision Records numerados
│
└── README.md
```

**Reglas de la estructura:**

- La lógica de negocio vive en `backend/app/services/`, nunca directamente en los routers de `backend/app/api/` — mantiene los endpoints delgados y testeables.
- `backend/ml/` y `backend/rag/` no importan nada de `backend/app/api/`; se comunican con el backend únicamente a través de `backend/app/services/`, lo que permite testear el pipeline de ML/RAG de forma aislada.
- Todo lo que corre en `backend/workers/` se invoca vía Celery, nunca de forma síncrona dentro de un endpoint (regla de la sección 4).
- Cada decisión que se aparte de este documento debe registrarse como un ADR en `docs/adr/`.

---

## 11. Documentos de proceso versionados

| Documento | Ubicación | Contenido |
|---|---|---|
| Team Charter | `docs/team-charter.md` | Integrantes, roles, canales, flujo de PR, manejo de bloqueos, uso de IA, DoD |
| Product Goal | `docs/product_goal.md` | Enunciado de valor validado, desglose y trazabilidad al backlog |
| Backlog Inicial | `docs/backlog_inicial.md` | Tareas de Sprint 0 organizadas por lista (Discovery, Data, Architecture, Build/QA/Deploy, Risk) |
| Este documento | `docs/project_spec.md` | Decisiones de producto y técnicas consolidadas — v2.0 |

---

## 12. Registro de cambios v1.0 → v2.0

| Área | v1.0 | v2.0 | Motivo |
|---|---|---|---|
| LLM | Claude API directa | AWS Bedrock (Claude vía Converse API) | Autenticación gestionada por IAM, facturación unificada, decisión del equipo |
| Embeddings | Ambiguo entre `text-embedding-3-small` y `sentence-transformers` | Amazon Titan Text Embeddings V2 (Bedrock) | Elimina ambigüedad; coherente con el proveedor único (Bedrock) |
| Retrieval RAG | Sin filtro temporal explícito | Filtro obligatorio `fecha_noticia < kickoff` a nivel de query | Evita fuga de información y explicaciones con evidencia inexistente al momento del partido |
| Datos de entrenamiento | Implícito, solo temporada actual (~380 partidos) | Football-Data.co.uk + Kaggle European Soccer Database, multi-década y multi-liga | Resuelve volumen insuficiente para DL sin inventar datos sintéticos |
| Combinación de modelos | No definida (3 modelos "compitiendo") | Ensemble explícito: Dixon-Coles + XGBoost por promedio ponderado, LSTM como generador de features en fase stretch | Da un predictor final con lógica de arbitraje clara |
| Split de entrenamiento | No especificado | Cronológico obligatorio, verificado por test automatizado | Evita fuga de información temporal, error clásico en datos deportivos |
| Alcance DL (LSTM, sentimiento) | Núcleo del MVP | Stretch goal post-MVP | Reduce riesgo de cronograma sin perder pilares de valor |
| SHAP | Aplicado sin distinción a todos los modelos | Limitado a XGBoost; DL se explica solo vía LLM | SHAP sobre LSTM/Transformer es costoso e inestable |
| Aislamiento de entrenamiento | Implícito vía Celery, sin regla explícita | Regla arquitectónica explícita: ningún job pesado en el proceso API | Evita degradar la latencia del servicio mientras se reentrena |
| Reentrenamiento/drift | Ausente sin mención | Declarado explícitamente fuera de alcance del MVP, con criterio manual documentado | Consistencia documental con el resto de la sección "fuera de alcance" |

### 12.1 Registro de cambios v2.0 → v2.1 (auditoría SDD)

<!-- audit-sdd:ignore-start — esta tabla cita a propósito los nombres y rutas antiguos -->

| Área | v2.0 | v2.1 | Motivo |
|---|---|---|---|
| Nivel de confianza (§2.1) | Badge derivado de la distancia a un reparto uniforme (33/33/33) | Badge derivado de la precisión histórica calibrada (backtesting cronológico, §6.5) | §2.1 contradecía directamente a `RF-005` de `specs/001-prediccion-partido/spec.md` y al spec delta de OpenSpec, que ya prohibían explícitamente la distancia a uniforme. Un badge basado en la forma de la distribución mide *decisión del modelo*, no *fiabilidad*, y rompe los pilares 2 y 3 del product goal. Ver ADR [0001](adr/0001-badge-confianza-calibrado.md) |
| Ubicación de este documento | `docs/project_spec_v2.md` (con la cabecera declarando `docs/project_spec.md`) | `docs/project_spec.md` | 24 referencias en 15 archivos apuntaban a `docs/project_spec.md`, que no existía. El rename cierra el grafo de referencias en lugar de reescribir 24 enlaces |
| Ruta del ensamble | Ambigua: `ml/ensemble/` (§10) vs `ml/models/ensemble/` (plan y tasks de 001) | `backend/ml/ensemble/` canónico en §10, plan y tasks | Tres fuentes daban tres rutas distintas. `ml/models/*/` conlleva el contrato `train/predict/evaluate` del Artículo II, que no aplica al ensamble |
| Referencias de sección | 14 apuntaban a secciones inexistentes (`7.7`, `7.8`, `7.9`) o desfasadas en uno | Todas resuelven a un heading real, verificado por `npm run audit:sdd` | `T011` de 002 remitía a "sección 7.5" para la sanitización anti-prompt-injection, que es en realidad la caché de explicaciones — un agente habría implementado el control equivocado |

<!-- audit-sdd:ignore-end -->

---

*Este documento consolida las decisiones de producto y técnicas tomadas hasta la fecha, incorporando las correcciones de la auditoría técnica interna. Cualquier cambio de alcance o de stack debe reflejarse aquí vía Pull Request, y debe justificarse con un ADR en `docs/adr/` si afecta una decisión arquitectónica ya registrada.*
