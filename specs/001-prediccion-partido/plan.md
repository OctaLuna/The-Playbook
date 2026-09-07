# Plan de implementación: Predicción de Partido (1X2, Over/Under, BTTS, xG y Confianza)

**Basado en:** `specs/001-prediccion-partido/spec.md`
**Stack propuesto por el usuario:** El definido en `docs/project_spec.md` (secciones 4 y 5) — FastAPI (Python 3.12) + SQLAlchemy 2.0 async + Alembic sobre PostgreSQL 16, Celery + Redis para jobs en background, statsmodels (Dixon-Coles) + XGBoost con capa de ensamble propia, SHAP (TreeExplainer) para explicabilidad interna, Next.js 15 + TypeScript + TanStack Query + Recharts en el frontend.

## Resumen técnico

Esta feature calcula y expone, para cada partido próximo de las cinco grandes ligas, cuatro señales (1X2, Over/Under 2.5, BTTS, xG por equipo) más un nivel de confianza calibrado. El cálculo lo hacen dos modelos — Dixon-Coles como prior estadístico y XGBoost sobre features adicionales — combinados por promedio ponderado (sección 6.4 de project_spec.md), siempre respetando el split cronológico obligatorio (Artículo IV de la constitución). El resultado, junto con los top-N valores SHAP del modelo XGBoost, se persiste en PostgreSQL como una `Predicción` asociada a un `Partido`.

Todo el cálculo corre como tarea de Celery (nunca síncrono dentro de un request HTTP, Artículo VI): un job periódico genera predicciones para los partidos que entran en la ventana de 24 horas antes de kickoff (RF-007 del spec). El backend FastAPI solo lee predicciones ya calculadas — los endpoints de `backend/app/api/matches` son delgados y no ejecutan ML directamente, delegando a `backend/app/services/predictions_service.py`, que a su vez llama a `backend/ml/ensemble/predict.py`.

El nivel de confianza (Alta/Media/Baja) se deriva de una tabla de calibración empírica (`Calibración histórica`) generada por el backtesting cronológico (sección 6.5); si un rango de probabilidad aún no tiene suficientes observaciones de backtesting, se asigna Baja por defecto (decisión ya resuelta en el spec).

## Fase -1: Gates previos a la implementación

### Gate de simplicidad (Artículo VII)
- [x] ¿Se usan ≤3 proyectos/módulos? Sí — todo vive dentro del monorepo backend existente (`backend/app/`, `backend/ml/`, `backend/workers/`), sin proyectos nuevos.
- [x] ¿No hay "future-proofing"? Sí — solo se implementa la línea O/U 2.5 (no 1.5/3.5) y las 5 ligas ya decididas; sin código especulativo para líneas o ligas futuras.

### Gate anti-abstracción (Artículo VIII)
- [x] ¿Se usa el framework directamente? Sí — modelos SQLAlchemy y schemas Pydantic directos, sin capas de repositorio genérico innecesarias.
- [x] ¿Una sola representación del modelo de datos? Sí — el schema Pydantic de `Predicción` es el mismo contrato que consume el frontend, generado desde el modelo SQLAlchemy.

### Gate integration-first (Artículo IX)
- [x] ¿Los contratos (API/eventos) están definidos? Sí — ver `contracts/matches-api.md`.
- [x] ¿Existen o están planeadas pruebas de contrato? Sí — pruebas de contrato para los 4 endpoints antes de implementar los routers (ver orden de archivos abajo).

### Cumplimiento constitucional (Artículos IV-VI del proyecto)
- [x] **Artículo IV (Integridad Temporal):** el entrenamiento de Dixon-Coles/XGBoost usa split cronológico (verificado por el test existente en `backend/ml/evaluation/`); la calibración del badge de confianza usa solo backtesting cronológico, nunca resultados futuros al momento de predecir.
- [x] **Artículo V (Independencia del Mercado):** el feature set de esta predicción NO incluye ninguna columna derivada de cuotas (verificado por el test existente en `backend/ml/features/`); esta feature no expone ni consume cuotas de mercado en absoluto (eso vive solo en 003-track-record-publico).
- [x] **Artículo VI (Aislamiento de Procesos):** la generación de predicciones corre exclusivamente como tarea Celery (`backend/workers/tasks/generate_predictions.py`); los endpoints de `backend/app/api/matches` solo leen de PostgreSQL, nunca ejecutan el pipeline de ML de forma síncrona.

## Decisiones técnicas y su porqué

| Decisión | Alternativas consideradas | Por qué esta opción | Requisito que satisface |
|---|---|---|---|
| Ensamble Dixon-Coles + XGBoost por promedio ponderado (pesos ajustados por backtesting) | Solo XGBoost; solo Dixon-Coles; stacking con meta-modelo | Balance entre interpretabilidad (Dixon-Coles como ancla) y poder predictivo (XGBoost); pesos auditables en MLflow (sección 6.4 project_spec.md) | RF-001, RF-002, RF-003 |
| Generación batch vía Celery, ventana de 24h antes del kickoff | Generar on-demand al abrir la ficha del partido | Evita latencia de ML en el path de request HTTP (Artículo VI); permite cachear y servir instantáneamente | RF-007 |
| Tabla de `Calibración histórica` como lookup por (mercado, rango de probabilidad) → precisión empírica | Calcular calibración on-the-fly en cada request | Se recalcula una vez por reentrenamiento (Celery), no en cada lectura; consistente con el criterio de reentrenamiento de la sección 6.5 | RF-005 |
| Badge "Baja" por defecto cuando no hay calibración suficiente | Ocultar el badge; mostrar "N/D" | Decisión ya tomada en Clarify — postura conservadora en vez de ausencia de información | Historia 4, escenario 2 |
| Persistir top-N SHAP values junto a la Predicción (campo interno, no expuesto por defecto en la API pública) | Recalcular SHAP en el momento en que 002 lo necesite | Evita recomputar SHAP dos veces; el mismo pipeline que genera la predicción ya tiene el modelo XGBoost cargado (sección 8) | Prepara la integración con 002-explicacion-lenguaje-natural |
| Endpoints de solo lectura en `backend/app/api/matches`, lógica en `backend/app/services/predictions_service.py` | Lógica directamente en los routers | Cumple la regla de estructura de la sección 10 del project_spec.md y el Artículo I (Library-First) | Todos los RF |

## Modelo de datos (resumen — detalle en data-model.md)
Cuatro entidades: `Partido` (con estado programado/jugado/pospuesto/cancelado), `Equipo`, `Predicción` (1:1 con Partido, contiene las cuatro señales + confianza + SHAP interno + versión de modelo) y `Calibración histórica` (tabla de lookup independiente, no asociada a un partido específico). El detalle completo, con tipos y relaciones, está en `data-model.md`.

## Contratos (resumen — detalle en contracts/)
Cuatro endpoints de solo lectura: listar ligas cubiertas, listar próximos partidos (filtrable por liga), detalle de un partido, y la predicción de un partido. El detalle completo de request/response está en `contracts/matches-api.md`.

## Orden de creación de archivos (test-first, obligatorio)

0. **Arranque del stack (Grupo 0 de `tasks.md`, tareas B01-B09).** Nada de lo que sigue es
   escribible sin esto: las pruebas de contrato necesitan una app FastAPI que importar y un
   Postgres real contra el que correr (Artículo IX). En orden: dependencias en
   `backend/pyproject.toml` → `infra/docker-compose.yml` → `backend/app/core/config.py` →
   `backend/app/db/session.py` → fixtures de `backend/tests/conftest.py` → prueba de `/health`
   **en rojo** → `backend/app/main.py` → Alembic.
1. `contracts/matches-api.md` — ya definido en este plan.
2. Tests, en este orden:
   - Pruebas de contrato de los 4 endpoints (`backend/tests/contract/test_matches_api.py`)
   - Prueba de integración: generación de predicción vía Celery task y su persistencia (`backend/tests/integration/test_generate_predictions.py`)
   - Reutilizar el test existente en `backend/ml/features/` que verifica que ninguna columna de odds llega al feature set
   - Pruebas unitarias de la capa de ensamble y de la asignación de badge de confianza (`backend/tests/unit/`)
3. Código fuente, en este orden: modelos SQLAlchemy → schemas Pydantic → `backend/ml/ensemble/predict.py` → `backend/app/services/predictions_service.py` → `backend/workers/tasks/generate_predictions.py` → routers de `backend/app/api/matches`.

## Registro de complejidad
Ningún gate de la Fase -1 falló — no aplica registro de complejidad.

## Validación / Quickstart (resumen — detalle en quickstart.md)
Los escenarios clave: (1) ver las 4 señales de un partido próximo con datos suficientes, (2) ver el aviso de baja confiabilidad en un partido con datos insuficientes, (3) verificar que una línea O/U distinta a 2.5 no es un caso soportado, (4) verificar que la predicción de un partido pospuesto sigue visible con su marca de estado, (5) verificar el aviso de head-to-head no disponible. Detalle paso a paso en `quickstart.md`.
