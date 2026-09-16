import { describe, expect, it } from "vitest";
import type { PredictionResponse } from "@/lib/api/types";

function getPredictionSignals(prediction: PredictionResponse) {
  return {
    oneXtwo: prediction.probabilities_1x2,
    overUnder25: prediction.over_under_2_5,
    btts: prediction.btts,
    xg: prediction.xg,
    confidence: prediction.confidence,
  };
}

describe("T017 - detalle del partido", () => {
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

  it("incluye las cuatro señales de predicción", () => {
    const signals = getPredictionSignals(prediction);

    expect(signals.oneXtwo).toEqual(prediction.probabilities_1x2);
    expect(signals.overUnder25).toEqual(prediction.over_under_2_5);
    expect(signals.btts).toEqual(prediction.btts);
    expect(signals.xg).toEqual(prediction.xg);
  });

  it("incluye el nivel de confianza", () => {
    const signals = getPredictionSignals(prediction);

    expect(signals.confidence).toBe("media");
  });
});
