import { describe, expect, it } from "vitest";
import type { ExplanationResponse } from "@/lib/api/types";

function getExplanationContent(explanation: ExplanationResponse) {
  return {
    text: explanation.text,
    evidence: explanation.evidence.map((item) => ({
      title: item.title,
      url: item.url,
    })),
  };
}

describe("T020 - explicación y evidencia", () => {
  const explanation: ExplanationResponse = {
    match_id: "match-001",
    text: "El modelo favorece al equipo local por su rendimiento reciente.",
    is_fallback_no_evidence: false,
    evidence: [
      {
        id: "evidence-001",
        title: "Rendimiento reciente del equipo local",
        url: "https://example.com/evidence",
        source: "Example",
        published_at: "2026-08-29T06:00:00Z",
      },
    ],
    generated_at: "2026-08-29T06:00:00Z",
    updated_at: "2026-08-29T06:00:00Z",
  };

  it("muestra el texto de explicación", () => {
    const content = getExplanationContent(explanation);

    expect(content.text).toBe(
      "El modelo favorece al equipo local por su rendimiento reciente.",
    );
  });

  it("incluye título y URL para cada evidencia", () => {
    const content = getExplanationContent(explanation);

    expect(content.evidence).toEqual([
      {
        title: "Rendimiento reciente del equipo local",
        url: "https://example.com/evidence",
      },
    ]);
  });
});
