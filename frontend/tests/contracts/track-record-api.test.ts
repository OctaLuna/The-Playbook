import { describe, expect, it } from "vitest";
import type {
  TrackRecordMatchesResponse,
  TrackRecordResponse,
} from "@/lib/api/types";

describe("track record API contracts", () => {
  it("parses the track record summary with the three markets", () => {
    const response = {
      league: "premier_league",
      window_size: 50,
      matches_included: 50,
      model_versions: ["xgb-ensemble-2026.08.1"],
      markets: [
        {
          market: "1x2",
          hit_rate: 0.54,
          avg_brier_score: 0.19,
          avg_log_loss: 0.61,
          avg_market_log_loss: 0.58,
          market_baseline_matches: 47,
        },
        {
          market: "over_under_2_5",
          hit_rate: 0.61,
          avg_brier_score: 0.22,
          avg_log_loss: 0.65,
          avg_market_log_loss: null,
          market_baseline_matches: 0,
        },
        {
          market: "btts",
          hit_rate: 0.58,
          avg_brier_score: 0.23,
          avg_log_loss: 0.67,
          avg_market_log_loss: null,
          market_baseline_matches: 0,
        },
      ],
      last_updated_at: "2026-08-24T03:00:00Z",
    } satisfies TrackRecordResponse;

    expect(response.markets).toHaveLength(3);
    expect(response.markets.map((market) => market.market)).toEqual([
      "1x2",
      "over_under_2_5",
      "btts",
    ]);
  });

  it("parses the track record match detail", () => {
    const response = {
      matches: [
        {
          match_id: "uuid",
          league: "premier_league",
          home_team: "Arsenal",
          away_team: "Chelsea",
          kickoff_at: "2026-08-16T14:00:00Z",
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
          hit_over_under_2_5: true,
          hit_btts: true,
          has_market_odds: true,
          market_implied_1x2: {
            home: 0.52,
            draw: 0.26,
            away: 0.22,
          },
          model_version: "xgb-ensemble-2026.08.1",
        },
      ],
      page: 1,
      page_size: 20,
      total: 50,
    } satisfies TrackRecordMatchesResponse;

    expect(response.matches).toHaveLength(1);
    expect(response.matches[0].predicted_1x2.home).toBe(0.48);
    expect(response.matches[0].predicted_over_under_2_5.over).toBe(0.58);
    expect(response.matches[0].predicted_btts.yes).toBe(0.55);
  });
});