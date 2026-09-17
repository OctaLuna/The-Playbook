import { describe, expect, it } from "vitest";
import type {
  ExplanationResponse,
  FollowUpRequest,
  FollowUpResponse,
} from "@/lib/api/types";

describe("explanations API contracts", () => {
  it("parses the explanation example with verifiable evidence", () => {
    const response = {
      match_id: "uuid",
      text: "El modelo favorece al local principalmente por su forma reciente.",
      is_fallback_no_evidence: false,
      evidence: [
        {
          id: "uuid",
          title: "El delantero del Chelsea, baja por lesión ante el Arsenal",
          url: "https://ejemplo.com/noticia",
          source: "News API",
          published_at: "2026-08-27T10:00:00Z",
        },
      ],
      generated_at: "2026-08-29T06:05:00Z",
      updated_at: "2026-08-29T06:05:00Z",
    } satisfies ExplanationResponse;

    expect(response.evidence).toHaveLength(1);
    expect(response.evidence[0].title).toBe(
      "El delantero del Chelsea, baja por lesión ante el Arsenal",
    );
    expect(response.evidence[0].url).toBe("https://ejemplo.com/noticia");
  });

  it("parses the follow-up request example", () => {
    const request = {
      question: "¿Por qué pesa tanto la lesión del delantero?",
    } satisfies FollowUpRequest;

    expect(request.question).toBeTruthy();
  });

  it("parses the follow-up response with evidence", () => {
    const response = {
      match_id: "uuid",
      question: "¿Por qué pesa tanto la lesión del delantero?",
      answer:
        "Porque el delantero concentra el 40% del xG del equipo en los últimos 5 partidos.",
      evidence: [
        {
          id: "uuid",
          title: "El delantero del Chelsea, baja por lesión ante el Arsenal",
          url: "https://ejemplo.com/noticia",
          source: "News API",
          published_at: "2026-08-27T10:00:00Z",
        },
      ],
      generated_at: "2026-08-29T10:12:00Z",
    } satisfies FollowUpResponse;

    expect(response.evidence[0].title).toBe(
      "El delantero del Chelsea, baja por lesión ante el Arsenal",
    );
    expect(response.evidence[0].url).toBe("https://ejemplo.com/noticia");
  });
});