import { describe, expect, it } from "vitest";

function getModelVersionWarning(modelVersions: string[]) {
  return modelVersions.length > 1
    ? "El historial incluye múltiples versiones del modelo."
    : null;
}

describe("T027 - múltiples versiones del modelo", () => {
  it("muestra advertencia cuando hay múltiples model_versions", () => {
    expect(
      getModelVersionWarning([
        "xgb-ensemble-2026.08.1",
        "xgb-ensemble-2026.08.2",
      ]),
    ).toBe(
      "El historial incluye múltiples versiones del modelo.",
    );
  });

  it("no muestra advertencia con una sola versión", () => {
    expect(
      getModelVersionWarning(["xgb-ensemble-2026.08.1"]),
    ).toBeNull();
  });

  it("no muestra advertencia si no hay versiones", () => {
    expect(getModelVersionWarning([])).toBeNull();
  });
});
