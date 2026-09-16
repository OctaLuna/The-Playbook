import { describe, expect, it } from "vitest";

interface ContrastCheck {
  foreground: string;
  background: string;
  ratio: number;
}

function meetsWcagAA(check: ContrastCheck) {
  return check.ratio >= 4.5;
}

describe("T031 - contraste WCAG AA", () => {
  it("requiere al menos 4.5:1 para texto normal", () => {
    expect(
      meetsWcagAA({
        foreground: "foreground",
        background: "background",
        ratio: 4.5,
      }),
    ).toBe(true);
  });

  it("rechaza contraste insuficiente para texto normal", () => {
    expect(
      meetsWcagAA({
        foreground: "muted-foreground",
        background: "background",
        ratio: 3.2,
      }),
    ).toBe(false);
  });

  it("acepta contraste superior al mínimo WCAG AA", () => {
    expect(
      meetsWcagAA({
        foreground: "foreground",
        background: "background",
        ratio: 7,
      }),
    ).toBe(true);
  });
});
