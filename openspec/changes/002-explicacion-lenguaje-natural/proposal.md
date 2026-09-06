# Change: explicacion-lenguaje-natural

## Why
Un número de probabilidad solo no le dice a un aficionado o analista amateur *por qué* el modelo predice lo que predice (pilar 2 del product goal). Sin una explicación anclada a evidencia real y verificable, el producto no se diferencia de un simple generador de cuotas — y pierde el diferencial declarado frente a la competencia (comparación honesta y trazabilidad predicción → evidencia).

## What Changes
- **Explicación en lenguaje natural** por partido, generada vía RAG (LangChain + AWS Bedrock/Claude), citando evidencia real (forma, lesiones, head-to-head) y las variables SHAP del modelo XGBoost que más influyeron.
- **Filtro temporal obligatorio**: ninguna explicación puede citar evidencia publicada después del kickoff del partido.
- **Aviso honesto de evidencia insuficiente**: si no hay cobertura mediática suficiente, se declara explícitamente en vez de inventar contexto.
- **Preguntas de seguimiento**: el usuario puede profundizar sobre una explicación ya generada, con las mismas garantías (misma evidencia, mismo filtro temporal).
- Producto español-only en este alcance; sin traducción a otros idiomas.

## Impact
- **Specs afectadas:** `explicacion-lenguaje-natural` (capability nueva)
- **Código afectado:** `backend/rag/ingestion/`, `backend/rag/retrieval/`, `backend/rag/generation/`, `backend/app/services/explanations_service.py`, `backend/app/api/explanations.py`, `backend/workers/tasks/{ingest_news,reindex_rag}.py`
- **Dependencias:** requiere `prediccion-partido` (001) ya implementada — consume `Predicción.top_shap_features`.
- **Riesgo de seguridad:** ingiere contenido externo no confiable (News API/RSS); requiere sanitización y delimitación explícita en el prompt para mitigar prompt injection (ver `../../project.md`, convención #4).

---
*Migrado desde `specs/002-explicacion-lenguaje-natural/spec.md` (formato spec-kit). Detalle completo de historias de usuario y criterios de éxito en `specs/002-explicacion-lenguaje-natural/spec.md`; decisiones técnicas en `design.md`; tareas ejecutables en `tasks.md`.*
