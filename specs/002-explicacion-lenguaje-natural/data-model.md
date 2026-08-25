# Modelo de datos: Explicación en Lenguaje Natural

**Basado en:** `specs/002-explicacion-lenguaje-natural/spec.md` y `plan.md`

## Explicación
Relación 1:1 con `Predicción` (entidad de 001-prediccion-partido).

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| prediccion_id | FK → Predicción (001) | único |
| texto | text | Explicación en lenguaje natural, español |
| evidencia_citada_ids | array de FK → Evidencia | Solo evidencia con `fecha_publicacion < fecha_kickoff` del partido |
| es_fallback_sin_evidencia | boolean | true si se usó el mensaje de ausencia de datos (Historia 2) |
| shap_features_usadas | JSON | Copia de `top_shap_features` de la Predicción, congelada al momento de generación (trazabilidad) |
| generado_en | datetime | |
| actualizado_en | datetime | Se actualiza solo si se regenera por cambio de evidencia (sección 7.7) |

## Evidencia (noticia indexada)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| texto_sanitizado | text | Ya pasó por `rag/ingestion/` (sección 7.5) |
| fecha_publicacion | datetime | Verificada contra `fecha_kickoff` del partido en cada query de retrieval (7.3) |
| embedding | vector (Titan V2) | Índice HNSW en pgvector |
| equipo_relacionado_id | FK → Equipo (001), opcional | |
| partido_relacionado_id | FK → Partido (001), opcional | |
| fuente | string | News API / RSS |

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
Explicación (N) ──> Evidencia (N, vía evidencia_citada_ids)
```
