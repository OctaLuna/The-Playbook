# Contrato de API: Explicaciones en Lenguaje Natural

**Basado en:** `specs/002-explicacion-lenguaje-natural/plan.md`

## GET /api/matches/{match_id}/explanation
Requiere que exista una Predicción para ese partido (001); si no existe, 404.

**Response 200**
```json
{
  "match_id": "uuid",
  "text": "El modelo favorece al local principalmente por su forma reciente (4 victorias en los últimos 5 partidos)...",
  "is_fallback_no_evidence": false,
  "evidence": [
    { "id": "uuid", "source": "News API", "published_at": "2026-08-27T10:00:00Z" }
  ],
  "generated_at": "2026-08-29T06:05:00Z",
  "updated_at": "2026-08-29T06:05:00Z"
}
```
**Response 404** si el partido no tiene predicción generada aún.

## POST /api/matches/{match_id}/explanation/follow-up
**Request**
```json
{ "question": "¿Por qué pesa tanto la lesión del delantero?" }
```

**Response 200**
```json
{
  "match_id": "uuid",
  "question": "¿Por qué pesa tanto la lesión del delantero?",
  "answer": "Porque el delantero concentra el 40% del xG del equipo en los últimos 5 partidos según las variables SHAP de esta predicción...",
  "generated_at": "2026-08-29T10:12:00Z"
}
```
**Response 404** si no existe una explicación previa generada para ese partido (la pregunta de seguimiento requiere una Explicación inicial ya generada, Historia 4).

Nota: ninguno de los dos endpoints acepta un parámetro de idioma — el MVP es español-only (decisión de Clarify).
