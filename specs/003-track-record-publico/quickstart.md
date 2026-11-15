# Quickstart: Validación manual de Track Record Público

**Basado en:** `specs/003-track-record-publico/spec.md`, `plan.md` y `contracts/track-record-api.md`.

Este documento describe la secuencia paso a paso para validar manualmente el funcionamiento de la Feature 003: Track Record Público del Modelo.

---

## Preparar el entorno

1. **Iniciar servicios de infraestructura** (desde la raíz del repositorio):
   ```powershell
   docker compose -f infra/docker-compose.yml up -d postgres redis
   ```

2. **Aplicar migraciones** (desde `backend/`):
   ```powershell
   alembic upgrade head
   ```

3. **Iniciar la API** (desde `backend/`):
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

4. **Ejecutar el recálculo periódico del track record**:
   La tarea corre automáticamente todos los días a las 03:00 UTC vía Celery Beat. Para forzar una ejecución manual inmediata en Python:
   ```powershell
   python -c "import asyncio; from app.db.session import async_session_factory; from workers.tasks.update_track_record import actualizar_track_record_job; asyncio.run(async_session_factory().__aenter__().then(lambda s: actualizar_track_record_job(s)))"
   ```
   O vía Celery:
   ```powershell
   python -c "from workers.tasks.update_track_record import update_track_record; print(update_track_record.delay().get(timeout=30))"
   ```

---

## Escenarios de validación manual

### Escenario 1 — Ver el agregado de los últimos 50 partidos (RF-001, RF-002, RF-006)
1. Consultar el endpoint público global:
   ```powershell
   curl -s http://localhost:8000/api/track-record | ConvertFrom-Json
   ```
2. **Verificar:**
   * `window_size` es `50`.
   * `matches_included` indica la muestra real disponible ($\le 50$, RF-009).
   * `markets` contiene exactamente 3 elementos: `1x2`, `over_under_2_5` y `btts`.
   * Cada mercado expone `hit_rate`, `avg_brier_score` y `avg_log_loss`.
   * `last_updated_at` muestra la marca temporal del último cálculo.

### Escenario 2 — Auditar el detalle partido a partido (RF-003)
1. Consultar la lista paginada de partidos evaluados:
   ```powershell
   curl -s "http://localhost:8000/api/track-record/matches?page=1&page_size=10" | ConvertFrom-Json
   ```
2. **Verificar:**
   * Cada partido incluye `real_result` (`home_goals` y `away_goals`).
   * Se muestran las 3 predicciones originales (`predicted_1x2`, `predicted_over_under_2_5`, `predicted_btts`).
   * Los aciertos booleanos (`hit_1x2`, `hit_over_under_2_5`, `hit_btts`) coinciden exactamente con la comparación entre predicción y resultado real.
   * `model_version` preserva la versión del modelo que generó la predicción original.

### Escenario 3 — Comparación de log-loss vs. baseline de mercado (RF-004, RF-005)
1. Consultar `GET /api/track-record`:
2. **Verificar:**
   * En la entrada de mercado `1x2`: `avg_market_log_loss` tiene un valor numérico comparable y `market_baseline_matches` indica cuántos partidos contaban con cuota.
   * En `over_under_2_5` y `btts`: `avg_market_log_loss` es estrictamente `null` y `market_baseline_matches = 0`.
   * Ningún campo expone cuotas crudas ni casas de apuestas individuales (cumplimiento del Artículo V).

### Escenario 4 — Partidos pospuestos o cancelados no cuentan (RF-011)
1. Con un partido en estado `pospuesto` o `cancelado`, ejecutar el job de actualización.
2. **Verificar:** El partido no suma en `matches_included` ni distorsiona métricas hasta que pase a estado `jugado` con goles registrados.

### Escenario 5 — Partido sin cuota de mercado cuenta para hit rate (RF-004)
1. Para partidos de ligas o fechas sin cuota de mercado registrada (`tiene_cuota_mercado = false`).
2. **Verificar:** El partido computa normalmente en `hit_rate`, `avg_brier_score` y `avg_log_loss` del modelo, pero se descuenta de `market_baseline_matches`.

### Escenario 6 — Filtrado por liga (RF-007)
1. Consultar el agregado filtrado por liga:
   ```powershell
   curl -s "http://localhost:8000/api/track-record?league=premier_league" | ConvertFrom-Json
   curl -s "http://localhost:8000/api/track-record/matches?league=premier_league" | ConvertFrom-Json
   ```
2. **Verificar:** `league` en el JSON devuelto es `"premier_league"` y las métricas computan únicamente los partidos correspondientes a esa competición.
