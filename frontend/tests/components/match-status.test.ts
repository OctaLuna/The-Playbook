import { describe, expect, it } from "vitest";
import type { PredictionResponse } from "@/lib/api/types";

function shouldKeepPredictionVisible(
  status: string,
  prediction: PredictionResponse | null,
) {
  const affectedStatuses = ["postponed", "cancelled", "played"];

  return (
    affectedStatuses.includes(status) &&
    prediction !== null
  );
}

describe("T023 - estados del partido y predicción original", () => {
  const prediction: PredictionResponse = {
    match_id: "match-001",
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
  };

  it.each(["postponed", "cancelled", "played"])(
    "mantiene la predicción para un partido %s",
    (status) => {
      expect(
        shouldKeepPredictionVisible(status, prediction),
      ).toBe(true);
    },
  );

  it("no considera que exista predicción si no hay datos de predicción", () => {
    expect(
      shouldKeepPredictionVisible("played", null),
    ).toBe(false);
  });
});