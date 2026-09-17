import { describe, expect, it } from "vitest";
import type {
  LeaguesResponse,
  MatchDetail,
  PredictionResponse,
  UpcomingMatchesResponse,
} from "@/lib/api/types";

describe("matches API contracts", () => {
  it("parses the leagues example", () => {
    const response = {
      leagues: [
        { id: "premier_league", name: "Premier League" },
        { id: "laliga", name: "LaLiga" },
        { id: "serie_a", name: "Serie A" },
        { id: "bundesliga", name: "Bundesliga" },
        { id: "ligue_1", name: "Ligue 1" },
      ],
    } satisfies LeaguesResponse;

    expect(response.leagues).toHaveLength(5);
  });

  it("parses the upcoming matches example", () => {
    const response = {
      matches: [
        {
          id: "uuid",
          league: "premier_league",
          home_team: "Arsenal",
          away_team: "Chelsea",
          kickoff_at: "2026-08-30T14:00:00Z",
          status: "scheduled",
          has_prediction: true,
        },
      ],
      page: 1,
      page_size: 20,
      total: 42,
    } satisfies UpcomingMatchesResponse;

    expect(response.matches[0].has_prediction).toBe(true);
  });

  it("parses the match detail example", () => {
    const response = {
      id: "uuid",
      league: "premier_league",
      home_team: "Arsenal",
      away_team: "Chelsea",
      kickoff_at: "2026-08-30T14:00:00Z",
      status: "scheduled",
      real_result: null,
    } satisfies MatchDetail;

    expect(response.real_result).toBeNull();
  });

  it("parses the prediction example", () => {
    const response = {
      match_id: "uuid",
      probabilities_1x2: {
        home: 0.48,
        draw: 0.27,
        away: 0.25,
      },
      over_under_2_5: {
        over: 0.58,
        under: 0.42,
      },
      btts: {
        yes: 0.55,
        no: 0.45,
      },
      xg: {
        home: 1.62,
        away: 1.11,
      },
      confidence: "media",
      head_to_head_available: false,
      low_data_warning: false,
      model_version: "xgb-ensemble-2026.08.1",
      generated_at: "2026-08-29T06:00:00Z",
    } satisfies PredictionResponse;

    expect(response.xg.home).toBe(1.62);
    expect(response.confidence).toBe("media");
  });
});