export interface League {
  id: string;
  name: string;
}

export interface LeaguesResponse {
  leagues: League[];
}

export interface UpcomingMatch {
  id: string;
  league: string;
  home_team: string;
  away_team: string;
  kickoff_at: string;
  status: string;
  has_prediction: boolean;
}

export interface UpcomingMatchesResponse {
  matches: UpcomingMatch[];
  page: number;
  page_size: number;
  total: number;
}

export interface MatchRealResult {
  home_score: number;
  away_score: number;
}

export interface MatchDetail {
  id: string;
  league: string;
  home_team: string;
  away_team: string;
  kickoff_at: string;
  status: string;
  real_result: MatchRealResult | null;
}

export interface PredictionProbabilities1X2 {
  home: number;
  draw: number;
  away: number;
}

export interface OverUnder25 {
  over: number;
  under: number;
}

export interface BttsProbabilities {
  yes: number;
  no: number;
}

export interface ExpectedGoals {
  home: number;
  away: number;
}

export interface PredictionResponse {
  match_id: string;
  probabilities_1x2: PredictionProbabilities1X2;
  over_under_2_5: OverUnder25;
  btts: BttsProbabilities;
  xg: ExpectedGoals;
  confidence: string;
  head_to_head_available: boolean;
  low_data_warning: boolean;
  model_version: string;
  generated_at: string;
}

export interface Evidence {
  id: string;
  title: string;
  url: string;
  source: string;
  published_at: string;
}

export interface ExplanationResponse {
  match_id: string;
  text: string;
  is_fallback_no_evidence: boolean;
  evidence: Evidence[];
  generated_at: string;
  updated_at: string;
}

export interface FollowUpRequest {
  question: string;
}

export interface FollowUpResponse {
  match_id: string;
  question: string;
  answer: string;
  evidence: Evidence[];
  generated_at: string;
}

export interface TrackRecordMarket {
  market: string;
  hit_rate: number;
  avg_brier_score: number;
  avg_log_loss: number;
  avg_market_log_loss: number | null;
  market_baseline_matches: number;
}

export interface TrackRecordResponse {
  league: string;
  window_size: number;
  matches_included: number;
  model_versions: string[];
  markets: TrackRecordMarket[];
  last_updated_at: string;
}

export interface TrackRecordMatchResult {
  home_goals: number;
  away_goals: number;
}

export interface TrackRecordMatch {
  match_id: string;
  league: string;
  home_team: string;
  away_team: string;
  kickoff_at: string;
  real_result: TrackRecordMatchResult;
  predicted_1x2: PredictionProbabilities1X2;
  predicted_over_under_2_5: OverUnder25;
  predicted_btts: BttsProbabilities;
  hit_1x2: boolean;
  hit_over_under_2_5: boolean;
  hit_btts: boolean;
  has_market_odds: boolean;
  market_implied_1x2: PredictionProbabilities1X2 | null;
  model_version: string;
}

export interface TrackRecordMatchesResponse {
  matches: TrackRecordMatch[];
  page: number;
  page_size: number;
  total: number;
}