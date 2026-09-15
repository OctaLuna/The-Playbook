# Contrato de API: Partidos y Predicciones

**Basado en:** `specs/001-prediccion-partido/plan.md`
Todos los endpoints son de solo lectura (GET). Formato de respuesta: JSON, contratos definidos como Pydantic schemas en `backend/app/schemas/`.

## GET /api/leagues
Lista las ligas cubiertas en el MVP.

**Response 200**
```json
{
  "leagues": [
    { "id": "premier_league", "name": "Premier League" },
    { "id": "laliga", "name": "LaLiga" },
    { "id": "serie_a", "name": "Serie A" },
    { "id": "bundesliga", "name": "Bundesliga" },
    { "id": "ligue_1", "name": "Ligue 1" }
  ]
}
```

## GET /api/matches/upcoming
Query params: `league` (opcional), `from`, `to` (opcional, default: próximos 7 días), `page`, `page_size`.

**Response 200**
```json
{
  "matches": [
    {
      "id": "uuid",
      "league": "premier_league",
      "home_team": "Arsenal",
      "away_team": "Chelsea",
      "kickoff_at": "2026-08-30T14:00:00Z",
      "status": "scheduled",
      "has_prediction": true
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 42
}
```

## GET /api/matches/{match_id}
**Response 200**
```json
{
  "id": "uuid",
  "league": "premier_league",
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "kickoff_at": "2026-08-30T14:00:00Z",
  "status": "scheduled",
  "real_result": null
}
```
**Response 404** si el partido no existe.

## GET /api/matches/{match_id}/prediction
**Response 200**
```json
{
  "match_id": "uuid",
  "probabilities_1x2": { "home": 0.48, "draw": 0.27, "away": 0.25 },
  "over_under_2_5": { "over": 0.58, "under": 0.42 },
  "btts": { "yes": 0.55, "no": 0.45 },
  "xg": { "home": 1.62, "away": 1.11 },
  "confidence": "media",
  "head_to_head_available": false,
  "low_data_warning": false,
  "model_version": "xgb-ensemble-2026.08.1",
  "generated_at": "2026-08-29T06:00:00Z"
}
```
**Response 404** si el partido no tiene predicción generada aún (ej. fuera de la ventana de 24h, RF-007).

Nota: `top_shap_features` NO se incluye en este contrato público — es un campo interno consumido por `backend/app/services/` para 002-explicacion-lenguaje-natural, no se expone al frontend en este endpoint.
