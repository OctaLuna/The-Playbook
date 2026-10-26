# Quickstart: validación manual de Predicción de Partido

**Basado en:** `spec.md`, `plan.md` y `contracts/matches-api.md`.

## Preparar el entorno local

Desde la raíz del repositorio, inicia PostgreSQL y Redis:

```powershell
docker compose -f infra/docker-compose.yml up -d postgres redis
```

Configura `backend/.env` a partir de `backend/.env.example` si aún no existe. Desde `backend/`,
instala el proyecto y aplica las migraciones:

```powershell
python -m pip install -e ".[dev]"
alembic upgrade head
```

En terminales separadas, levanta la API y el worker Celery con Beat. Beat ejecuta el generador cada
hora; el worker entrena sobre el histórico con split cronológico y persiste partidos cuyo kickoff
está en las próximas 24 horas:

```powershell
uvicorn app.main:app --reload
celery -A workers.celery_app:celery_app worker --beat --pool=solo --loglevel=INFO
```

La carga del histórico disponible se ejecuta desde `backend/`:

```powershell
python -m ml.data.cargar ml/data/raw/premier_league_2024.csv premier_league
```

Sustituye el CSV por un archivo local de Football-Data.co.uk y usa uno de estos valores de liga:
`premier_league`, `laliga`, `serie_a`, `bundesliga` o `ligue_1`.
El worker necesita al menos 30 partidos jugados, los tres resultados 1X2 en el tramo de
entrenamiento y equipos presentes en ese histórico. Si el entrenamiento falla o faltan equipos,
no crea una predicción ficticia; revisa el log del worker y la consulta devuelve 404 mientras no
haya una predicción persistida.

### Fixture local de demostración

Si la base solo tiene históricos, crea un único partido local de demostración usando equipos que
aparecen en el tramo de entrenamiento. El preflight valida la ventana cronológica, las tres clases
1X2, ambos resultados para O/U y BTTS y cinco apariciones por equipo. No añade resultados al
histórico. Desde `backend/`, primero revisa el plan sin escribir y luego persiste con `--apply`:

```powershell
python -m ml.data.demo_fixture
python -m ml.data.demo_fixture --apply
```

El comando solo escribe cuando `DATABASE_URL` apunta a `localhost`, `127.0.0.1` o `::1`. El kickoff
queda a 12 horas de la ejecución. Copia el UUID que muestra y, con el worker activo, solicita la
predicción:

```powershell
python -c "from workers.tasks.generate_predictions import generate_predictions; print(generate_predictions.delay().get(timeout=900))"
```

El resultado debe ser `1`; verifica las cuatro señales con
`Invoke-RestMethod "http://localhost:8000/api/matches/<UUID>/prediction"`. El ID del fixture es
determinista para el par seleccionado, así que volver a ejecutar el comando no duplica el partido.

## Verificar los endpoints de lectura

Con la API en `http://localhost:8000`, ejecuta desde PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/api/leagues
Invoke-RestMethod 'http://localhost:8000/api/matches/upcoming?page=1&page_size=20'
```

Toma un `id` de la respuesta de partidos y consulta su detalle y predicción:

```powershell
$matchId = '<UUID de la respuesta>'
Invoke-RestMethod "http://localhost:8000/api/matches/$matchId"
Invoke-RestMethod "http://localhost:8000/api/matches/$matchId/prediction"
```

Comprueba que la respuesta incluye `probabilities_1x2`, `over_under_2_5`, `btts`, `xg`,
`confidence`, `head_to_head_available` y `low_data_warning`. Las probabilidades 1X2 deben sumar
1.0; `under` y `btts.no` son los complementos de `over` y `btts.yes`.

## Casos límite

- Partido fuera de la ventana: el detalle existe y la consulta de predicción devuelve 404.
- Equipo con historial insuficiente: la predicción incluye `low_data_warning: true`.
- Sin calibración suficiente para la versión del modelo: `confidence` es `baja`.
- Partido pospuesto: el detalle indica `status: postponed` y la predicción original sigue disponible.
- Sin enfrentamientos previos: `head_to_head_available` es `false`.
- El feature set continúa protegido por `backend/ml/features/test_no_odds_en_feature_set.py`; no se
  agregan cuotas a la predicción.

Para ejecutar el generador una sola vez, con el worker activo, desde otra terminal en `backend/`:

```powershell
python -c "from workers.tasks.generate_predictions import generate_predictions; print(generate_predictions.delay().get(timeout=900))"
```

La salida es el número de predicciones nuevas guardadas. Una segunda ejecución conserva las filas
existentes y no las sobrescribe.
