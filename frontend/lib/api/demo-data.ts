import type {
  ExplanationResponse,
  MatchDetail,
  PredictionResponse,
  TrackRecordMatchesResponse,
  TrackRecordResponse,
  UpcomingMatchesResponse,
} from "./types";

export const demoUpcomingMatches: UpcomingMatchesResponse = {
  matches: [
    {
      id: "arsenal-man-city",
      league: "Premier League",
      home_team: "Arsenal",
      away_team: "Manchester City",
      kickoff_at: "2026-09-16T19:30:00Z",
      status: "scheduled",
      has_prediction: true,
    },
    {
      id: "liverpool-chelsea",
      league: "Premier League",
      home_team: "Liverpool",
      away_team: "Chelsea",
      kickoff_at: "2026-09-17T17:00:00Z",
      status: "scheduled",
      has_prediction: true,
    },
    {
      id: "real-madrid-barcelona",
      league: "La Liga",
      home_team: "Real Madrid",
      away_team: "Barcelona",
      kickoff_at: "2026-09-18T20:00:00Z",
      status: "scheduled",
      has_prediction: false,
    },
    {
      id: "inter-milan-juventus",
      league: "Serie A",
      home_team: "Inter",
      away_team: "Juventus",
      kickoff_at: "2026-09-19T18:45:00Z",
      status: "scheduled",
      has_prediction: true,
    },
  ],
  page: 1,
  page_size: 20,
  total: 4,
};

export const demoMatches: Record<string, MatchDetail> = {
  "arsenal-man-city": {
    id: "arsenal-man-city",
    league: "Premier League",
    home_team: "Arsenal",
    away_team: "Manchester City",
    kickoff_at: "2026-09-16T19:30:00Z",
    status: "scheduled",
    real_result: null,
  },
  "liverpool-chelsea": {
    id: "liverpool-chelsea",
    league: "Premier League",
    home_team: "Liverpool",
    away_team: "Chelsea",
    kickoff_at: "2026-09-17T17:00:00Z",
    status: "scheduled",
    real_result: null,
  },
};

export const demoPredictions: Record<string, PredictionResponse> = {
  "arsenal-man-city": {
    match_id: "arsenal-man-city",
    probabilities_1x2: {
      home: 0.46,
      draw: 0.27,
      away: 0.27,
    },
    over_under_2_5: {
      over: 0.61,
      under: 0.39,
    },
    btts: {
      yes: 0.58,
      no: 0.42,
    },
    xg: {
      home: 1.72,
      away: 1.34,
    },
    confidence: "Alta",
    head_to_head_available: true,
    low_data_warning: false,
    model_version: "v1.0.0",
    generated_at: "2026-09-15T18:00:00Z",
  },
  "liverpool-chelsea": {
    match_id: "liverpool-chelsea",
    probabilities_1x2: {
      home: 0.52,
      draw: 0.25,
      away: 0.23,
    },
    over_under_2_5: {
      over: 0.57,
      under: 0.43,
    },
    btts: {
      yes: 0.55,
      no: 0.45,
    },
    xg: {
      home: 1.81,
      away: 1.18,
    },
    confidence: "Media",
    head_to_head_available: true,
    low_data_warning: true,
    model_version: "v1.0.0",
    generated_at: "2026-09-15T18:05:00Z",
  },
};

export const demoExplanations: Record<string, ExplanationResponse> = {
  "arsenal-man-city": {
    match_id: "arsenal-man-city",
    text: "El modelo da una ligera ventaja al equipo local. La señal combina el rendimiento reciente, la producción ofensiva esperada y la disponibilidad de datos históricos relevantes para este enfrentamiento.",
    is_fallback_no_evidence: false,
    evidence: [
      {
        id: "evidence-1",
        title: "Análisis previo al partido",
        url: "https://example.com/evidence-1",
        source: "Demo",
        published_at: "2026-09-15T10:00:00Z",
      },
      {
        id: "evidence-2",
        title: "Contexto de rendimiento reciente",
        url: "https://example.com/evidence-2",
        source: "Demo",
        published_at: "2026-09-15T12:00:00Z",
      },
    ],
    generated_at: "2026-09-15T18:01:00Z",
    updated_at: "2026-09-15T18:01:00Z",
  },
};

export const demoTrackRecord: TrackRecordResponse = {
  league: "Premier League",
  window_size: 50,
  matches_included: 50,
  model_versions: ["v1.0.0"],
  markets: [
    {
      market: "1x2",
      hit_rate: 0.64,
      avg_brier_score: 0.218,
      avg_log_loss: 0.624,
      avg_market_log_loss: 0.671,
      market_baseline_matches: 50,
    },
    {
      market: "over_under_2_5",
      hit_rate: 0.58,
      avg_brier_score: 0.239,
      avg_log_loss: 0.658,
      avg_market_log_loss: 0.692,
      market_baseline_matches: 50,
    },
    {
      market: "btts",
      hit_rate: 0.61,
      avg_brier_score: 0.226,
      avg_log_loss: 0.641,
      avg_market_log_loss: 0.676,
      market_baseline_matches: 50,
    },
  ],
  last_updated_at: "2026-09-15T18:30:00Z",
};

export const demoTrackRecordMatches: TrackRecordMatchesResponse = {
  matches: [
    {
      match_id: "demo-1",
      league: "Premier League",
      home_team: "Arsenal",
      away_team: "Chelsea",
      kickoff_at: "2026-08-30T15:00:00Z",
      real_result: {
        home_goals: 2,
        away_goals: 1,
      },
      predicted_1x2: {
        home: 0.57,
        draw: 0.24,
        away: 0.19,
      },
      predicted_over_under_2_5: {
        over: 0.63,
        under: 0.37,
      },
      predicted_btts: {
        yes: 0.59,
        no: 0.41,
      },
      hit_1x2: true,
      hit_over_under_2_5: true,
      hit_btts: true,
      has_market_odds: true,
      market_implied_1x2: {
        home: 0.51,
        draw: 0.27,
        away: 0.22,
      },
      model_version: "v1.0.0",
    },
    {
      match_id: "demo-2",
      league: "Premier League",
      home_team: "Liverpool",
      away_team: "Tottenham",
      kickoff_at: "2026-08-23T15:00:00Z",
      real_result: {
        home_goals: 1,
        away_goals: 1,
      },
      predicted_1x2: {
        home: 0.49,
        draw: 0.31,
        away: 0.2,
      },
      predicted_over_under_2_5: {
        over: 0.54,
        under: 0.46,
      },
      predicted_btts: {
        yes: 0.62,
        no: 0.38,
      },
      hit_1x2: true,
      hit_over_under_2_5: false,
      hit_btts: true,
      has_market_odds: true,
      market_implied_1x2: {
        home: 0.55,
        draw: 0.25,
        away: 0.2,
      },
      model_version: "v1.0.0",
    },
  ],
  page: 1,
  page_size: 20,
  total: 2,
};