# Design: prediccion-partido

**Referencia completa:** `specs/001-prediccion-partido/plan.md`, `data-model.md`, `contracts/matches-api.md` (spec-kit) — este documento es un resumen orientado a OpenSpec; el detalle de campos, tipos y contratos de API completos vive en esos archivos, no se duplica aquí.

## Resumen técnico
Se calculan y exponen, para cada partido próximo de las 5 grandes ligas, cuatro señales (1X2, O/U 2.5, BTTS, xG) más un nivel de confianza calibrado. El cálculo lo hacen dos modelos — Dixon-Coles (prior estadístico) y XGBoost (features adicionales) — combinados por promedio ponderado ajustado por backtesting cronológico. Todo el cálculo corre vía Celery (nunca síncrono en el request HTTP); el API solo lee predicciones ya persistidas.

## Gates de simplicidad y arquitectura (ver `../../project.md`)
- ≤3 módulos: todo vive en `app/`, `ml/`, `workers/` del monorepo existente — sin proyectos nuevos.
- Sin future-proofing: solo línea O/U 2.5 y las 5 ligas ya decididas; nada especulativo.
- Framework directo: SQLAlchemy/Pydantic sin capas de envoltura innecesarias.
- Integration-first: contratos definidos en `contracts/matches-api.md`, pruebas de contrato antes de implementar routers.

## Cumplimiento de convenciones no negociables
- **Integridad temporal:** entrenamiento con split cronológico (test existente en `ml/evaluation/`); calibración del badge de confianza usa solo backtesting cronológico, nunca resultados futuros.
- **Independencia del mercado:** el feature set no incluye columnas de odds (test existente en `ml/features/`); esta capability no consume cuotas de mercado en absoluto.
- **Aislamiento de procesos:** generación de predicciones vía `workers/tasks/generate_predictions.py` (Celery); `app/api/matches` es de solo lectura.

## Decisiones técnicas clave
| Decisión | Por qué |
|---|---|
| Ensamble Dixon-Coles + XGBoost, pesos ajustados por backtesting | Balance interpretabilidad/poder predictivo; pesos auditables en MLflow |
| Generación batch vía Celery, ventana 24h antes del kickoff | Evita latencia de ML en el path de request HTTP |
| Tabla de Calibración histórica como lookup, recalculada por reentrenamiento | Evita recalcular calibración en cada lectura |
| Badge "Baja" por defecto sin calibración suficiente | Postura conservadora ante ausencia de información |
| `top_shap_features` persistido junto a la Predicción (campo interno) | Evita recomputar SHAP dos veces; lo consume `explicacion-lenguaje-natural` |

Detalle completo de alternativas consideradas y requisito satisfecho por cada decisión: `specs/001-prediccion-partido/plan.md`.

## Modelo de datos y contratos
Ver `specs/001-prediccion-partido/data-model.md` (entidades `Partido`, `Equipo`, `Predicción`, `Calibración histórica`) y `specs/001-prediccion-partido/contracts/matches-api.md` (4 endpoints GET). No se duplican aquí para evitar que las dos copias se desalineen.

## Registro de complejidad
Ningún gate falló — no aplica.
