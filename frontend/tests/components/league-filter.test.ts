import { describe, expect, it } from "vitest";

function buildLeagueUrl(league: string) {
  const params = new URLSearchParams();

  if (league) {
    params.set("league", league);
  }

  const query = params.toString();
  return query ? `/?${query}` : "/";
}

describe("T015 - filtro de liga en URL", () => {
  it("refleja la liga seleccionada en el parámetro league", () => {
    expect(buildLeagueUrl("premier_league")).toBe(
      "/?league=premier_league",
    );
  });

  it("mantiene la URL sin parámetro cuando no hay filtro", () => {
    expect(buildLeagueUrl("")).toBe("/");
  });
});
