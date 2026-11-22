import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

function luminance(hex: string) {
  const channels = hex.match(/[a-f\d]{2}/gi)?.map((channel) => parseInt(channel, 16) / 255);
  if (!channels || channels.length !== 3) throw new Error(`Color inválido: ${hex}`);
  const linear = channels.map((channel) => channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrastRatio(foreground: string, background: string) {
  const lighter = Math.max(luminance(foreground), luminance(background));
  const darker = Math.min(luminance(foreground), luminance(background));
  return (lighter + 0.05) / (darker + 0.05);
}

describe("T031 - contraste de la paleta en vistas oscuras", () => {
  it("mantiene contraste AA para el texto secundario real de las vistas", () => {
    const files = [
      "app/page.tsx",
      "app/partidos/[id]/page.tsx",
      "app/track-record/page.tsx",
      "components/estado/Error.tsx",
      "components/estado/Vacio.tsx",
    ];
    const source = files.map((file) => readFileSync(file, "utf8")).join("\n");
    const styles = readFileSync("app/globals.css", "utf8");

    expect(styles).toContain("--muted-foreground: #aeb6b0");
    expect(source).toContain("text-[#aeb6b0]");

    expect(source).not.toMatch(/text-\[#(?:77827c|69766f|68736d|81918a|8e9b95|565f5b)\]/i);
    expect(contrastRatio("#8f9a94", "#101c18")).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio("#8f9a94", "#182922")).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio("#aeb6b0", "#17352b")).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio("#aeb6b0", "#0f1310")).toBeGreaterThanOrEqual(4.5);
  });
});