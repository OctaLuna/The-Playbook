import { describe, expect, it } from "vitest";

function getPredictionLabel(hasPrediction: boolean) {
  return hasPrediction ? null : "Predicción no disponible todavía.";
}

describe("T016 - indicador de partidos sin predicción", () => {
  it("muestra un indicador cuando el partido no tiene predicción", () => {
    expect(getPredictionLabel(false)).toBe(
      "Predicción no disponible todavía.",
    );
  });

  it("no muestra el indicador cuando el partido sí tiene predicción", () => {
    expect(getPredictionLabel(true)).toBeNull();
  });
});
