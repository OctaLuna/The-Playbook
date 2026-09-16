import { describe, expect, it } from "vitest";
import type { TrackRecordResponse } from "@/lib/api/types";

describe("T024 - track record separado por 3 mercados", () => {
  const trackRecord: TrackRecordResponse = {
    league: "premier_league",
    window_size: 50,
    matches_included: 50,
    model_versions: ["xgb-ensemble-2026.08.1"],
    markets: [
      {
        market: "1x2",
        hit_rate: 0.62,
        avg_brier_score: 0.21,
        avg_log_loss: 0.68,
        avg_market_log_loss: 0.71,
        market_baseline_matches: 50,
      },
      {
        market: "over_under_2_5",
        hit_rate: 0.58,
        avg_brier_score: 0.23,
        avg_log_loss: 0.69,
        avg_market_log_loss: 0.72,
        market_baseline_matches: 50,
      },
      {
        market: "btts",
        hit_rate: 0.64,
        avg_brier_score: 0.20,
        avg_log_loss: 0.65,
        avg_market_log_loss: 0.68,
        market_baseline_matches: 50,
      },
    ],
    last_updated_at: "2026-08-30T06:00:00Z",
  };

  it("incluye exactamente los tres mercados", () => {
    expect(trackRecord.markets).toHaveLength(3);
  });

  it("mantiene cada mercado separado", () => {
    expect(trackRecord.markets.map((market) => market.market)).toEqual([
      "1x2",
      "over_under_2_5",
      "btts",
    ]);
  });

  it("conserva las métricas independientes de cada mercado", () => {
    expect(trackRecord.markets[0].hit_rate).toBe(0.62);
    expect(trackRecord.markets[1].hit_rate).toBe(0.58);
    expect(trackRecord.markets[2].hit_rate).toBe(0.64);
  });
});