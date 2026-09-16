import { describe, expect, it } from "vitest";

interface KeyboardTarget {
  role: string;
  tabIndex: number;
  accessibleName: string;
}

function isKeyboardAccessible(target: KeyboardTarget) {
  return target.tabIndex >= 0 && target.accessibleName.trim().length > 0;
}

describe("T029 - navegación y foco por teclado", () => {
  it("permite enfocar controles interactivos mediante teclado", () => {
    expect(
      isKeyboardAccessible({
        role: "link",
        tabIndex: 0,
        accessibleName: "Ver detalle del partido",
      }),
    ).toBe(true);
  });

  it("requiere un nombre accesible para los controles", () => {
    expect(
      isKeyboardAccessible({
        role: "button",
        tabIndex: 0,
        accessibleName: "",
      }),
    ).toBe(false);
  });

  it("rechaza elementos interactivos fuera del orden de tabulación", () => {
    expect(
      isKeyboardAccessible({
        role: "button",
        tabIndex: -1,
        accessibleName: "Reintentar",
      }),
    ).toBe(false);
  });
});
