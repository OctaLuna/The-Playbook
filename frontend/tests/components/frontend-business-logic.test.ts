import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";

const frontendFiles = [
  "app/page.tsx",
  "app/partidos/[id]/page.tsx",
  "app/track-record/page.tsx",
  "components/estado/Cargando.tsx",
  "components/estado/Error.tsx",
  "components/estado/Vacio.tsx",
  "lib/api/client.ts",
  "lib/api/hooks.ts",
  "lib/api/types.ts",
];

function readFrontendSource() {
  return frontendFiles
    .map((file) => readFileSync(file, "utf8"))
    .join("\n");
}

describe("Frontend sin lógica de negocio ni cuotas", () => {
  it("no contiene campos ni referencias a cuotas de bookmakers", () => {
    const source = readFrontendSource();

    expect(source).not.toMatch(
      /bookmaker|bookmaker_odds|decimal_odds|bookmakerOdds|cuota/i,
    );
  });

  it("no calcula métricas de rendimiento en el frontend", () => {
    const source = readFrontendSource();

    expect(source).not.toMatch(
      /reduce\s*\(|average|brier_score\s*=|log_loss\s*=/i,
    );
  });

  it("usa las métricas calculadas por backend directamente", () => {
    const source = readFileSync("app/track-record/page.tsx", "utf8");

    expect(source).toContain("market.hit_rate");
    expect(source).toContain("market.avg_brier_score");
    expect(source).toContain("market.avg_log_loss");
  });
});
