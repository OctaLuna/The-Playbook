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
    {
      "id": "uuid",
      "title": "El delantero del Chelsea, baja por lesión ante el Arsenal",
      "url": "https://ejemplo.com/noticia",
      "source": "News API",
      "published_at": "2026-08-27T10:00:00Z"
    }
  ],
  "generated_at": "2026-08-29T06:05:00Z",
  "updated_at": "2026-08-29T06:05:00Z"
}
```
**Response 404** si el partido no tiene predicción generada aún.

`title` y `url` no son adorno: el pilar 2 del product goal es evidencia **verificable**, y una
cita sin titular ni enlace no se puede verificar. Sin ellos el usuario tiene que creerse la
explicación, que es exactamente lo que este feature existe para evitar.

Toda entrada de `evidence` cumple `published_at < kickoff_at` del partido (Artículo IV). El
orden del array es el de la cita en el texto.

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
  "evidence": [
    {
      "id": "uuid",
      "title": "El delantero del Chelsea, baja por lesión ante el Arsenal",
      "url": "https://ejemplo.com/noticia",
      "source": "News API",
      "published_at": "2026-08-27T10:00:00Z"
    }
  ],
  "generated_at": "2026-08-29T10:12:00Z"
}
```
**Response 404** si no existe una explicación previa generada para ese partido (la pregunta de seguimiento requiere una Explicación inicial ya generada, Historia 4).

La respuesta devuelve la evidencia a la que se ancló, que siempre es un subconjunto de la de la
explicación original. RF-005 exige que la respuesta no introduzca evidencia nueva ni posterior al
kickoff; devolverla es lo que hace esa garantía verificable desde fuera, en vez de una promesa
que solo se puede comprobar leyendo el código del servicio.

Nota: ninguno de los dos endpoints acepta un parámetro de idioma — el MVP es español-only (decisión de Clarify).
