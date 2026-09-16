import { describe, expect, it } from "vitest";
import type { TrackRecordMatch } from "@/lib/api/types";

describe("T026 - detalle partido por partido del track record", () => {
  const match: TrackRecordMatch = {
    match_id: "match-001",
    league: "premier_league",
    home_team: "Arsenal",
    away_team: "Chelsea",
    kickoff_at: "2026-08-30T14:00:00Z",
    real_result: {
      home_goals: 2,
      away_goals: 1,
    },
    predicted_1x2: {
      home: 0.48,
      draw: 0.27,
      away: 0.25,
    },
    predicted_over_under_2_5: {
      over: 0.58,
      under: 0.42,
    },
    predicted_btts: {
      yes: 0.55,
      no: 0.45,
    },
    hit_1x2: true,
    hit_over_under_2_5: false,
    hit_btts: true,
    has_market_odds: false,
    market_implied_1x2: null,
    model_version: "xgb-ensemble-2026.08.1",
  };

  it("incluye los datos del partido y resultado real", () => {
    expect(match.home_team).toBe("Arsenal");
    expect(match.away_team).toBe("Chelsea");
    expect(match.real_result).toEqual({
      home_goals: 2,
      away_goals: 1,
    });
  });

  it("incluye las tres predicciones y sus resultados", () => {
    expect(match.predicted_1x2).toBeDefined();
    expect(match.predicted_over_under_2_5).toBeDefined();
    expect(match.predicted_btts).toBeDefined();

    expect(match.hit_1x2).toBe(true);
    expect(match.hit_over_under_2_5).toBe(false);
    expect(match.hit_btts).toBe(true);
  });
});
