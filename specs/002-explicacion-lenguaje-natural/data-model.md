# Modelo de datos: Explicación en Lenguaje Natural

**Basado en:** `specs/002-explicacion-lenguaje-natural/spec.md` y `plan.md`

## Explicación
Relación 1:1 con `Predicción` (entidad de 001-prediccion-partido).

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| prediccion_id | FK → Predicción (001) | único |
| texto | text | Explicación en lenguaje natural, español |
| es_fallback_sin_evidencia | boolean | true si se usó el mensaje de ausencia de datos (Historia 2) |
| shap_features_usadas | JSON | Copia de `top_shap_features` de la Predicción, congelada al momento de generación (trazabilidad) |
| generado_en | datetime | |
| actualizado_en | datetime | Se actualiza solo si se regenera por cambio de evidencia (RF-006) |

## ExplicacionEvidencia (tabla puente)
Qué evidencia citó cada explicación. Es una tabla y no un array de identificadores dentro de
`Explicación`: PostgreSQL no aplica integridad referencial sobre los elementos de un array, así
que una evidencia borrada dejaría identificadores colgando sin que la base de datos lo impidiera.
El Artículo VIII pide además usar el framework directo, y esta es la relación N:M que SQLAlchemy
modela de forma nativa.

| Campo | Tipo | Notas |
|---|---|---|
| explicacion_id | FK → Explicación | PK compuesta |
| evidencia_id | FK → Evidencia | PK compuesta |
| orden | int | Posición de la cita en el texto, para renderizarlas en el mismo orden |

Toda fila aquí debe cumplir `Evidencia.fecha_publicacion < Partido.fecha_kickoff` (Artículo IV).
Es una invariante del servicio, verificada por la prueba de integración `T001`.

## Evidencia (noticia indexada)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| url | string | **Único.** Clave de deduplicación: `reindex_rag` corre periódicamente y sin esto reingestaría la misma noticia en cada pasada. Se expone en la API para que la evidencia sea verificable (pilar 2) |
| titulo | string | Titular del artículo. Se expone junto a la `url`: una cita sin titular ni enlace no es verificable por el usuario |
| texto_sanitizado | text | Ya pasó por `backend/rag/ingestion/` (Artículo VI de la constitución) |
| fecha_publicacion | datetime | NOT NULL. Verificada contra `fecha_kickoff` del partido en cada query de retrieval (sección 7.3) |
| embedding | **vector(1024)** | Amazon Titan Text Embeddings V2, dimensión por defecto. pgvector exige la dimensión en el DDL, así que fijarla aquí es requisito para poder escribir la migración `T008`. Índice HNSW |
| equipo_relacionado_id | FK → Equipo (001), opcional | |
| partido_relacionado_id | FK → Partido (001), opcional | |
| fuente | string | News API / RSS |

### Fuente de ingestión y mapeo de campos

`backend/workers/tasks/ingest_news.py` consulta el endpoint `/v2/everything` de News API por
cada equipo cubierto (query: nombre del equipo + liga, para acotar ruido). Cada artículo de la
respuesta trae este esquema JSON:

```json
{
  "title": "...",
  "url": "...",
  "publishedAt": "2026-08-27T10:00:00Z",
  "source": { "name": "..." },
  "content": "..."
}
```

| Campo de News API | Mapea a |
|---|---|
| `title` | `Evidencia.titulo` |
| `url` | `Evidencia.url` (clave de deduplicación) |
| `publishedAt` | `Evidencia.fecha_publicacion` — ya viene en ISO 8601 UTC, sin conversión |
| `source.name` | `Evidencia.fuente` |
| `content` | Entrada de `backend/rag/ingestion/sanitizer.py`, cuya salida es `Evidencia.texto_sanitizado` — **nunca** se persiste el `content` crudo, siempre pasa primero por el sanitizador (Artículo VI) |

Si un artículo no trae `publishedAt` (algunos artículos de agregadores lo omiten), se descarta
en la ingestión — un `NULL` ahí sería invisible al filtro temporal en vez de excluido por él, la
misma razón por la que `fecha_publicacion` es `NOT NULL` en la tabla.

El RSS de respaldo (cuando News API agota su cuota) sigue el mismo mapeo con los campos
equivalentes del formato RSS 2.0: `<title>` → `titulo`, `<link>` → `url`, `<pubDate>` →
`fecha_publicacion` (convertir de RFC 822 a UTC), `<description>` → entrada del sanitizador.

## PreguntaSeguimiento
N:1 con `Explicación` (Historia 4).

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| explicacion_id | FK → Explicación | |
| pregunta | text | |
| respuesta | text | Generada reutilizando el mismo contexto de evidencia y SHAP de la Explicación padre |
| generado_en | datetime | |

## Relaciones
```
Predicción (001) (1) ── (1) Explicación
Explicación (1) ──< PreguntaSeguimiento (N)
Explicación (N) >──< Evidencia (N, vía ExplicacionEvidencia)
Evidencia (N) ──> Equipo (001)   (opcional)
Evidencia (N) ──> Partido (001)  (opcional)
```

## Índices y restricciones

| Tabla | Restricción | Por qué |
|---|---|---|
| `Explicación` | `unique(prediccion_id)` | La relación es 1:1; sin esto nada impide dos explicaciones para la misma predicción |
| `Evidencia` | `unique(url)` | Deduplicación del reindexado periódico (`T018`) |
| `Evidencia` | `fecha_publicacion NOT NULL` | Sin fecha no se puede aplicar el filtro temporal del Artículo IV, y una fila sin ella sería invisible al filtro en vez de excluida |
| `Evidencia` | índice HNSW sobre `embedding` | Búsqueda vectorial (`T008`) |
| `Evidencia` | índice sobre `fecha_publicacion` | Toda query de retrieval filtra por este campo (sección 7.3) |
| `ExplicacionEvidencia` | PK compuesta `(explicacion_id, evidencia_id)` | Impide citar dos veces la misma evidencia en una explicación |
| `PreguntaSeguimiento` | índice sobre `explicacion_id` | Listado de preguntas por explicación |
