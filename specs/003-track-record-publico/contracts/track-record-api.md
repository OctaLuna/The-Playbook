# Contrato de API: Track Record Público

**Basado en:** `specs/003-track-record-publico/plan.md`

## GET /api/track-record
Query params: `league` (opcional; si se omite, devuelve el agregado global).

**Response 200**
```json
{
  "league": "premier_league",
  "window_size": 50,
  "hit_rate": 0.54,
  "avg_brier_score": 0.19,
  "avg_log_loss": 0.61,
  "avg_market_log_loss": 0.58,
  "matches_included": 50,
  "last_updated_at": "2026-08-24T03:00:00Z"
}
```
Nota: `avg_market_log_loss` puede calcularse sobre menos de `matches_included` partidos si alguno no tenía cuota de mercado disponible (caso límite resuelto) — no se expone ese detalle numérico en este contrato para no sobrecargar la respuesta; si se necesita, está disponible vía el endpoint de detalle.

## GET /api/track-record/matches
Query params: `league` (opcional), `page`, `page_size`.

**Response 200**
```json
{
  "matches": [
    {
      "match_id": "uuid",
      "league": "premier_league",
      "home_team": "Arsenal",
      "away_team": "Chelsea",
      "kickoff_at": "2026-08-16T14:00:00Z",
      "predicted_1x2": { "home": 0.48, "draw": 0.27, "away": 0.25 },
      "real_result": { "home_goals": 2, "away_goals": 1 },
      "hit_1x2": true,
      "model_version": "xgb-ensemble-2026.08.1"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 50
}
```

Nota: ningún endpoint de este contrato expone cuotas de casas de apuestas individuales ni un comparador independiente — solo el agregado `avg_market_log_loss` como referencia de baseline (RF-005, fuera de alcance según sección 2.4 de project_spec.md).
