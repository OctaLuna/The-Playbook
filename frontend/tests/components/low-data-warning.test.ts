import { describe, expect, it } from "vitest";
import type { PredictionResponse } from "@/lib/api/types";

function getLowDataWarning(prediction: PredictionResponse) {
  return prediction.low_data_warning
    ? "Datos insuficientes para una predicción confiable."
    : null;
}

describe("T019 - advertencia de datos insuficientes", () => {
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
    low_data_warning: true,
    model_version: "xgb-ensemble-2026.08.1",
    generated_at: "2026-08-29T06:00:00Z",
  };

  it("muestra advertencia cuando low_data_warning es true", () => {
    expect(getLowDataWarning(prediction)).toBe(
      "Datos insuficientes para una predicción confiable.",
    );
  });

  it("no muestra advertencia cuando low_data_warning es false", () => {
    expect(
      getLowDataWarning({
        ...prediction,
        low_data_warning: false,
      }),
    ).toBeNull();
  });
});
