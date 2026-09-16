import { describe, expect, it } from "vitest";

interface LiveRegion {
  ariaLive: "polite" | "assertive" | "off";
  role?: string;
  message: string;
}

function isValidLiveRegion(region: LiveRegion) {
  return (
    region.ariaLive !== "off" &&
    region.message.trim().length > 0
  );
}

describe("T030 - regiones en vivo", () => {
  it("usa aria-live para comunicar cambios de carga o estado", () => {
    expect(
      isValidLiveRegion({
        ariaLive: "polite",
        message: "Cargando partidos...",
      }),
    ).toBe(true);
  });

  it("permite una región asertiva para errores importantes", () => {
    expect(
      isValidLiveRegion({
        ariaLive: "assertive",
        role: "alert",
        message: "No se pudo cargar el partido.",
      }),
    ).toBe(true);
  });

  it("rechaza regiones sin mensaje", () => {
    expect(
      isValidLiveRegion({
        ariaLive: "polite",
        message: "",
      }),
    ).toBe(false);
  });
});
