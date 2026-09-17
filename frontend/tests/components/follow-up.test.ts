import { describe, expect, it } from "vitest";
import type { FollowUpResponse } from "@/lib/api/types";

function getFollowUpContent(response: FollowUpResponse) {
  return {
    question: response.question,
    answer: response.answer,
    evidence: response.evidence.map((item) => ({
      title: item.title,
      url: item.url,
    })),
  };
}

describe("T021 - pregunta de seguimiento", () => {
  const response: FollowUpResponse = {
    match_id: "match-001",
    question: "¿Por qué el modelo favorece al equipo local?",
    answer:
      "El modelo favorece al equipo local debido a su rendimiento reciente.",
    evidence: [
      {
        id: "evidence-002",
        title: "Rendimiento reciente",
        url: "https://example.com/rendimiento",
        source: "Example",
        published_at: "2026-08-29T06:00:00Z",
      },
    ],
    generated_at: "2026-08-29T06:00:00Z",
  };

  it("mantiene la pregunta y muestra la respuesta", () => {
    const content = getFollowUpContent(response);

    expect(content.question).toBe(
      "¿Por qué el modelo favorece al equipo local?",
    );
    expect(content.answer).toBe(
      "El modelo favorece al equipo local debido a su rendimiento reciente.",
    );
  });

  it("muestra la evidencia asociada a la respuesta", () => {
    const content = getFollowUpContent(response);

    expect(content.evidence).toEqual([
      {
        title: "Rendimiento reciente",
        url: "https://example.com/rendimiento",
      },
    ]);
  });
});
