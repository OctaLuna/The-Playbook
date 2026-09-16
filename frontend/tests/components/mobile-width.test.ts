import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";

describe("Responsive width at 360px", () => {
  it("does not define fixed widths larger than a 360px viewport", () => {
    const files = [
      "app/page.tsx",
      "app/partidos/[id]/page.tsx",
      "app/track-record/page.tsx",
      "components/estado/Cargando.tsx",
      "components/estado/Error.tsx",
      "components/estado/Vacio.tsx",
    ];

    for (const file of files) {
      const content = readFileSync(file, "utf8");

      expect(content).not.toMatch(/(?:w|min-w|max-w)-\[(?:3[7-9]\d|[4-9]\d{2,})px\]/);
    }
  });

  it("uses responsive grid columns instead of fixed multi-column layouts", () => {
    const files = [
      "app/page.tsx",
      "app/partidos/[id]/page.tsx",
      "app/track-record/page.tsx",
    ];

    for (const file of files) {
      const content = readFileSync(file, "utf8");

      expect(content).not.toMatch(/grid-cols-[2-9](?!\s|")/);
    }
  });

  it("does not use horizontal overflow on the main application layout", () => {
    const globals = readFileSync("app/globals.css", "utf8");

    expect(globals).not.toMatch(/min-width\s*:\s*(?:3[7-9]\d|[4-9]\d{2,})px/);
  });
});
