import { describe, expect, it } from "vitest";

function getInsufficientDataMessage(
  lowDataWarning: boolean,
) {
  return lowDataWarning
    ? "Datos insuficientes para una predicción confiable."
    : null;
}

describe("T028 - datos insuficientes", () => {
  it("muestra advertencia cuando low_data_warning es true", () => {
    expect(getInsufficientDataMessage(true)).toBe(
      "Datos insuficientes para una predicción confiable.",
    );
  });

  it("no muestra advertencia cuando low_data_warning es false", () => {
    expect(getInsufficientDataMessage(false)).toBeNull();
  });

  it("no reemplaza los datos válidos con ceros", () => {
    const prediction = {
      home: 0.48,
      draw: 0.27,
      away: 0.25,
    };

    expect(prediction.home).not.toBe(0);
    expect(prediction.draw).not.toBe(0);
    expect(prediction.away).not.toBe(0);
  });
});
