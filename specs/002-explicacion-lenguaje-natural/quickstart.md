# Quickstart: validación manual de Explicación en Lenguaje Natural

**Basado en:** `spec.md`, `plan.md` y `contracts/explanations-api.md`.

## Requisitos previos

Desde la raíz del repositorio, inicia PostgreSQL y Redis:

```powershell
docker compose -f infra/docker-compose.yml up -d postgres redis
```

Configura `backend/.env` a partir de `backend/.env.example` si aún no existe. Desde `backend/`,
instala dependencias y aplica las migraciones:

```powershell
python -m pip install -e ".[dev]"
alembic upgrade head
```

Configura `NEWS_API_KEY` o `NEWS_RSS_FEEDS` (URLs separadas por comas). La ingesta programada
consulta News API cada seis horas y usa RSS si News API no estÃ¡ configurada o no responde. El
reindexado corre cada 15 minutos y consulta las fuentes cuando hay partidos en las prÃ³ximas 24 horas.
Arranca API, worker y scheduler en terminales separadas desde `backend/`:

```powershell
uvicorn app.main:app --reload
celery -A workers.celery_app.celery_app worker --loglevel=info
celery -A workers.celery_app.celery_app beat --loglevel=info
```

Solicita una ingesta y revisa cuÃ¡ntos artÃ­culos se insertaron o actualizaron:

```powershell
python -c "from workers.tasks.ingest_news import ingest_news; print(ingest_news.delay().get(timeout=120))"
```

Configura credenciales IAM de Bedrock para `AWS_REGION` y confirma acceso a `BEDROCK_MODEL_ID`.
La API debe estar activa en `http://localhost:8000`; el partido debe tener una predicción de 001 y
evidencias relacionadas, con embeddings Titan V2 de 1024 dimensiones, indexadas en Postgres. El GET
genera y persiste la primera explicación; necesita Bedrock para crear el embedding de consulta y,
si encuentra evidencia, para redactar el texto. Sin evidencias anteriores al kickoff devuelve el
fallback explícito. Las credenciales Bedrock reales no se sustituyen por los mocks de CI.
El texto generado se guarda en Redis bajo una clave ligada al contenido de la evidencia recuperada y
SHAP; al cambiar esos datos, la siguiente generación usa una entrada distinta de caché.

## Explicación y pregunta de seguimiento

Obtén el UUID de un partido próximo que ya tenga predicción. Consulta la explicación:

```powershell
$matchId = '<UUID de un partido con predicción>'
$explanation = Invoke-RestMethod "http://localhost:8000/api/matches/$matchId/explanation"
$explanation | ConvertTo-Json -Depth 8
```

Para verificar T019–T021b en CI/local con Bedrock simulado y Postgres/pgvector real, ejecuta desde
`backend/`:

```powershell
python -m pytest tests/integration/test_explanations_grounded.py tests/integration/test_temporal_filter.py -q
```

Comprueba que cada evidencia tiene `title`, `url`, `source` y `published_at`, y que cada fecha de
publicación es anterior al kickoff. Sin evidencia suficiente, la respuesta debe indicar
`is_fallback_no_evidence: true` y declarar explícitamente la ausencia de datos.

Envía una pregunta sobre la misma explicación:

```powershell
$body = @{ question = '¿Qué evidencia respalda el factor principal?' } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/api/matches/$matchId/explanation/follow-up" `
  -ContentType 'application/json' `
  -Body $body
```

La respuesta debe limitar `evidence` a fuentes ya citadas por la explicación inicial, mantener las
variables SHAP de esa predicción y no introducir una predicción nueva. Sin explicación inicial, el
endpoint debe devolver 404.

## Revisión manual de groundedness (T022)

Guarda una muestra reproducible con `match_id`, `model_version`, fecha de revisión y respuesta JSON.
Para cada explicación de la muestra, completa esta revisión:

| Comprobación | Criterio |
|---|---|
| Integridad temporal | Cada `published_at` es anterior al kickoff y el enlace abre la fuente citada. |
| Soporte factual | Cada afirmación verificable del texto se puede asociar a una evidencia citada. |
| Relación con el modelo | La variable SHAP mencionada existe en `Predicción.top_shap_features`. |
| No contradicción | El texto no afirma un resultado ni cifras incompatibles con 1X2, O/U 2.5 o BTTS. |
| Fallback | Si no hay cobertura suficiente, el texto reconoce la ausencia y no inventa contexto. |

Registra por comprobación `pasa` o `falla`, el fragmento revisado y el `evidence.id` que lo respalda.
Reporta los fallos con el `match_id` y la versión del modelo. Opcionalmente configura
`RAG_GROUNDEDNESS_ALERT_THRESHOLD` como tasa máxima aceptable entre `0` y `1`; la alerta se activa
cuando `fallidas / revisadas` supera ese valor. Si la variable no está configurada, las alertas
permanecen desactivadas. El equipo aún debe elegir su umbral. El helper
`rag.groundedness.groundedness_alert_triggered(fallidas, revisadas, threshold)` aplica esa regla;
una muestra vacía no genera alerta.

La revisión T022 sigue siendo manual: guarda `match_id`, `model_version`, fecha, respuesta y el
resultado de cada fila de la tabla anterior. La prueba simulada de automatización no reemplaza una
ejecución real con credenciales de Bedrock y evidencia noticiosa verificable.
