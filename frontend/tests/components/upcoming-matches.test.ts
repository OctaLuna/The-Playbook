import { describe, expect, it } from "vitest";
import type { UpcomingMatch } from "@/lib/api/types";

function orderUpcomingMatches(matches: UpcomingMatch[]) {
  return [...matches].sort(
    (a, b) =>
      new Date(a.kickoff_at).getTime() -
      new Date(b.kickoff_at).getTime(),
  );
}

describe("T013 - vista de lista de partidos", () => {
  const matches: UpcomingMatch[] = [
    {
      id: "match-later",
      league: "premier_league",
      home_team: "Arsenal",
      away_team: "Chelsea",
      kickoff_at: "2026-08-30T18:00:00Z",
      status: "scheduled",
      has_prediction: true,
    },
    {
      id: "match-sooner",
      league: "premier_league",
      home_team: "Liverpool",
      away_team: "Manchester City",
      kickoff_at: "2026-08-30T14:00:00Z",
      status: "scheduled",
      has_prediction: false,
    },
  ];

  it("ordena los partidos por proximidad al kickoff", () => {
    const ordered = orderUpcomingMatches(matches);

    expect(ordered.map((match) => match.id)).toEqual([
      "match-sooner",
      "match-later",
    ]);
  });

  it("distingue los partidos que no tienen predicción", () => {
    const ordered = orderUpcomingMatches(matches);

    expect(ordered[0].has_prediction).toBe(false);
    expect(ordered[1].has_prediction).toBe(true);
  });
});
