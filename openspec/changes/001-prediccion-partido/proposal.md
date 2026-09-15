# Change: prediccion-partido

## Why
Para aficionados y analistas amateur de fútbol que quieren entender —no solo adivinar— qué puede pasar en un partido (pilar 1 del product goal), el sistema hoy no tiene ninguna forma de mostrar probabilidades de resultado. Sin esta capacidad el producto no tiene razón de ser: es la funcionalidad núcleo mínima sobre la que se apoyan las otras dos (explicación en lenguaje natural y track record público).

## What Changes
- **Predicción 1X2**: probabilidad de victoria local/empate/visitante por partido, calculada por el ensamble Dixon-Coles + XGBoost (promedio ponderado, pesos ajustados por backtesting).
- **Predicción Over/Under 2.5**: probabilidad de más/menos de 2.5 goles totales — única línea en este alcance; otras líneas (1.5, 3.5) quedan explícitamente fuera.
- **Predicción BTTS**: probabilidad de que ambos equipos anoten.
- **xG por equipo**: goles esperados calculados por el modelo propio, no histórico.
- **Nivel de confianza calibrado**: badge Alta/Media/Baja derivado de precisión histórica real (backtesting cronológico); "Baja" por defecto si un rango de probabilidad aún no tiene calibración suficiente.
- **Avisos de honestidad**: aviso visible de baja confiabilidad cuando el historial de un equipo es insuficiente; indicador cuando no hay head-to-head disponible.
- Cobertura: las 5 grandes ligas (Premier League, LaLiga, Serie A, Bundesliga, Ligue 1); predicción disponible al menos 24h antes del kickoff.

## Impact
- **Specs afectadas:** `prediccion-partido` (capability nueva — no existe aún en `openspec/specs/`, hoy vive solo como propuesta)
- **Código afectado:** `backend/ml/ensemble/`, `backend/ml/evaluation/calibration.py`, `backend/app/models/{partido,equipo,prediccion,calibracion_historica}.py`, `backend/app/services/predictions_service.py`, `backend/app/api/matches.py`, `backend/workers/tasks/generate_predictions.py`
- **Dependencias:** ninguna — es la primera capability del proyecto; `explicacion-lenguaje-natural` y `track-record-publico` dependen de esta (consumen `Predicción.top_shap_features` y `Predicción.version_modelo` respectivamente).
- **Datos:** requiere Football-Data.co.uk + Kaggle European Soccer Database ya cargados (Sprint 0-1, sección 6.2 de `docs/project_spec.md`).
- **No negociables constitucionales que aplican:** split cronológico obligatorio en el entrenamiento (nunca ver el futuro) y prohibición de usar columnas de cuotas como feature — ambos ya verificados por tests existentes en `backend/ml/evaluation/` y `backend/ml/features/` (ver `openspec/project.md`).

---
*Migrado desde `specs/001-prediccion-partido/spec.md` (formato spec-kit) al adoptar OpenSpec. El detalle completo de historias de usuario, escenarios Dado/Cuando/Entonces y criterios de éxito vive ahora en `specs/prediccion-partido/spec.md` (delta spec de este change, no en este proposal). Las decisiones técnicas y los gates de la Fase -1 viven en `design.md`. Las tareas ejecutables viven en `tasks.md` (idéntico al `tasks.md` ya auditado en Analyze).*
