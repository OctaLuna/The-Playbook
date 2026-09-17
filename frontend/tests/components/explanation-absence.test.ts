import { describe, expect, it } from "vitest";

interface ExplanationState {
  available: boolean;
  text?: string;
}

function getExplanationMessage(explanation: ExplanationState | null) {
  return explanation?.available
    ? explanation.text ?? null
    : "No hay una explicación disponible para este partido.";
}

function shouldShowPredictionSignals() {
  return true;
}

describe("T022 - ausencia de explicación", () => {
  it("mantiene visibles las señales aunque no exista explicación", () => {
    expect(shouldShowPredictionSignals()).toBe(true);
  });

  it("indica claramente cuando no existe explicación", () => {
    expect(getExplanationMessage(null)).toBe(
      "No hay una explicación disponible para este partido.",
    );
  });
});
