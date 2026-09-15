# Plan de implementación: Explicación en Lenguaje Natural de la Predicción

**Basado en:** `specs/002-explicacion-lenguaje-natural/spec.md`
**Stack propuesto por el usuario:** El definido en `docs/project_spec.md` (secciones 5.1 y 7) — LangChain para orquestación de RAG, AWS Bedrock (Claude) vía `boto3`/`bedrock-runtime` con Converse API, Amazon Titan Text Embeddings V2, pgvector (índice HNSW) sobre PostgreSQL, Redis para caché de explicaciones, Celery para ingesta/reindexado.

## Resumen técnico

Esta feature genera, para cada partido con predicción ya calculada (001-prediccion-partido), una explicación en lenguaje natural que combina dos anclas: la evidencia textual recuperada por RAG (noticias pre-partido) y los top-N valores SHAP de la predicción XGBoost (ya persistidos por 001). El pipeline vive en `backend/rag/ingestion/` (scraping + chunking + sanitización, sección 7.1 + Artículo VI de la constitución), `backend/rag/retrieval/` (queries a pgvector con el filtro temporal obligatorio, sección 7.3) y `backend/rag/generation/` (prompt versionado + cliente Bedrock, secciones 7.2, 7.5 y 7.6).

Toda query de retrieval aplica `WHERE fecha_publicacion_noticia < fecha_kickoff_del_partido` sin excepción (Artículo IV). Si no hay evidencia suficiente, el LLM declara la ausencia en vez de inventar una justificación (Historia 2). Las explicaciones se cachean en Redis y solo se regeneran si cambia la evidencia subyacente (sección 7.5). La Historia 4 (preguntas de seguimiento) reutiliza el mismo contexto de evidencia y SHAP ya usado en la generación inicial — no dispara una nueva búsqueda de evidencia salvo que la pregunta lo requiera, y respeta las mismas reglas (nunca predice, nunca usa evidencia posterior al kickoff).

## Fase -1: Gates previos a la implementación

### Gate de simplicidad (Artículo VII)
- [x] ¿Se usan ≤3 proyectos/módulos? Sí — `backend/rag/` (3 submódulos: ingestion, retrieval, generation) vive dentro del mismo proyecto backend, sin desplegables nuevos.
- [x] ¿No hay "future-proofing"? Sí — no se construye soporte multi-idioma (MVP es español-only, ya resuelto) ni un límite configurable de preguntas de seguimiento más allá del rate-limiting ya existente en Redis.

### Gate anti-abstracción (Artículo VIII)
- [x] ¿Se usa el framework directamente? Sí — LangChain se usa tal como está pensado por el project_spec (orquestación de chunking/retrieval/prompting), sin una capa propia adicional por encima; el cliente Bedrock se invoca vía Converse API, sin envolver el SDK de `boto3`.
- [x] ¿Una sola representación del modelo de datos? Sí — la `Explicación` tiene un único schema Pydantic, reutilizado tanto para la generación inicial como para las respuestas de seguimiento (Historia 4).

### Gate integration-first (Artículo IX)
- [x] Contratos definidos — ver `contracts/explanations-api.md`.
- [~] Pruebas 100% contra servicios reales — **parcial, ver Registro de complejidad**: el test del filtro temporal obligatorio (7.3) SÍ corre contra una instancia real de Postgres/pgvector; las pruebas unitarias de generación usan un stub del cliente Bedrock para no incurrir en costo/latencia en cada corrida de CI, con un subconjunto reducido de pruebas de integración que sí llaman a Bedrock real.

### Cumplimiento constitucional (Artículos IV-VI del proyecto)
- [x] **Artículo IV:** filtro temporal obligatorio a nivel de query (7.3), verificado por test de integración con caso construido a propósito.
- [x] **Artículo V:** esta feature no usa cuotas de mercado en ningún punto del pipeline (ni en retrieval, ni en el prompt).
- [x] **Artículo VI:** la ingesta (scraping/reindexado) corre en `backend/workers/` vía Celery, nunca síncrona en un endpoint; la generación de la explicación inicial también se dispara por el mismo job que genera la predicción en 001, no dentro del request del usuario que la lee (se sirve desde caché o ya persistida).

## Decisiones técnicas y su porqué

| Decisión | Alternativas consideradas | Por qué esta opción | Requisito que satisface |
|---|---|---|---|
| LangChain para chunking/retrieval/prompting | Cliente Bedrock directo sin framework de orquestación | Pipeline reproducible y auditable (versionado de prompts), evita acoplar el backend a un formato específico de proveedor (sección 5.1) | RF-001 |
| Converse API de Bedrock, no la API nativa por modelo | API nativa de invocación por modelo | Normaliza el formato de mensajes; facilita comparar con otro modelo de Bedrock más adelante sin reescribir el backend | Decisión ya fijada en project_spec 5.1 |
| Filtro temporal a nivel de query SQL (`WHERE fecha_publicacion < fecha_kickoff`), no post-filtrado en memoria | Filtrar después de recibir los resultados de pgvector | Es una restricción de integridad, no una conveniencia — debe ser imposible de saltarse aunque cambie el código de generación (Artículo IV) | RF-002 |
| Cache en Redis, invalidado solo si cambia la evidencia indexada | Cachear por TTL fijo | Evita regenerar (costo de Bedrock) cuando no hay nada nuevo que decir; evita servir una explicación desactualizada cuando sí lo hay (sección 7.5) | Caso límite de indicador de última actualización |
| Preguntas de seguimiento como turno adicional sobre el mismo contexto ya recuperado (sin nueva búsqueda RAG por defecto) | Ejecutar una nueva búsqueda RAG completa por cada pregunta | Evita el riesgo de que una nueva búsqueda traiga evidencia que rompa el filtro temporal por un descuido de implementación; más barato en tokens/latencia | RF-005, Historia 4 |
| Contenido de noticias delimitado en bloque XML explícito en el prompt + sanitización previa (`backend/rag/ingestion/`) | Insertar el texto scrapeado directamente en el prompt | Mitiga prompt injection desde una fuente no confiable (Artículo VI de la constitución) | Artículo VI |

## Modelo de datos (resumen — detalle en data-model.md)
Tres entidades: `Explicación` (1:1 con Predicción de 001, contiene el texto, las citas de evidencia usadas y el timestamp de última actualización), `Evidencia` (noticia indexada, con fecha de publicación verificable contra el kickoff) y `PreguntaSeguimiento` (N:1 con Explicación, para la Historia 4). Detalle completo en `data-model.md`.

## Contratos (resumen — detalle en contracts/)
Dos endpoints: obtener la explicación de un partido, y enviar una pregunta de seguimiento sobre esa explicación. Detalle completo en `contracts/explanations-api.md`.

## Orden de creación de archivos (test-first, obligatorio)
1. `contracts/explanations-api.md` — ya definido en este plan.
2. Tests, en este orden:
   - Test de integración del filtro temporal (7.3) contra pgvector real, con caso construido a propósito (evidencia post-kickoff que nunca debe aparecer citada)
   - Pruebas de contrato de los 2 endpoints (`backend/tests/contract/test_explanations_api.py`)
   - Prueba de integración del fallback de evidencia insuficiente (Historia 2)
   - Pruebas unitarias de sanitización de ingesta (7.5) y de armado del prompt (inyección de SHAP values, sección 8)
3. Código fuente, en este orden: modelos SQLAlchemy (`Explicación`, `Evidencia`, `PreguntaSeguimiento`) → `backend/rag/ingestion/` → `backend/rag/retrieval/` (con el filtro temporal) → `backend/rag/generation/` (prompt + cliente Bedrock) → `backend/app/services/explanations_service.py` → routers de `backend/app/api/explanations`.

## Registro de complejidad
| Gate que falló | Por qué fue necesario | Alternativa más simple descartada y por qué |
|---|---|---|
| Integration-first (parcial, pruebas de generación LLM) | Llamar a Bedrock real en cada test unitario de CI sería lento y costoso (facturación por invocación) y no aporta señal adicional sobre la lógica de negocio (armado de prompt, fallback de evidencia insuficiente) | Se descartó mockear también el test del filtro temporal de pgvector (7.3): ese es el test crítico de integridad temporal exigido explícitamente en la sección 7.3 del spec técnico, y ahí sí se usa una base de datos real sin excepción |

## Validación / Quickstart (resumen — detalle en quickstart.md)
Los escenarios clave: (1) explicación generada con evidencia real disponible, (2) aviso honesto de evidencia insuficiente, (3) verificar que una noticia posterior al kickoff nunca aparece citada (caso construido a propósito), (4) hacer una pregunta de seguimiento y verificar que respeta las mismas reglas que la explicación inicial. Detalle paso a paso en `quickstart.md`.
