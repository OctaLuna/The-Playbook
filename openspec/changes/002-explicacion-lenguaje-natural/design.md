# Design: explicacion-lenguaje-natural

**Referencia completa:** `specs/002-explicacion-lenguaje-natural/plan.md`, `data-model.md`, `contracts/explanations-api.md` (spec-kit) — resumen orientado a OpenSpec; el detalle completo no se duplica aquí.

## Resumen técnico
Para cada `Predicción` ya calculada (001), se genera una explicación anclada a dos fuentes: noticias pre-partido recuperadas vía RAG con filtro temporal obligatorio (`fecha_publicacion_noticia < fecha_kickoff_del_partido`), y los `top_shap_features` ya persistidos en la Predicción. Pipeline en `rag/ingestion/` (scraping + chunking + sanitización), `rag/retrieval/` (queries a pgvector con el filtro temporal) y `rag/generation/` (prompts versionados, cliente Bedrock Converse API, caché Redis). La ingesta corre vía Celery, nunca síncrona. Las preguntas de seguimiento reutilizan el mismo contexto de evidencia/SHAP que la generación inicial.

## Gates de simplicidad y arquitectura (ver `../../project.md`)
- ≤3 módulos: `rag/ingestion`, `rag/retrieval`, `rag/generation` son submódulos de un único módulo `rag/`.
- Sin future-proofing: sin soporte multi-idioma (español-only ya decidido); sin motor de conversación de propósito general.
- Framework directo: LangChain sin envoltura adicional; Bedrock vía Converse API directo.
- Integration-first: el test del filtro temporal corre contra pgvector real, sin excepción (ver Registro de complejidad).

## Cumplimiento de convenciones no negociables
- **Integridad temporal:** filtro temporal a nivel de query SQL, verificado por test de integración con caso construido a propósito — no negociable, sin excepción.
- **Independencia del mercado:** no aplica — esta capability no usa cuotas de mercado en ningún punto.
- **Aislamiento de procesos y seguridad de ingesta:** scraping/reindexado vía Celery; contenido no confiable delimitado en bloque XML en el prompt + sanitización previa; el LLM nunca ejecuta acciones ni código a partir de contenido indexado.

## Decisiones técnicas clave
| Decisión | Por qué |
|---|---|
| Filtro temporal a nivel de query SQL, no post-filtro en memoria | Garantiza que la restricción no se pueda "olvidar" en un nuevo punto de retrieval |
| Chunking por artículo completo (overlap 15-20% si excede ~500 tokens) | Las noticias pre-partido son cortas; fragmentar pierde contexto |
| Contenido scrapeado delimitado en bloque XML + instrucción de sistema que lo ignora como comando | Mitigación estándar de prompt injection |
| Caché de explicaciones en Redis, invalidado solo si cambia la evidencia | Controla costo de Bedrock sin servir explicaciones desactualizadas |
| Preguntas de seguimiento sobre el mismo contexto ya recuperado (sin nueva búsqueda RAG por defecto) | Evita que una nueva búsqueda rompa el filtro temporal por descuido |

Detalle completo de alternativas consideradas: `specs/002-explicacion-lenguaje-natural/plan.md`.

## Modelo de datos y contratos
Ver `specs/002-explicacion-lenguaje-natural/data-model.md` (`Explicación`, `Evidencia`, `PreguntaSeguimiento`) y `contracts/explanations-api.md` (2 endpoints). No se duplican aquí.

## Registro de complejidad
| Gate que falló | Por qué fue necesario | Alternativa descartada |
|---|---|---|
| Integration-first (parcial) | Las pruebas unitarias de generación usan un stub de Bedrock para no incurrir en costo/latencia en cada corrida de CI; el test del filtro temporal SÍ corre contra pgvector real, sin excepción | Se descartó mockear también el test del filtro temporal — es el test crítico de integridad temporal exigido por convención #1 |
