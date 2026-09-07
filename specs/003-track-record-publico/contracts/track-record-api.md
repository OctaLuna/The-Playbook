# Contrato de API: Track Record Público

**Basado en:** `specs/003-track-record-publico/plan.md`

## GET /api/track-record
Query params: `league` (opcional; si se omite, devuelve el agregado global).

**Response 200**
```json
{
  "league": "premier_league",
  "window_size": 50,
  "matches_included": 50,
  "model_versions": ["xgb-ensemble-2026.08.1"],
  "markets": [
    {
      "market": "1x2",
      "hit_rate": 0.54,
      "avg_brier_score": 0.19,
      "avg_log_loss": 0.61,
      "avg_market_log_loss": 0.58,
      "market_baseline_matches": 47
    },
    {
      "market": "over_under_2_5",
      "hit_rate": 0.61,
      "avg_brier_score": 0.22,
      "avg_log_loss": 0.65,
      "avg_market_log_loss": null,
      "market_baseline_matches": 0
    },
    {
      "market": "btts",
      "hit_rate": 0.58,
      "avg_brier_score": 0.23,
      "avg_log_loss": 0.67,
      "avg_market_log_loss": null,
      "market_baseline_matches": 0
    }
  ],
  "last_updated_at": "2026-08-24T03:00:00Z"
}
```

Notas del contrato:

- Se auditan los **tres mercados probabilísticos**, no solo 1X2 (RF-001, RF-003). El xG queda
  fuera del track record del MVP: no es una probabilidad y necesitaría su propia métrica.
- `avg_market_log_loss` solo existe para `1x2` — es el único mercado con cuota implícita
  disponible en las fuentes históricas (sección 6.2). En los otros dos es `null`, no cero.
- `market_baseline_matches` dice sobre cuántos partidos se calculó ese baseline, que puede ser
  menos que `matches_included` si alguno no tenía cuota. Antes esta cifra se omitía "para no
  sobrecargar la respuesta" y se remitía al endpoint de detalle, que tampoco la daba.
- `model_versions` con más de un elemento significa que la ventana abarca un reentrenamiento y
  la serie no es continua. El panel debe decirlo en vez de presentarla como una sola.
- `matches_included` puede ser menor que `window_size` mientras no haya 50 partidos jugados
  (RF-009).

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
      "real_result": { "home_goals": 2, "away_goals": 1 },
      "predicted_1x2": { "home": 0.48, "draw": 0.27, "away": 0.25 },
      "predicted_over_under_2_5": { "over": 0.58, "under": 0.42 },
      "predicted_btts": { "yes": 0.55, "no": 0.45 },
      "hit_1x2": true,
      "hit_over_under_2_5": true,
      "hit_btts": true,
      "has_market_odds": true,
      "market_implied_1x2": { "home": 0.52, "draw": 0.26, "away": 0.22 },
      "model_version": "xgb-ensemble-2026.08.1"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 50
}
```

Notas del contrato:

- Cada fila muestra la predicción original de los tres mercados junto al resultado real, que es
  lo que RF-003 promete poder auditar partido a partido.
- `market_implied_1x2` son **probabilidades implícitas agregadas del baseline**, no cuotas por
  casa de apuestas: el modelo de datos ni siquiera guarda la cuota cruda. Es lo que hace
  verificable la comparación de RF-004 sin abrir la puerta a un comparador de casas, que sigue
  fuera de alcance (RF-005 y sección 2.4 de `docs/project_spec.md`).
- `has_market_odds: false` implica `market_implied_1x2: null`; el partido cuenta igual para el
  acierto y el Brier del modelo (caso límite resuelto).
- `model_version` por fila es lo que permite auditar una ventana que abarca un reentrenamiento
  sin mezclar versiones.
