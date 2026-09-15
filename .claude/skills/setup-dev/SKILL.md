---
name: setup-dev
description: Levanta el entorno de desarrollo del backend desde cero — venv, dependencias, .env, docker-compose, migraciones — y verifica que /health responda. Úsala la primera vez que alguien clona el repo, o para reproducir la verificación de B01-B09 de Grupo 0 sin depender de pasos hechos a mano en otra sesión.
disable-model-invocation: true
---

# Arranque del entorno de desarrollo (backend)

Reproduce, en orden, todo lo que Grupo 0 (`specs/001-prediccion-partido/tasks.md`,
`B01`-`B09`) exige que funcione sin pasos manuales no documentados. Si un paso falla,
parás ahí y lo mostrás — no sigas al siguiente adivinando que va a andar.

## 0. Prerequisitos

- Docker Desktop corriendo (`docker info` no debe dar error de conexión al engine).
- Python ≥3.12 (`python --version`).

## 1. Levantar Postgres + Redis

```bash
docker compose -f infra/docker-compose.yml up -d
```

Esperá a que ambos healthchecks pasen antes de seguir:

```bash
docker compose -f infra/docker-compose.yml ps
```

Los dos servicios deben decir `(healthy)`, no solo `Up`.

## 2. Crear el venv e instalar dependencias

Desde `backend/`:

```bash
python -m venv .venv
```

Windows:
```bash
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
```
POSIX:
```bash
./.venv/bin/python -m pip install -e ".[dev]"
```

Si esto falla con "Multiple top-level packages discovered in a flat-layout", revisá que
`[tool.setuptools] packages = []` siga en `backend/pyproject.toml` — sin eso, setuptools
intenta adivinar cuál de `backend/app`, `backend/ml`, `backend/rag`, `backend/workers` es
"el" paquete y se niega.

## 3. Variables de entorno

```bash
cp backend/.env.example backend/.env
```

Los valores de ejemplo ya coinciden con las credenciales por defecto de
`infra/docker-compose.yml` — no hace falta editarlos para desarrollo local.

## 4. Migraciones

Desde `backend/`, con el venv activo:

```bash
python -m alembic upgrade head
```

Debe aplicar la revisión que habilita `CREATE EXTENSION vector` sin error.

## 5. Verificación

```bash
python -m pytest -q
```

Se esperan fallos **solo** en los tests marcados `pendiente_implementacion`
(`backend/ml/evaluation/test_split_cronologico.py`,
`backend/ml/features/test_no_odds_en_feature_set.py`) — son la fase Red del Artículo III,
documentada en `CLAUDE.md`. Cualquier otro fallo es un problema real de este entorno, no
algo esperado.

Por último, levantá la app y confirmá `/health` a mano:

```bash
python -m uvicorn app.main:app --port 8000 &
curl http://localhost:8000/health   # -> {"status":"ok"}
```

## 6. Si algo de esto no reprodujo el entorno completo

Es un hallazgo real, no un detalle — decíselo al usuario explícitamente: `B09` de
Grupo 0 exige justamente que este camino sea completo y sin pasos ocultos. No lo arregles
en silencio agregando un paso que no está en esta skill; actualizá esta skill (y
`quickstart.md` si aplica) para que el próximo que la corra no tropiece con lo mismo.
