# Quickstart: Validación manual de la Interfaz Web

**Basado en:** `specs/004-interfaz-web/spec.md`, `plan.md` y los contratos de API de 001, 002 y 003.

## Requisitos

- Docker Desktop en ejecución.
- Python 3.12 y Node.js 20 o posterior.
- Backend y frontend instalados según los pasos siguientes.
- Una base local configurada en `backend/.env`.
- `frontend/.env.local` con `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## 1. Iniciar PostgreSQL y Redis

Desde la raíz del repositorio:

```powershell
docker compose -f infra/docker-compose.yml up -d postgres redis
```

El compose está en `infra/docker-compose.yml`; inicia PostgreSQL y Redis, no la API FastAPI.

## 2. Preparar el backend (solo la primera vez)

Desde la raíz del repositorio, entra a backend, copia la configuración solo si no existe y crea el entorno solo si aún no está:

~~~powershell
cd backend
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path .venv/Scripts/python.exe)) { py -3.12 -m venv .venv }
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m alembic upgrade heads
cd ..
~~~

El paso de instalación se ejecuta la primera vez o cuando cambian las dependencias. Las migraciones preparan el esquema de la base; no cargan partidos ni predicciones.

## 3. Iniciar la API

En una terminal desde la raíz del repositorio:

```powershell
cd backend
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000`. En otra terminal, comprueba:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/api/leagues
$r = Invoke-RestMethod 'http://localhost:8000/api/matches/upcoming?page=1&page_size=20'
$r | ConvertTo-Json -Depth 5
```

La salud debe devolver `status: ok` y ligas debe devolver las cinco ligas. En una base recién migrada, `matches` puede estar vacío y `total` ser 0; eso indica que faltan datos para el recorrido completo, no que la API esté desconectada. La carga de históricos y la generación de fixtures/predicciones se describen en `specs/001-prediccion-partido/quickstart.md`.

## 4. Preparar e iniciar el frontend

Desde la raíz del repositorio, crea la configuración local solo si aún no existe e instala las dependencias bloqueadas:

```powershell
if (-not (Test-Path frontend/.env.local)) { Copy-Item frontend/.env.example frontend/.env.local }
cd frontend
npm ci
```

Confirma que `frontend/.env.local` contiene `NEXT_PUBLIC_API_URL=http://localhost:8000`. Luego inicia Next.js:

```powershell
npm run dev
```

Abre la URL que Next.js indique, normalmente `http://localhost:3000`.

## Modo de demostración del frontend (opcional)

Para revisar el diseño con respuestas de ejemplo sin insertar datos en la base, inicia el frontend en una terminal de PowerShell así:

```powershell
cd frontend
$env:NEXT_PUBLIC_DEMO_MODE = "true"
npm run dev
```

Las pantallas de este modo usan datos de demostración y no prueban la integración con la API real. Para volver al modo API, detén el frontend con `Ctrl+C`, elimina la variable de esa terminal y vuelve a iniciarlo:

```powershell
Remove-Item Env:NEXT_PUBLIC_DEMO_MODE -ErrorAction SilentlyContinue
npm run dev
```

## Validación automática

Desde `frontend/`, ejecuta:

```powershell
npm run lint
npm run typecheck
npm test
```

Los tres comandos deben finalizar correctamente.

## Escenario 1 — Recorrido completo del producto

1. Abrir la página principal.
2. Verificar que se listan los partidos próximos con equipos, liga y fecha.
3. Verificar que los partidos aparecen ordenados por proximidad al kickoff.
4. Filtrar por una liga y verificar que la liga aparece en la URL.
5. Copiar esa URL en una pestaña nueva y verificar que el filtro se conserva.
6. Abrir un partido con predicción generada.
7. Verificar que aparecen las cuatro señales: 1X2, O/U 2.5, BTTS y xG.
8. Verificar que el badge de confianza aparece en la misma vista.
9. Verificar que la explicación aparece y que cada evidencia tiene título y enlace.
10. Enviar una pregunta de seguimiento y verificar que la respuesta aparece en la misma vista junto con su evidencia.

## Escenario 2 — API no disponible

1. Con la interfaz abierta, detener la API en su terminal con `Ctrl+C`.
2. Recargar la página principal.
3. Verificar que aparece un mensaje de error distinto del estado de "no hay partidos".
4. Verificar que aparece la opción **Reintentar**.
5. Volver a iniciar la API siguiendo el paso 3.
6. Pulsar **Reintentar** y verificar que la información vuelve a cargar.

## Escenario 3 — Partido sin explicación

1. Abrir un partido que tenga predicción pero cuya explicación todavía no esté disponible.
2. Verificar que las cuatro señales continúan mostrándose.
3. Verificar que la interfaz indica que la explicación no está disponible todavía.
4. Verificar que la vista no se rompe ni queda en blanco.

## Escenario 4 — Aviso de datos insuficientes

1. Abrir un partido cuya predicción tenga `low_data_warning: true`.
2. Verificar que el aviso aparece antes de las probabilidades.
3. Verificar que el aviso no aparece únicamente como una nota al pie.

## Escenario 5 — Track record sin credenciales

1. Abrir el panel de track record en una ventana privada, sin sesión iniciada.
2. Verificar que carga sin solicitar autenticación.
3. Verificar que aparecen por separado los tres mercados: 1X2, O/U 2.5 y BTTS.
4. Verificar que cada mercado muestra su porcentaje de aciertos y sus métricas.
5. Entrar al detalle y verificar que cada fila muestra lo predicho junto con lo ocurrido.
6. Si `model_versions` contiene más de una versión, verificar que la interfaz muestra el aviso correspondiente.

## Escenario 6 — Muestra insuficiente

1. Con una base de datos sin partidos evaluados, abrir el panel de track record.
2. Verificar que declara que todavía no existe una muestra suficiente.
3. Verificar que no presenta ceros como sustituto de datos inexistentes.

## Escenario 7 — Accesibilidad y responsive

1. Recorrer las tres vistas utilizando únicamente el teclado (`Tab`, `Enter`, `Escape`).
2. Verificar que todos los controles interactivos son alcanzables.
3. Verificar que el foco permanece visible.
4. Reducir la ventana a 360 px de ancho.
5. Verificar que ninguna vista genera desplazamiento horizontal.

## Comprobación final

Antes de considerar la feature lista, ejecutar desde `frontend/`:

```powershell
npm run lint
npm run typecheck
npm test
```

Los tres comandos deben terminar sin errores.


